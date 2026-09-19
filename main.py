import flet as ft
import csv
import json
import os

# Compatibilidade de botões para Flet 0.x e Flet 1.0+
ElevatedButton = getattr(ft, "ElevatedButton", getattr(ft, "Button", None))

# Arquivo para persistência da garagem local
GARAGEM_FILE = "garagem.json"

def carregar_garagem():
    if os.path.exists(GARAGEM_FILE):
        try:
            with open(GARAGEM_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def salvar_garagem(garagem):
    try:
        with open(GARAGEM_FILE, "w", encoding="utf-8") as f:
            json.dump(garagem, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Erro ao salvar garagem: {e}")

def carregar_veiculos_csv():
    veiculos = []
    files_to_check = [f for f in os.listdir(".") if f.lower().endswith(".csv")]
    if not files_to_check:
        files_to_check = ["veiculos.csv", "veiculos_fh6.csv", "dados_carros.csv"]

    for filename in files_to_check:
        if os.path.exists(filename):
            for encoding in ["utf-8-sig", "utf-8", "latin1", "cp1252"]:
                try:
                    with open(filename, mode="r", encoding=encoding) as f:
                        content = f.read()
                        if not content.strip():
                            continue
                        lines = [line for line in content.splitlines() if line.strip()]
                        if not lines:
                            continue
                        first_line = lines[0]
                        delimiter = ";" if ";" in first_line else ("," if "," in first_line else "\t")
                        
                        f.seek(0)
                        reader = csv.DictReader(f, delimiter=delimiter)
                        for row in reader:
                            clean_row = {k.strip() if k else "": v.strip() if v else "" for k, v in row.items()}
                            veiculos.append(clean_row)
                        if veiculos:
                            return veiculos
                except Exception as e:
                    print(f"Erro ao ler {filename}: {e}")
    return veiculos

def get_value_from_row(row, keywords):
    for k, v in row.items():
        k_clean = k.lower().replace(" ", "").replace("_", "").replace("/", "").replace("(", "").replace(")", "").replace("%", "")
        for kw in keywords:
            if kw in k_clean:
                return v
    return ""

def calcular_marchas(num_marchas, modo="safe"):
    # Tabela de marchas base Safira Spec (6 a 10 marchas)
    tabelas_marchas = {
        6: [2.80, 1.90, 1.40, 1.10, 0.92, 0.78],
        7: [3.15, 2.20, 1.65, 1.30, 1.08, 0.90, 0.78],
        8: [3.40, 2.30, 1.70, 1.35, 1.10, 0.92, 0.78, 0.67],
        9: [3.60, 2.50, 1.85, 1.45, 1.18, 0.98, 0.82, 0.70, 0.58],
        10: [3.80, 2.70, 2.00, 1.60, 1.30, 1.08, 0.90, 0.77, 0.65, 0.55]
    }

    # Transmissões Finais exatas do Safira Spec
    finais = {
        6: {"safe": 3.50, "agressivo": 3.80},
        7: {"safe": 3.70, "agressivo": 4.10},
        8: {"safe": 3.60, "agressivo": 3.90},
        9: {"safe": 3.80, "agressivo": 4.10},
        10: {"safe": 3.90, "agressivo": 4.30}
    }

    num = int(num_marchas)
    modo_key = modo.lower()

    if num in tabelas_marchas:
        final_drive = finais[num][modo_key]
        marchas = tabelas_marchas[num]
        return final_drive, marchas
    else:
        return 3.70, [2.80, 1.90, 1.40, 1.10, 0.92][:num]

def main(page: ft.Page):
    page.title = "Calculadora de Tunagem Forza - Safira Spec"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 15
    page.scroll = ft.ScrollMode.AUTO

    setups_salvos = carregar_garagem()
    ultimo_setup_calculado = {}

    lista_veiculos = carregar_veiculos_csv()

    # Notificação segura na tela
    def mostrar_snack(mensagem):
        try:
            snack = ft.SnackBar(ft.Text(mensagem))
            page.snack_bar = snack
            snack.open = True
        except Exception:
            try:
                page.open(ft.SnackBar(ft.Text(mensagem)))
            except Exception:
                pass
        page.update()

    # ETAPA 1: Dados do Veículo
    txt_nome = ft.TextField(label="Nome do Projeto / Carro", hint_text="Ex: Mustang GT 2018", expand=True)
    txt_peso = ft.TextField(label="Peso (kg)", keyboard_type=ft.KeyboardType.NUMBER, value="1500", expand=True)
    txt_potencia = ft.TextField(label="Potência (CV/HP)", keyboard_type=ft.KeyboardType.NUMBER, value="450", expand=True)
    txt_distribuicao = ft.TextField(label="Distribuição Dianteira (%)", keyboard_type=ft.KeyboardType.NUMBER, value="54", expand=True)
    
    lbl_status_csv = ft.Text(
        f"🚗 Base de dados: {len(lista_veiculos)} veículos encontrados" if lista_veiculos else "⚠️ Nenhum arquivo CSV encontrado na raiz",
        size=12,
        weight="bold",
        color="greenAccent" if lista_veiculos else "orangeAccent"
    )

    opcoes_carros = []
    for v in lista_veiculos:
        marca = get_value_from_row(v, ["marca", "brand", "manufacturer"])
        modelo = get_value_from_row(v, ["modelo", "model", "nome", "carro", "veiculo"])
        nome_c = f"{marca} {modelo}".strip() if (marca or modelo) else str(list(v.values())[0])
        if nome_c and nome_c not in [opt.key for opt in opcoes_carros]:
            opcoes_carros.append(ft.dropdown.Option(key=nome_c, text=nome_c))

    def selecionar_veiculo(e):
        if dd_busca_carro.value:
            for v in lista_veiculos:
                marca = get_value_from_row(v, ["marca", "brand", "manufacturer"])
                modelo = get_value_from_row(v, ["modelo", "model", "nome", "carro", "veiculo"])
                nome_completo = f"{marca} {modelo}".strip() if (marca or modelo) else str(list(v.values())[0])
                
                if nome_completo == dd_busca_carro.value:
                    txt_nome.value = nome_completo
                    
                    p_str = get_value_from_row(v, ["peso"])
                    p_str = p_str.replace("kg", "").replace(".", "").replace(",", "").strip()
                    if p_str:
                        txt_peso.value = p_str
                    
                    pot_str = get_value_from_row(v, ["potencia", "potên", "hp", "cv", "power"])
                    pot_str = pot_str.lower().replace("cv", "").replace("hp", "").replace(".", "").replace(",", "").strip()
                    if pot_str:
                        txt_potencia.value = pot_str

                    d_str = get_value_from_row(v, ["distribui", "distr"])
                    d_str = d_str.replace("%", "").replace(",", ".").strip()
                    if d_str:
                        txt_distribuicao.value = d_str
                    
                    tr = get_value_from_row(v, ["trac", "traç", "drivetrain", "opção2", "opcao2"]).upper().strip()
                    if "AWD" in tr:
                        dd_tracao.value = "AWD"
                    elif "RWD" in tr:
                        dd_tracao.value = "RWD"
                    elif "FWD" in tr:
                        dd_tracao.value = "FWD"

                    mostrar_snack(f"Veículo '{nome_completo}' carregado!")
                    page.update()
                    break

    dd_busca_carro = ft.Dropdown(
        label="Pesquisar / Carregar Veículo da Base de Dados (CSV)",
        options=opcoes_carros,
        expand=True
    )
    dd_busca_carro.on_change = selecionar_veiculo

    # ETAPA 2: Configurações & Peças Instaladas
    dd_modalidade = ft.Dropdown(
        label="Modalidade de Corrida",
        options=[
            ft.dropdown.Option("Pista / Asfalto"),
            ft.dropdown.Option("Rali / Terra"),
            ft.dropdown.Option("Offroad / Todo Terreno"),
            ft.dropdown.Option("Drift"),
        ],
        value="Pista / Asfalto",
        expand=True
    )

    dd_tracao = ft.Dropdown(
        label="Tração Atual",
        options=[
            ft.dropdown.Option("AWD"),
            ft.dropdown.Option("RWD"),
            ft.dropdown.Option("FWD"),
        ],
        value="AWD",
        expand=True
    )

    dd_marchas = ft.Dropdown(
        label="Tipo de Câmbio Instalado (Marchas)",
        options=[
            ft.dropdown.Option("6"),
            ft.dropdown.Option("7"),
            ft.dropdown.Option("8"),
            ft.dropdown.Option("9"),
            ft.dropdown.Option("10"),
        ],
        value="6",
        expand=True
    )

    dd_modo_marchas = ft.Dropdown(
        label="Perfil de Escalonamento",
        options=[
            ft.dropdown.Option("Safe"),
            ft.dropdown.Option("Agressivo"),
        ],
        value="Safe",
        expand=True
    )

    # Lista completa dos 10 Compostos de Pneus do Forza
    dd_pneus = ft.Dropdown(
        label="Composto de Pneus",
        options=[
            ft.dropdown.Option("Original"),
            ft.dropdown.Option("Pneu de Rua"),
            ft.dropdown.Option("Pneu Esportivo"),
            ft.dropdown.Option("Semi-Slick"),
            ft.dropdown.Option("Pneu Slick (Corrida)"),
            ft.dropdown.Option("Pneu de Rally"),
            ft.dropdown.Option("Pneu de Drift"),
            ft.dropdown.Option("Pneu de Arrancada (Drag)"),
            ft.dropdown.Option("Pneu Off-Road"),
            ft.dropdown.Option("Pneu de Neve / Lama"),
        ],
        value="Pneu Slick (Corrida)",
        expand=True
    )

    dd_suspensao = ft.Dropdown(
        label="Suspensão Instalada",
        options=[
            ft.dropdown.Option("Corrida / Pista"),
            ft.dropdown.Option("Rali"),
            ft.dropdown.Option("Offroad"),
            ft.dropdown.Option("Drift"),
        ],
        value="Corrida / Pista",
        expand=True
    )

    dd_freios = ft.Dropdown(
        label="Freios Instalados",
        options=[
            ft.dropdown.Option("Freios de Corrida"),
            ft.dropdown.Option("Freios de Rua / Originais"),
        ],
        value="Freios de Corrida",
        expand=True
    )

    dd_aerodinamica_kit = ft.Dropdown(
        label="Possui Kit Aerodinâmico Ajustável?",
        options=[
            ft.dropdown.Option("Sim (Aerofólio/Pára-choque Ajustável)"),
            ft.dropdown.Option("Não (Aerodinâmica Original)"),
        ],
        value="Sim (Aerofólio/Pára-choque Ajustável)",
        expand=True
    )

    slider_aero = ft.Slider(
        min=0,
        max=100,
        divisions=10,
        value=50,
        label="{value}% (Velocidade vs Curva)"
    )

    lbl_aero_status = ft.Text("[ Velocidade | █ █ █ ░ ░ | Curva ] (50%)", weight="bold", color="cyan")

    def on_aero_change(e):
        val = int(slider_aero.value)
        blocos = int(val / 20)
        vazia = 5 - blocos
        bar = "█ " * blocos + "░ " * vazia
        lbl_aero_status.value = f"[ Velocidade | {bar.strip()} | Curva ] ({val}%)"
        page.update()

    slider_aero.on_change = on_aero_change

    # Área de Resultados
    container_resultados = ft.Column(spacing=10)

    def calcular_tunagem(e):
        nonlocal ultimo_setup_calculado
        try:
            peso = float(txt_peso.value.replace(",", "."))
            potencia = float(txt_potencia.value.replace(",", "."))
            dist_diant = float(txt_distribuicao.value.replace(",", "."))
            modalidade = dd_modalidade.value
            tracao = dd_tracao.value
            num_m = int(dd_marchas.value)
            modo_m = dd_modo_marchas.value
            pneu_tipo = dd_pneus.value
            susp_tipo = dd_suspensao.value
            freios_tipo = dd_freios.value
            possui_aero = dd_aerodinamica_kit.value
            aero_pct = slider_aero.value
        except ValueError:
            mostrar_snack("Por favor, preencha peso, potência e distribuição com números válidos!")
            return

        dist_traseira = 100.0 - dist_diant

        # 1. PRESSÃO DOS PNEUS
        if "Rally" in pneu_tipo or "Off-Road" in pneu_tipo or "Neve" in pneu_tipo or "Rali" in modalidade:
            pneu_d, pneu_t = 1.7, 1.7
        elif "Arrancada" in pneu_tipo or "Drag" in pneu_tipo:
            pneu_d, pneu_t = 1.9, 1.0  # Pressão baixa no eixo motriz para largada
        elif "Drift" in pneu_tipo:
            pneu_d, pneu_t = 2.2, 2.2  # Pressão alta para deslize controlado
        elif "Rua" in pneu_tipo or "Original" in pneu_tipo:
            pneu_d, pneu_t = 2.1, 2.0
        elif "Esportivo" in pneu_tipo or "Semi-Slick" in pneu_tipo:
            pneu_d, pneu_t = 2.0, 1.95
        else: # Slick / Corrida
            pneu_d, pneu_t = 1.9, 1.9

        pneu_d_psi, pneu_t_psi = round(pneu_d * 14.5038, 1), round(pneu_t * 14.5038, 1)
        pneus_str = f"Dianteira: {pneu_d:.1f} bar ({pneu_d_psi} psi) | Traseira: {pneu_t:.1f} bar ({pneu_t_psi} psi) [{pneu_tipo}]"

        # 2. TRANSMISSÃO / CÂMBIO (Safira Spec)
        final_drive, lista_m = calcular_marchas(num_m, modo_m)
        transmissao_str = f"Transmissão Final: {final_drive:.2f} (Modo {modo_m})\n"
        for idx, m_val in enumerate(lista_m, start=1):
            transmissao_str += f" - {idx}ª Marcha: {m_val:.2f}\n"

        # 3. ALINHAMENTO
        if "Rally" in pneu_tipo or "Off-Road" in pneu_tipo or "Rali" in susp_tipo or "Offroad" in susp_tipo:
            camber_d, camber_t = -1.0, -0.5
            toe_d, toe_t = 0.0, 0.0
            caster = 6.0
        elif "Drift" in pneu_tipo or "Drift" in susp_tipo or "Drift" in modalidade:
            camber_d, camber_t = -3.0, -1.0
            toe_d, toe_t = 0.2, -0.1
            caster = 7.0
        else: # Pista / Asfalto
            camber_d, camber_t = -1.5, -1.0
            toe_d, toe_t = 0.0, 0.0
            caster = 6.0
        alinhamento_str = f"Cambagem D/T: {camber_d}° / {camber_t}° | Convergência D/T: {toe_d}° / {toe_t}° | Caster: {caster}°"

        # 4. BARRAS ESTABILIZADORAS (ARBs / STB)
        arb_diant = round(1.0 + (dist_diant / 100.0) * 64.0, 1)
        arb_tras = round(1.0 + (dist_traseira / 100.0) * 64.0, 1)
        arbs_str = f"Dianteira: {arb_diant} | Traseira: {arb_tras}"

        # 5. MOLAS
        mola_diant = round((dist_diant / 100.0) * (peso * 0.15), 1)
        mola_tras = round((dist_traseira / 100.0) * (peso * 0.15), 1)
        molas_str = f"Dianteira: {mola_diant} kgf/mm | Traseira: {mola_tras} kgf/mm"

        # 6. ALTURA DO CARRO
        if "Rally" in pneu_tipo or "Off-Road" in pneu_tipo or "Rali" in susp_tipo or "Offroad" in susp_tipo:
            altura_str = "Elevada / Média (A critério do usuário conforme o terreno)"
        else:
            altura_str = "Mínima / Baixa (A critério do usuário conforme a pista)"

        # 7. AMORTECIMENTO
        reb_diant = round(min(20.0, max(1.0, 0.2 * mola_diant)), 1)
        reb_tras = round(min(20.0, max(1.0, 0.2 * mola_tras)), 1)
        bump_diant = round(0.6 * reb_diant, 1)
        bump_tras = round(0.6 * reb_tras, 1)
        amortecimento_str = f"Rebound (Extensão) D/T: {reb_diant} / {reb_tras}\nBump (Compressão) D/T: {bump_diant} / {bump_tras}"

        # 8. AERODINÂMICA
        if "Sim" in possui_aero:
            aero_d_kgf = round(75 + (aero_pct / 100.0) * 125)
            aero_t_kgf = round(100 + (aero_pct / 100.0) * 180)
            aerodinamica_str = f"Downforce D/T: {aero_d_kgf} kgf / {aero_t_kgf} kgf (Equilíbrio {aero_pct:.0f}%)"
        else:
            aerodinamica_str = "Aerodinâmica Original de fábrica (sem ajustes disponíveis)"

        # 9. FREIOS
        if "Corrida" in freios_tipo:
            freios_str = "Balanço de Frenagem: 50% Dianteira | Pressão: 100%"
        else:
            freios_str = "Freios Originais / Sem regulagem no menu de tunagem"

        # 10. DIFERENCIAL (Safira Spec)
        if tracao == "AWD":
            diff_str = "Dianteiro: Aceleração 25% / Desaceleração 0%\nTraseiro: Aceleração 75% / Desaceleração 15%\nTorque Central: 65% Traseira"
        elif tracao == "RWD":
            diff_str = "Aceleração: 45% / Desaceleração: 10%"
        else: # FWD
            diff_str = "Aceleração: 35% / Desaceleração: 0%"

        ultimo_setup_calculado = {
            "nome": txt_nome.value if txt_nome.value else "Carro sem nome",
            "peso": peso,
            "potencia": potencia,
            "distribuicao": dist_diant,
            "modalidade": modalidade,
            "tracao": tracao,
            "pneus": pneus_str,
            "transmissao": transmissao_str.strip(),
            "alinhamento": alinhamento_str,
            "arbs": arbs_str,
            "molas": molas_str,
            "altura": altura_str,
            "amortecimento": amortecimento_str,
            "aerodinamica": aerodinamica_str,
            "freios": freios_str,
            "diferencial": diff_str
        }

        container_resultados.controls.clear()
        container_resultados.controls.append(
            ft.Card(
                content=ft.Container(
                    padding=15,
                    content=ft.Column([
                        ft.Text(f"🏁 Setup Calculado: {ultimo_setup_calculado['nome']}", size=18, weight="bold", color="greenAccent"),
                        ft.Text(f"📊 {peso:.0f} kg | {potencia:.0f} CV | {dist_diant:.0f}% Dianteira | Tração {tracao} | {modalidade}", size=12, color="white70"),
                        ft.Divider(),
                        ft.Text(f"1. 🛞 Pressão dos Pneus:\n{pneus_str}"),
                        ft.Text(f"2. 🚦 Transmissão / Câmbio ({num_m} Marchas - Modo {modo_m}):\n{transmissao_str.strip()}"),
                        ft.Text(f"3. 📐 Alinhamento:\n{alinhamento_str}"),
                        ft.Text(f"4. ⚖️ Barras Estabilizadoras (ARBs / STB):\n{arbs_str}"),
                        ft.Text(f"5. ⚙️ Molas:\n{molas_str}"),
                        ft.Text(f"6. 📏 Altura do Carro:\n{altura_str}"),
                        ft.Text(f"7. 📉 Amortecimento:\n{amortecimento_str}"),
                        ft.Text(f"8. ✈️ Aerodinâmica:\n{aerodinamica_str}"),
                        ft.Text(f"9. 🛑 Freios:\n{freios_str}"),
                        ft.Text(f"10. 🎯 Diferencial ({tracao}):\n{diff_str}"),
                        ft.Divider(),
                        ElevatedButton("Salvar Setup na Garagem", icon="save", on_click=salvar_na_garagem_click)
                    ])
                )
            )
        )
        page.update()

    def salvar_na_garagem_click(e):
        if ultimo_setup_calculado:
            setups_salvos.append(ultimo_setup_calculado)
            salvar_garagem(setups_salvos)
            atualizar_view_garagem()
            mostrar_snack("Setup completo salvo na garagem com sucesso!")

    # View da Garagem (Mostra todas as 10 categorias calculadas)
    garagem_list_view = ft.Column(spacing=10)

    def atualizar_view_garagem():
        garagem_list_view.controls.clear()
        if not setups_salvos:
            garagem_list_view.controls.append(ft.Text("Nenhum setup salvo na garagem ainda.", italic=True))
        else:
            for idx, item in enumerate(setups_salvos):
                def deletar_item(e, index=idx):
                    setups_salvos.pop(index)
                    salvar_garagem(setups_salvos)
                    atualizar_view_garagem()
                    page.update()

                garagem_list_view.controls.append(
                    ft.Card(
                        content=ft.Container(
                            padding=15,
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(f"🚗 {item.get('nome', 'Carro sem nome')}", size=16, weight="bold", color="greenAccent"),
                                    ft.IconButton(
                                        icon=getattr(ft.Icons, "DELETE_OUTLINED", getattr(ft.Icons, "DELETE", None)),
                                        icon_color="red",
                                        tooltip="Excluir Setup",
                                        on_click=deletar_item
                                    )
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Text(f"📊 {item.get('peso', 1500):.0f} kg | {item.get('potencia', 450):.0f} CV | {item.get('distribuicao', 54):.0f}% Dianteira | Tração {item.get('tracao', 'AWD')}", size=12, color="white70"),
                                ft.Divider(),
                                ft.Text(f"1. 🛞 Pneus: {item.get('pneus', 'N/A')}", size=12),
                                ft.Text(f"2. 🚦 Transmissão:\n{item.get('transmissao', 'N/A')}", size=12),
                                ft.Text(f"3. 📐 Alinhamento: {item.get('alinhamento', 'N/A')}", size=12),
                                ft.Text(f"4. ⚖️ STB (ARBs): {item.get('arbs', 'N/A')}", size=12),
                                ft.Text(f"5. ⚙️ Molas: {item.get('molas', 'N/A')}", size=12),
                                ft.Text(f"6. 📏 Altura: {item.get('altura', 'N/A')}", size=12),
                                ft.Text(f"7. 📉 Amortecimento:\n{item.get('amortecimento', 'N/A')}", size=12),
                                ft.Text(f"8. ✈️ Aerodinâmica: {item.get('aerodinamica', 'N/A')}", size=12),
                                ft.Text(f"9. 🛑 Freios: {item.get('freios', 'N/A')}", size=12),
                                ft.Text(f"10. 🎯 Diferencial:\n{item.get('diferencial', 'N/A')}", size=12),
                            ])
                        )
                    )
                )

    atualizar_view_garagem()

    # Conteúdo das Vistas
    conteudo_calculadora = ft.Container(
        padding=10,
        content=ft.Column([
            ft.Text("ETAPA 1: Dados do Veículo", size=16, weight="bold", color="blueAccent"),
            ft.Row([dd_busca_carro]),
            lbl_status_csv,
            ft.Row([txt_nome]),
            ft.Row([txt_peso, txt_potencia, txt_distribuicao]),
            ft.Divider(),
            ft.Text("ETAPA 2: Configurações & Peças Instaladas", size=16, weight="bold", color="blueAccent"),
            ft.Row([dd_modalidade, dd_tracao]),
            ft.Row([dd_marchas, dd_modo_marchas]),
            ft.Row([dd_pneus, dd_suspensao]),
            ft.Row([dd_freios, dd_aerodinamica_kit]),
            ft.Text("Equilíbrio Aerodinâmico (Velocidade vs Curva):", weight="bold"),
            slider_aero,
            lbl_aero_status,
            ft.Divider(),
            ElevatedButton("Calcular Tunagem Completa", icon="speed", on_click=calcular_tunagem, style=ft.ButtonStyle(color="white", bgcolor="blueAccent")),
            ft.Divider(),
            container_resultados
        ])
    )

    conteudo_garagem = ft.Container(
        padding=10,
        visible=False,
        content=ft.Column([
            ft.Text("🏎️ Minha Garagem de Setups Salvos", size=18, weight="bold"),
            garagem_list_view
        ])
    )

    # Navegação por Botões
    def alternar_aba(e):
        if e.control.data == "calc":
            conteudo_calculadora.visible = True
            conteudo_garagem.visible = False
            btn_aba_calc.style = ft.ButtonStyle(color="white", bgcolor="blueAccent")
            btn_aba_garagem.style = ft.ButtonStyle(color="white", bgcolor="grey800")
        else:
            conteudo_calculadora.visible = False
            conteudo_garagem.visible = True
            btn_aba_calc.style = ft.ButtonStyle(color="white", bgcolor="grey800")
            btn_aba_garagem.style = ft.ButtonStyle(color="white", bgcolor="blueAccent")
        page.update()

    btn_aba_calc = ElevatedButton(
        "Calculadora",
        icon="calculate",
        data="calc",
        on_click=alternar_aba,
        style=ft.ButtonStyle(color="white", bgcolor="blueAccent")
    )

    btn_aba_garagem = ElevatedButton(
        "Garagem",
        icon="directions_car",
        data="garagem",
        on_click=alternar_aba,
        style=ft.ButtonStyle(color="white", bgcolor="grey800")
    )

    barra_navegacao = ft.Row(
        [btn_aba_calc, btn_aba_garagem],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10
    )

    page.add(
        barra_navegacao,
        ft.Divider(),
        conteudo_calculadora,
        conteudo_garagem
    )

if hasattr(ft, "run"):
    ft.run(main)
elif hasattr(ft, "app") and callable(getattr(ft, "app")):
    ft.app(target=main)
