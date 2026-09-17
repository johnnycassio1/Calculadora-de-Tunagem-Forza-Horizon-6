import flet as ft
import os
import sqlite3
import csv
import io
import re

# ---------------------------------------------------------
# CAMINHO ABSOLUTO & BANCO DE DADOS
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "veiculos.db")
CSV_PATH = os.path.join(BASE_DIR, "veiculos.csv")

def conectar_banco():
    return sqlite3.connect(DB_NAME)

def ler_arquivo_csv_inteligente(caminho):
    if not os.path.exists(caminho):
        return []

    encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
    
    for enc in encodings:
        try:
            with open(caminho, mode="r", encoding=enc) as file:
                conteudo = file.read()
                if not conteudo.strip():
                    continue
                
                primeira_linha = conteudo.splitlines()[0]
                delimitador = ';' if ';' in primeira_linha else ','
                
                stream = io.StringIO(conteudo)
                reader = list(csv.reader(stream, delimiter=delimitador))
                
                if len(reader) > 1:
                    return reader[1:]
        except Exception:
            continue
    return []

def inicializar_banco():
    conn = conectar_banco()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS veiculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marca TEXT NOT NULL,
            modelo TEXT NOT NULL,
            classe TEXT,
            pi_original INTEGER,
            peso_fabrica TEXT,
            potencia TEXT,
            distribuicao_dianteira TEXT,
            tracao TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS garagem_setups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            modalidade TEXT,
            tracao TEXT,
            detalhes TEXT
        )
    """)
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM veiculos")
    total = cursor.fetchone()[0]
    
    if total < 50:
        cursor.execute("DELETE FROM veiculos")
        linhas = ler_arquivo_csv_inteligente(CSV_PATH)
        
        if linhas:
            for linha in linhas:
                if len(linha) >= 6:
                    marca = linha[0].strip()
                    modelo = linha[1].strip()
                    classe = linha[2].strip() if len(linha) > 2 else ""
                    peso = linha[3].strip() if len(linha) > 3 else "1350"
                    potencia = linha[4].strip() if len(linha) > 4 else "450"
                    distribuicao = linha[5].strip() if len(linha) > 5 else "50"
                    tracao = linha[6].strip() if len(linha) > 6 else "RWD"
                    
                    cursor.execute("""
                        INSERT INTO veiculos (marca, modelo, classe, pi_original, peso_fabrica, potencia, distribuicao_dianteira, tracao)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (marca, modelo, classe, 0, peso, potencia, distribuicao, tracao))
            conn.commit()
    conn.close()

inicializar_banco()

def buscar_veiculos_filtrados(termo=""):
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        termo_limpo = f"%{termo.strip().lower()}%"
        if termo.strip():
            cursor.execute(
                "SELECT id, marca, modelo FROM veiculos WHERE LOWER(marca) LIKE ? OR LOWER(modelo) LIKE ? ORDER BY marca, modelo",
                (termo_limpo, termo_limpo)
            )
        else:
            cursor.execute("SELECT id, marca, modelo FROM veiculos ORDER BY marca, modelo")
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception:
        return []

def carregar_garagem():
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute("SELECT nome, modalidade, tracao, detalhes FROM garagem_setups")
        rows = cursor.fetchall()
        conn.close()
        return [{"nome": r[0], "modalidade": r[1], "tracao": r[2], "detalhes": r[3]} for r in rows]
    except Exception:
        return []

def salvar_setup_banco(setup):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO garagem_setups (nome, modalidade, tracao, detalhes) VALUES (?, ?, ?, ?)",
                   (setup["nome"], setup["modalidade"], setup["tracao"], setup["detalhes"]))
    conn.commit()
    conn.close()

def deletar_setup_banco(index):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM garagem_setups")
    ids = cursor.fetchall()
    if index < len(ids):
        cursor.execute("DELETE FROM garagem_setups WHERE id = ?", (ids[index][0],))
        conn.commit()
    conn.close()

