import flet as ft
import os
import sqlite3
import csv

# ---------------------------------------------------------
# CONFIGURAÇÃO DO BANCO DE DADOS SQLite & IMPORTAÇÃO DO CSV
# ---------------------------------------------------------
DB_NAME = "veiculos.db"

def conectar_banco():
    return sqlite3.connect(DB_NAME)

def inicializar_banco():
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Tabela principal para os 638 veículos
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
    
    # Tabela para a Garagem de Setups Salvos pelo usuário
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
    
    # Importação automática do CSV se a tabela de veículos estiver vazia
    cursor.execute("SELECT COUNT(*) FROM veiculos")
    if cursor.fetchone()[0] == 0:
        csv_path = "veiculos.csv"
        if os.path.exists(csv_path):
            with open(csv_path, mode="r", encoding="utf-8") as file:
                reader = csv.reader(file)
                next(reader, None)  # Pula o cabeçalho se houver
                for linha in reader:
                    if len(linha) >= 8:
                        cursor.execute("""
                            INSERT INTO veiculos (marca, modelo, classe, pi_original, peso_fabrica, potencia, distribuicao_dianteira, tracao)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (linha[0], linha[1], linha[2], linha[3], linha[4], linha[5], linha[6], linha[7]))
            conn.commit()
            
    conn.close()

# Executa a inicialização e importação assim que o script roda
inicializar_banco()

def carregar_garagem():
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute("SELECT nome, modalidade, tracao, detalhes FROM garagem_setups")
        rows = cursor.fetchall()
        conn.close()
        
        setups = []
        for row in rows:
            setups.append({
                "nome": row[0],
                "modalidade": row[1],
                "tracao": row[2],
                "detalhes": row[3]
            })
        return setups
    except Exception:
        return []

def salvar_setup_banco(setup):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO garagem_setups (nome, modalidade, tracao, detalhes)
        VALUES (?, ?, ?, ?)
    """, (setup["nome"], setup["modalidade"], setup["tracao"], setup["detalhes"]))
    conn.commit()
    conn.close()