def main(page: ft.Page):
    page.title = "Calculadora de Tunagem Forza - Safira Spec"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    setups_salvos = carregar_garagem()
    ultimo_setup_calculado = {}

    # ---------------------------------------------------------
    # PAINEL 1: PESQUISA E SELEÇÃO DE VEÍCULO
    # ---------------------------------------------------------
    car_name = ft.TextField(label="Projeto / Nome do Carro", width=320, border_radius=8)
    weight_input = ft.TextField(label="Peso Final com Peças (kg)", value="1350", width=320, border_radius=8, keyboard_type=ft.KeyboardType.NUMBER)
    power_input = ft.TextField(label="Potência Final com Peças (CV/HP)", value="450", width=320, border_radius=8, keyboard_type=ft.KeyboardType.NUMBER)
    front_bias_input = ft.TextField(label="Distribuição Dianteira (%)", value="52.00", width=320, border_radius=8, keyboard_type=ft.KeyboardType.NUMBER)

    veiculos_db = buscar_veiculos_filtrados("")
    opcoes_veiculos = [ft.dropdown.Option(key=str(row[0]), text=f"{row[1]} - {row[2]}") for row in veiculos_db]

    veiculo_dropdown = ft.Dropdown(
        label=f"🚗 Carros Encontrados ({len(opcoes_veiculos)})",
        width=320,
        border_radius=8,
        options=opcoes_veiculos
    )

    search_input = ft.TextField(
        label="🔍 Pesquisar por Marca ou Modelo",
        hint_text="Ex: Skyline, Ferrari, Civic...",
        width=320,
        border_radius=8
    )

    def on_search_change(e):
        termo = search_input.value
        filtrados = buscar_veiculos_filtrados(termo)
        veiculo_dropdown.options = [ft.dropdown.Option(key=str(row[0]), text=f"{row[1]} - {row[2]}") for row in filtrados]
        veiculo_dropdown.label = f"🚗 Carros Encontrados ({len(filtrados)})"
        page.update()

    search_input.on_change = on_search_change

    def on_veiculo_change(e):
        v_id = veiculo_dropdown.value
        if v_id:
            conn = conectar_banco()
            cursor = conn.cursor()
            cursor.execute("SELECT marca, modelo, peso_fabrica, potencia, distribuicao_dianteira, tracao FROM veiculos WHERE id = ?", (v_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                marca, modelo, peso, potencia, distribuicao, tracao = row
                car_name.value = f"{marca} {modelo}"

                w_match = re.search(r'\d+', str(peso))
                p_match = re.search(r'\d+', str(potencia))
                d_match = re.search(r'\d+(\.\d+)?', str(distribuicao))

                if w_match: weight_input.value = w_match.group(0)
                if p_match: power_input.value = p_match.group(0)
                if d_match: front_bias_input.value = d_match.group(0)

                if tracao:
                    tr_upper = str(tracao).upper()
                    if "TRASEIRA" in tr_upper or "RWD" in tr_upper:
                        drivetrain_dd.value = "RWD (Traseira)"
                    elif "DIANTEIRA" in tr_upper or "FWD" in tr_upper:
                        drivetrain_dd.value = "FWD (Dianteira)"
                    elif "INTEGRAL" in tr_upper or "AWD" in tr_upper:
                        drivetrain_dd.value = "AWD (Integral)"

                page.update()

    veiculo_dropdown.on_change = on_veiculo_change

    # ---------------------------------------------------------
    # PAINEL 2: CONFIGURAÇÃO DO KIT DE TUNAGEM & MARCHAS
    # ---------------------------------------------------------
    modality_dd = ft.Dropdown(
        label="Modalidade de Corrida",
        value="Pista / Asfalto (Grip)",
        width=320,
        border_radius=8,
        options=[
            ft.dropdown.Option("Pista / Asfalto (Grip)"),
            ft.dropdown.Option("Drift"),
            ft.dropdown.Option("Rally / Off-road"),
            ft.dropdown.Option("Arrancada (Drag)")
        ]
    )

    drivetrain_dd = ft.Dropdown(
        label="Tração Atual/Convertida",
        value="RWD (Traseira)",
        width=320,
        border_radius=8,
        options=[
            ft.dropdown.Option("RWD (Traseira)"),
            ft.dropdown.Option("FWD (Dianteira)"),
            ft.dropdown.Option("AWD (Integral)")
        ]
    )

    transmission_dd = ft.Dropdown(
        label="Transmissão Instalada",
        value="Corrida (6V)",
        width=320,
        border_radius=8,
        options=[
            ft.dropdown.Option("Original"),
            ft.dropdown.Option("Rua"),
            ft.dropdown.Option("Esporte"),
            ft.dropdown.Option("Corrida (6V)"),
            ft.dropdown.Option("Corrida (7V)"),
            ft.dropdown.Option("Corrida (8V)"),
            ft.dropdown.Option("Corrida (9V)"),
            ft.dropdown.Option("Corrida (10V)")
        ]
    )

    gear_profile_dd = ft.Dropdown(
        label="Perfil do Escalonamento",
        value="Safe / Equilibrado",
        width=320,
        border_radius=8,
        options=[
            ft.dropdown.Option("Safe / Equilibrado"),
            ft.dropdown.Option("Agressivo (Aceleração Rápida)")
        ]
    )

    brakes_dd = ft.Dropdown(
        label="Freios Instalados",
        value="Corrida",
        width=320,
        border_radius=8,
        options=[ft.dropdown.Option("Original"), ft.dropdown.Option("Corrida")]
    )

    suspension_dd = ft.Dropdown(
        label="Suspensão Instalada",
        value="Corrida",
        width=320,
        border_radius=8,
        options=[
            ft.dropdown.Option("Original"),
            ft.dropdown.Option("Rua"),
            ft.dropdown.Option("Esporte"),
            ft.dropdown.Option("Corrida"),
            ft.dropdown.Option("Drift"),
            ft.dropdown.Option("Rally")
        ]
    )

    aero_kit_dd = ft.Dropdown(
        label="Possui Kit Aerodinâmico?",
        value="Não",
        width=320,
        border_radius=8,
        options=[ft.dropdown.Option("Sim"), ft.dropdown.Option("Não")]
    )

    front_bumper_dd = ft.Dropdown(
        label="Para-choque Dianteiro Ajustável",
        value="Sim",
        width=320,
        visible=False,
        border_radius=8,
        options=[ft.dropdown.Option("Sim"), ft.dropdown.Option("Não")]
    )
    rear_wing_dd = ft.Dropdown(
        label="Aerofólio Traseiro Ajustável",
        value="Sim",
        width=320,
        visible=False,
        border_radius=8,
        options=[ft.dropdown.Option("Sim"), ft.dropdown.Option("Não")]
    )

    def on_aero_kit_change(e):
        has_aero = (aero_kit_dd.value == "Sim")
        front_bumper_dd.visible = has_aero
        rear_wing_dd.visible = has_aero
        page.update()

    aero_kit_dd.on_change = on_aero_kit_change

    # ---------------------------------------------------------
    # EXIBIÇÃO DE RESULTADOS & AJUSTES FINOS
    # ---------------------------------------------------------
    result_title = ft.Text(value="⚙️ Status: Monte o kit de peças e clique em Gerar Tunagem.", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300)
    result_details = ft.Text(value="Os cálculos finos de suspensão, alinhamento, marchas e diferencial aparecerão aqui.", size=13, color=ft.Colors.WHITE_70)

    garagem_list_view = ft.ListView(expand=True, spacing=10, padding=10)

    def atualizar_view_garagem():
        nonlocal setups_salvos
        setups_salvos = carregar_garagem()
        garagem_list_view.controls.clear()
        if not setups_salvos:
            garagem_list_view.controls.append(ft.Text("Nenhum setup salvo na garagem ainda.", color=ft.Colors.WHITE_54, size=14))
        else:
            for idx, item in enumerate(setups_salvos):
                def remover_item(e, index=idx):
                    deletar_setup_banco(index)
                    atualizar_view_garagem()
                    page.update()

                card = ft.Card(
                    content=ft.Container(
                        padding=15,
                        content=ft.Column([
                            ft.Row([
                                ft.Text(f"🏎️ {item['nome']}", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300),
                                ft.Container(content=ft.Text("🗑️", size=18), on_click=remover_item, padding=5)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Text(f"Modalidade: {item['modalidade']} | Tração: {item['tracao']}", size=12, color=ft.Colors.WHITE_70),
                            ft.Text(item['detalhes'], size=12, color=ft.Colors.WHITE)
                        ])
                    )
                )
                garagem_list_view.controls.append(card)

    def salvar_na_garagem_click(e):
        if ultimo_setup_calculado:
            salvar_setup_banco(ultimo_setup_calculado)
            atualizar_view_garagem()
            save_btn.visible = False
            result_title.value += " (Salvo na Garagem! ✅)"
            page.update()

    save_btn = ft.Container(
        content=ft.Text("💾 SALVAR NA GARAGEM", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        on_click=salvar_na_garagem_click,
        bgcolor=ft.Colors.GREEN_600,
        border_radius=20,
        padding=ft.Padding(20, 12, 20, 12),
        visible=False,
        alignment=ft.Alignment(0, 0)
    )

    def calcular_tunagem(e):
        nonlocal ultimo_setup_calculado
        try:
            peso = float(weight_input.value)
            potencia = float(power_input.value)
            pct_dian = float(front_bias_input.value)
            bias = pct_dian / 100.0
            bias_tras = 1.0 - bias
            relacao_peso_pot = peso / potencia if potencia > 0 else 0

            pneu_diant = 1.95
            pneu_tras = 1.90 if "RWD" in drivetrain_dd.value else 1.95

            trans_val = transmission_dd.value
            final_drive = 3.20 if relacao_peso_pot < 2.0 else (3.55 if relacao_peso_pot < 3.0 else (3.80 if relacao_peso_pot < 4.0 else 4.10))
            mod = modality_dd.value
            if "Arrancada" in mod: final_drive -= 0.30
            elif "Drift" in mod: final_drive += 0.20

            perfil_marcha = gear_profile_dd.value
            if "Agressivo" in perfil_marcha:
                final_drive += 0.35
                first_gear = 3.60
                last_gear = 0.85
            else:
                first_gear = 3.30
                last_gear = 0.75

            if trans_val in ["Original", "Rua"]:
                gear_setting = "🔒 Bloqueado"
            elif trans_val == "Esporte":
                gear_setting = f"Final Drive: {final_drive:.2f} ({perfil_marcha}) | Marchas: Bloqueadas"
            else:
                num_marchas = 6
                if "7V" in trans_val: num_marchas = 7
                elif "8V" in trans_val: num_marchas = 8
                elif "9V" in trans_val: num_marchas = 9
                elif "10V" in trans_val: num_marchas = 10

                gears = [f"{i+1}ª: {first_gear - (i * (first_gear - last_gear) / (num_marchas - 1)):.2f}" for i in range(num_marchas)]
                gear_setting = f"Final Drive: {final_drive:.2f} [{perfil_marcha}]\n    - Escalonamento: {' | '.join(gears)}"

            if "Drift" in mod:
                cambagem, convergencia, caster, altura_carro = "Dianteira: -5.0° | Traseira: -1.0°", "Dianteira: 0.2° | Traseira: -0.1°", "7.0°", "Baixa / Média-Baixa"
            elif "Rally" in mod:
                cambagem, convergencia, caster, altura_carro = "Dianteira: -1.0° | Traseira: -0.8°", "Dianteira: 0.0° | Traseira: 0.0°", "6.0°", "Alta (Curso Máximo)"
            else:
                cambagem, convergencia, caster, altura_carro = "Dianteira: -2.0° | Traseira: -1.5°", "Dianteira: 0.0° | Traseira: -0.1°", "6.0°", "Baixa"

            arb_diant, arb_tras = 1.0 + (64.0 * bias), 1.0 + (64.0 * bias_tras)
            mola_min, mola_max = peso * 0.05, peso * 0.25
            mola_diant = mola_min + ((mola_max - mola_min) * bias)
            mola_tras = mola_min + ((mola_max - mola_min) * bias_tras)

            rebound_diant, rebound_tras = 3.0 + (10.0 * bias), 3.0 + (10.0 * bias_tras)
            bump_diant, bump_tras = rebound_diant * 0.6, rebound_tras * 0.6

            if aero_kit_dd.value == "Sim":
                f_val = f"{peso * 0.08:.1f} kgf" if front_bumper_dd.value == "Sim" else "Bloqueado"
                r_val = f"{peso * 0.12:.1f} kgf" if rear_wing_dd.value == "Sim" else "Bloqueado"
                aero_setting = f"Dianteira: {f_val} | Traseira: {r_val}"
            else:
                aero_setting = "Sem kit aerodinâmico ajustável"

            # ---------------------------------------------------------
            # REGRA AVANÇADA DE DIFERENCIAIS (FWD, RWD, AWD)
            # ---------------------------------------------------------
            tracao_tipo = drivetrain_dd.value
            if "AWD" in tracao_tipo:
                if "Drift" in mod:
                    diff_text = "• Dianteira: Aceleração 100% | Desaceleração 0%\n• Traseira: Aceleração 100% | Desaceleração 100%\n• Torque Central: 85% (Foco Traseira)"
                elif "Rally" in mod:
                    diff_text = "• Dianteira: Aceleração 50% | Desaceleração 0%\n• Traseira: Aceleração 75% | Desaceleração 50%\n• Torque Central: 60% (Traseira)"
                elif "Arrancada" in mod:
                    diff_text = "• Dianteira: Aceleração 100% | Desaceleração 0%\n• Traseira: Aceleração 100% | Desaceleração 0%\n• Torque Central: 50% (Neutro)"
                else: # Grip / Asfalto
                    diff_text = "• Dianteira: Aceleração 30% | Desaceleração 0%\n• Traseira: Aceleração 50% | Desaceleração 10%\n• Torque Central: 65% (Foco Traseira)"
            elif "FWD" in tracao_tipo:
                if "Arrancada" in mod:
                    diff_text = "• Aceleração: 100% | Desaceleração: 0%"
                else:
                    diff_text = "• Aceleração: 45% | Desaceleração: 0%"
            else: # RWD
                if "Drift" in mod:
                    diff_text = "• Aceleração: 100% | Desaceleração: 100%"
                elif "Arrancada" in mod:
                    diff_text = "• Aceleração: 100% | Desaceleração: 0%"
                elif "Rally" in mod:
                    diff_text = "• Aceleração: 75% | Desaceleração: 25%"
                else: # Grip / Asfalto
                    diff_text = "• Aceleração: 65% | Desaceleração: 15%"

            car_label = car_name.value if car_name.value else "Projeto Sem Nome"
            result_title.value = f"✅ TUNAGEM FINA GERADA: {car_label} ({peso}kg)"

            detalhes_str = (
                f"📊 ESPECIFICAÇÃO FINAL APÓS PEÇAS:\n"
                f"• Peso: {peso}kg | Potência: {potencia}CV | Relação: {relacao_peso_pot:.2f} kg/CV\n"
                f"• Tração: {drivetrain_dd.value} | Modalidade: {modality_dd.value}\n\n"
                f"⚙️ AJUSTES FINOS CALCULADOS:\n"
                f"------------------------------------------------------------------------\n"
                f"🔹 Pressão Pneus: Dianteira {pneu_diant:.2f} bar | Traseira {pneu_tras:.2f} bar\n"
                f"🔹 Transmissão ({perfil_marcha}):\n    - {gear_setting}\n"
                f"🔹 Alinhamento:\n    - Cambagem: {cambagem}\n    - Convergência: {convergencia}\n    - Caster: {caster}\n"
                f"🔹 Barras Estabilizadoras: Dianteira {arb_diant:.2f} | Traseira {arb_tras:.2f}\n"
                f"🔹 Molas: Dianteira {mola_diant:.1f} kgf/mm | Traseira {mola_tras:.1f} kgf/mm (Altura: {altura_carro})\n"
                f"🔹 Amortecimento Rebound: Dianteira {rebound_diant:.1f} | Traseira {rebound_tras:.1f}\n"
                f"🔹 Amortecimento Bump: Dianteira {bump_diant:.1f} | Traseira {bump_tras:.1f}\n"
                f"🔹 Aerodinâmica Downforce: {aero_setting}\n"
                f"🔹 Freios: Balanço {pct_dian:.1f}% | Pressão 100%\n"
                f"🔹 Diferencial de Corrida ({drivetrain_dd.value}):\n{diff_text}"
            )

            result_details.value = detalhes_str
            result_title.color = ft.Colors.CYAN_300

            ultimo_setup_calculado = {
                "nome": car_label,
                "modalidade": modality_dd.value,
                "tracao": drivetrain_dd.value,
                "detalhes": detalhes_str
            }
            save_btn.visible = True

        except ValueError:
            result_title.value = "⚠️ Preencha os valores de Peso e Potência"
            result_details.value = "Insira os números resultantes das peças para calcular a tunagem."
            result_title.color = ft.Colors.RED_400
            save_btn.visible = False

        page.update()

    calc_btn = ft.Container(
        content=ft.Text("⚡ GERAR TUNAGEM FINA", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        on_click=calcular_tunagem,
        bgcolor=ft.Colors.RED_ACCENT_400,
        border_radius=20,
        padding=ft.Padding(30, 15, 30, 15),
        alignment=ft.Alignment(0, 0)
    )

    # ---------------------------------------------------------
    # LAYOUT DAS TELAS
    # ---------------------------------------------------------
    left_column = ft.Column(
        controls=[
            ft.Text("🏎️ Etapa 1: Carro & Simulação de Peças", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300),
            search_input,
            veiculo_dropdown,
            car_name, weight_input, power_input, front_bias_input
        ],
        spacing=10
    )

    right_column = ft.Column(
        controls=[
            ft.Text("🔧 Etapa 2: Peças & Upgrades Instalados", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300),
            modality_dd, drivetrain_dd, transmission_dd, gear_profile_dd, brakes_dd, suspension_dd, aero_kit_dd, front_bumper_dd, rear_wing_dd
        ],
        spacing=10
    )

    container_calculadora = ft.Container(
        padding=10,
        content=ft.Column([
            ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.START,
                spacing=40,
                controls=[left_column, right_column]
            ),
            ft.Container(height=15),
            ft.Row([calc_btn, save_btn], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
            ft.Container(height=15),
            ft.Divider(color=ft.Colors.WHITE_24),
            result_title,
            result_details
        ])
    )

    atualizar_view_garagem()
    container_garagem = ft.Container(
        padding=10,
        content=ft.Column([
            ft.Text("🏎️ Garagem de Setups Salvos", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300),
            ft.Divider(color=ft.Colors.WHITE_24),
            garagem_list_view
        ])
    )

    content_area = ft.Container(content=container_calculadora, expand=True)

    btn_calc = ft.Container(
        content=ft.Text("⚡ Simulação & Tunagem", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        on_click=lambda e: trocar_view(0),
        bgcolor=ft.Colors.CYAN_800,
        border_radius=10,
        padding=ft.Padding(15, 10, 15, 10),
        alignment=ft.Alignment(0, 0)
    )

    btn_garagem = ft.Container(
        content=ft.Text("🏎️ Garagem", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        on_click=lambda e: trocar_view(1),
        bgcolor=ft.Colors.TRANSPARENT,
        border_radius=10,
        padding=ft.Padding(15, 10, 15, 10),
        alignment=ft.Alignment(0, 0)
    )

    def trocar_view(index):
        if index == 0:
            content_area.content = container_calculadora
            btn_calc.bgcolor = ft.Colors.CYAN_800
            btn_garagem.bgcolor = ft.Colors.TRANSPARENT
        else:
            atualizar_view_garagem()
            content_area.content = container_garagem
            btn_calc.bgcolor = ft.Colors.TRANSPARENT
            btn_garagem.bgcolor = ft.Colors.CYAN_800
        page.update()

    page.add(
        ft.Column([
            ft.Text("⚡ Calculadora de Tunagem Forza - Safira Spec", size=22, weight=ft.FontWeight.BOLD),
            ft.Text("Simule peças e gere os ajustes finos para seu veículo", size=12, color=ft.Colors.WHITE_54),
            ft.Container(height=10),
            ft.Row([btn_calc, btn_garagem], spacing=10),
            ft.Divider(color=ft.Colors.WHITE_24),
            content_area
        ], expand=True)
    )

if __name__ == "__main__":
    ft.run(main)