def deletar_setup_banco(index):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM garagem_setups")
    ids = cursor.fetchall()
    if index < len(ids):
        target_id = ids[index][0]
        cursor.execute("DELETE FROM garagem_setups WHERE id = ?", (target_id,))
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
    # CAMPOS DE ENTRADA (CALCULADORA)
    # ---------------------------------------------------------
    car_name = ft.TextField(label="Nome do Carro / Projeto (Opcional)", width=320, border_radius=8)
    weight_input = ft.TextField(label="Peso Total (kg)", value="1350", width=320, border_radius=8, keyboard_type=ft.KeyboardType.NUMBER)
    power_input = ft.TextField(label="Potência (CV/HP)", value="450", width=320, border_radius=8, keyboard_type=ft.KeyboardType.NUMBER)
    front_bias_input = ft.TextField(label="Distribuição Dianteira (%)", value="52.00", width=320, border_radius=8, keyboard_type=ft.KeyboardType.NUMBER)
    
    modality_dd = ft.Dropdown(
        label="Modalidade",
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

    front_bumper_dd = ft.Dropdown(
        label="Para-choque Dianteiro de Corrida",
        value="Sim",
        width=320,
        visible=False,
        border_radius=8,
        options=[ft.dropdown.Option("Sim"), ft.dropdown.Option("Não")]
    )
    rear_wing_dd = ft.Dropdown(
        label="Aerofólio de Corrida",
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

    aero_kit_dd = ft.Dropdown(
        label="Possui Kit Aerodinâmico?",
        value="Não",
        width=320,
        border_radius=8,
        options=[ft.dropdown.Option("Sim"), ft.dropdown.Option("Não")]
    )
    aero_kit_dd.on_change = on_aero_kit_change

    drivetrain_dd = ft.Dropdown(
        label="Tração",
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
        label="Transmissão",
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
    brakes_dd = ft.Dropdown(
        label="Freios",
        value="Corrida",
        width=320,
        border_radius=8,
        options=[ft.dropdown.Option("Original"), ft.dropdown.Option("Corrida")]
    )
    suspension_dd = ft.Dropdown(
        label="Suspensão",
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

    # ---------------------------------------------------------
    # EXIBIÇÃO DE RESULTADOS & BOTÕES
    # ---------------------------------------------------------
    result_title = ft.Text(value="💾 Setup Calculado: Aguardando cálculo...", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300)
    result_details = ft.Text(value="Preencha os dados acima e clique em Calcular Tunagem.", size=13, color=ft.Colors.WHITE_70)

    garagem_list_view = ft.ListView(expand=True, spacing=10, padding=10)

    def atualizar_view_garagem():
        nonlocal setups_salvos
        setups_salvos = carregar_garagem()
        garagem_list_view.controls.clear()
        if not setups_salvos:
            garagem_list_view.controls.append(
                ft.Text("Nenhum setup salvo na garagem ainda.", color=ft.Colors.WHITE_54, size=14)
            )
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
                                ft.Container(
                                    content=ft.Text("🗑️", size=18),
                                    on_click=remover_item,
                                    padding=5
                                )
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
            result_title.value += " (Salvo com sucesso no Banco de Dados! ✅)"
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

            # ---------------------------------------------------------
            # CÁLCULO DE TRANSMISSÃO E ESCALONAMENTO DE MARCHAS
            # ---------------------------------------------------------
            trans_val = transmission_dd.value
            
            if relacao_peso_pot < 2.0:
                final_drive = 3.20
            elif relacao_peso_pot < 3.0:
                final_drive = 3.55
            elif relacao_peso_pot < 4.0:
                final_drive = 3.80
            else:
                final_drive = 4.10

            mod = modality_dd.value
            if "Arrancada" in mod:
                final_drive -= 0.30
            elif "Drift" in mod:
                final_drive += 0.20

            if trans_val in ["Original", "Rua"]:
                gear_setting = "🔒 Bloqueado (Sem ajustes disponíveis)"
            elif trans_val == "Esporte":
                gear_setting = f"Marcha Final (Final Drive): {final_drive:.2f} | Marchas Individuais: 🔒 Bloqueadas"
            else:
                num_marchas = 6
                if "7V" in trans_val: num_marchas = 7
                elif "8V" in trans_val: num_marchas = 8
                elif "9V" in trans_val: num_marchas = 9
                elif "10V" in trans_val: num_marchas = 10

                first_gear = 3.30
                last_gear = 0.75 if num_marchas <= 7 else 0.65

                gears = []
                for i in range(num_marchas):
                    if num_marchas > 1:
                        ratio = first_gear - (i * (first_gear - last_gear) / (num_marchas - 1))
                    else:
                        ratio = first_gear
                    gears.append(f"{i+1}ª: {ratio:.2f}")

                gears_str = " | ".join(gears)
                gear_setting = (
                    f"Marcha Final (Final Drive): {final_drive:.2f}\n"
                    f"    - Escalonamento ({num_marchas} Marchas): {gears_str}"
                )

            # ---------------------------------------------------------
            # OUTROS CÁLCULOS DE TUNAGEM & ALTURA DO CARRO
            # ---------------------------------------------------------
            if "Drift" in mod:
                cambagem = "Dianteira: -5.0° | Traseira: -1.0°"
                convergencia = "Dianteira: 0.2° (Out) | Traseira: -0.1° (In)"
                caster = "7.0°"
                altura_carro = "Dianteira: Baixa | Traseira: Média-Baixa"
            elif "Rally" in mod:
                cambagem = "Dianteira: -1.0° | Traseira: -0.8°"
                convergencia = "Dianteira: 0.0° | Traseira: 0.0°"
                caster = "6.0°"
                altura_carro = "Dianteira: Alta | Traseira: Alta (Máximo curso de suspensão)"
            elif "Arrancada" in mod:
                cambagem = "Dianteira: 0.0° | Traseira: 0.0°"
                convergencia = "Dianteira: 0.0° | Traseira: 0.0°"
                caster = "5.0°"
                altura_carro = "Dianteira: Baixa | Traseira: Média (Transferência de peso)"
            else:
                cambagem = "Dianteira: -2.0° | Traseira: -1.5°"
                convergencia = "Dianteira: 0.0° | Traseira: -0.1° (In)"
                caster = "6.0°"
                altura_carro = "Dianteira: Baixa | Traseira: Baixa (Menor centro de gravidade)"

            arb_diant = 1.0 + (64.0 * bias)
            arb_tras = 1.0 + (64.0 * bias_tras)

            mola_min = peso * 0.05
            mola_max = peso * 0.25
            mola_diant = mola_min + ((mola_max - mola_min) * bias)
            mola_tras = mola_min + ((mola_max - mola_min) * bias_tras)

            rebound_diant = 3.0 + (10.0 * bias)
            rebound_tras = 3.0 + (10.0 * bias_tras)
            bump_diant = rebound_diant * 0.6
            bump_tras = rebound_tras * 0.6

            if aero_kit_dd.value == "Sim":
                downforce_dian_val = peso * 0.08
                downforce_tras_val = peso * 0.12
                f_val = f"{downforce_dian_val:.1f} kgf" if front_bumper_dd.value == "Sim" else "🔒 Bloqueado"
                r_val = f"{downforce_tras_val:.1f} kgf" if rear_wing_dd.value == "Sim" else "🔒 Bloqueado"
                aero_summary = f"Dianteira [{f_val}] | Traseira [{r_val}]"
                aero_setting = f"Dianteira: {f_val} | Traseira: {r_val}"
            else:
                aero_summary = "🔒 Bloqueado (Sem Kit Aerodinâmico instalado)"
                aero_setting = "Dianteira: 🔒 Bloqueado | Traseira: 🔒 Bloqueado"

            freio_bal = pct_dian
            freio_press = 100

            if "RWD" in drivetrain_dd.value:
                diff_text = "Aceleração: 65% | Desaceleração: 15%"
            elif "FWD" in drivetrain_dd.value:
                diff_text = "Aceleração: 45% | Desaceleração: 10%"
            else:
                diff_text = "Dianteira (Acc: 30% / Desacc: 0%) | Traseira (Acc: 50% / Desacc: 10%) | Balanço Central: 65% Traseira"

            car_label = car_name.value if car_name.value else "Carro sem nome"
            result_title.value = f"💾 Setup Calculado: {car_label} ({peso}kg)"
            
            detalhes_str = (
                f"📊 RESUMO DE PERFORMANCE:\n"
                f"• Relação Peso/Potência: {relacao_peso_pot:.2f} kg/CV | Tração: {drivetrain_dd.value}\n"
                f"• Aerodinâmica (Downforce): {aero_summary}\n\n"
                f"⚙️ AJUSTES RECOMENDADOS DE TUNAGEM:\n"
                f"------------------------------------------------------------------------\n"
                f"🔹 Pressão dos Pneus: Dianteira {pneu_diant:.2f} bar | Traseira {pneu_tras:.2f} bar\n"
                f"🔹 Transmissão:\n"
                f"    - {gear_setting}\n"
                f"🔹 Alinhamento:\n"
                f"    - Cambagem: {cambagem}\n"
                f"    - Convergência: {convergencia}\n"
                f"    - Caster Dianteiro: {caster}\n"
                f"🔹 Barras Estabilizadoras: Dianteira {arb_diant:.2f} | Traseira {arb_tras:.2f}\n"
                f"🔹 Molas:\n"
                f"    - Rigidez: Dianteira {mola_diant:.1f} kgf/mm | Traseira {mola_tras:.1f} kgf/mm\n"
                f"    - Altura do Carro: {altura_carro}\n"
                f"🔹 Amortecimento (Rebound): Dianteira {rebound_diant:.1f} | Traseira {rebound_tras:.1f}\n"
                f"🔹 Amortecimento (Bump/Carga): Dianteira {bump_diant:.1f} | Traseira {bump_tras:.1f}\n"
                f"🔹 Aerodinâmica (Downforce): {aero_setting}\n"
                f"🔹 Freios: Balanço {freio_bal:.1f}% | Pressão {freio_press}%\n"
                f"🔹 Diferencial: {diff_text}"
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
            result_title.value = "⚠️ Erro no Cálculo"
            result_details.value = "Por favor, insira valores numéricos válidos para Peso, Potência e Distribuição."
            result_title.color = ft.Colors.RED_400
            save_btn.visible = False
        
        page.update()

    calc_btn = ft.Container(
        content=ft.Text("⚡ CALCULAR TUNAGEM", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
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
            ft.Text("📋 Dados do Veículo", size=15, weight=ft.FontWeight.BOLD),
            car_name, weight_input, power_input, front_bias_input, modality_dd, aero_kit_dd, front_bumper_dd, rear_wing_dd
        ],
        spacing=10
    )

    right_column = ft.Column(
        controls=[
            ft.Container(height=25),
            drivetrain_dd, transmission_dd, brakes_dd, suspension_dd
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
        content=ft.Text("⚡ Calculadora", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
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
            ft.Text("Ajustes precisos de performance para o seu carro", size=12, color=ft.Colors.WHITE_54),
            ft.Container(height=10),
            ft.Row([btn_calc, btn_garagem], spacing=10),
            ft.Divider(color=ft.Colors.WHITE_24),
            content_area
        ], expand=True)
    )

if __name__ == "__main__":
    ft.run(main)
