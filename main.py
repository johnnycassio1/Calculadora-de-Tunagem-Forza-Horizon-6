import flet as ft
import json
import os

DB_FILE = "garagem_forza.json"

def carregar_garagem():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def salvar_garagem(dados):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

def main(page: ft.Page):
    page.title = "Calculadora de Tunagem Forza - Safira Spec"
    page.window.icon = "icon.png"  # <--- Adicione exatamente essa linha aqui!
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0

    garagem_list = carregar_garagem()

    # --- CAMPOS DE ENTRADA (COLUNA 1: ESQUERDA) ---
    input_nome = ft.TextField(
        label="Nome do Carro / Projeto (Opcional)", 
        hint_text="Ex: Nissan Skyline GT-R",
        bgcolor=ft.Colors.with_opacity(0.7, "#1E1E2E")
    )

    input_peso = ft.TextField(
        label="Peso Total (kg)", 
        value="1350", 
        keyboard_type=ft.KeyboardType.NUMBER,
        bgcolor=ft.Colors.with_opacity(0.7, "#1E1E2E")
    )

    input_potencia = ft.TextField(
        label="Potência (CV/HP)", 
        value="450", 
        keyboard_type=ft.KeyboardType.NUMBER,
        bgcolor=ft.Colors.with_opacity(0.7, "#1E1E2E")
    )

    input_dist_peso = ft.TextField(
        label="Distribuição Dianteira (%)", 
        value="52.00", 
        keyboard_type=ft.KeyboardType.NUMBER,
        bgcolor=ft.Colors.with_opacity(0.7, "#1E1E2E")
    )

    # --- CAMPOS DE ENTRADA (COLUNA 2: DIREITA) ---
    dropdown_modalidade = ft.Dropdown(
        label="Modalidade",
        value="Pista / Asfalto (Grip)",
        bgcolor=ft.Colors.with_opacity(0.8, "#1E1E2E"),
        options=[
            ft.dropdown.Option("Pista / Asfalto (Grip)"),
            ft.dropdown.Option("Corrida de Rua (Street Race)"),
            ft.dropdown.Option("Touge / Serras"),
            ft.dropdown.Option("Rally (Gravel/Dirt)"),
            ft.dropdown.Option("Cross Country"),
            ft.dropdown.Option("Drift"),
            ft.dropdown.Option("Arrancada (Drag)"),
        ]
    )

    dropdown_tracao = ft.Dropdown(
        label="Tração",
        value="RWD (Traseira)",
        bgcolor=ft.Colors.with_opacity(0.8, "#1E1E2E"),
        options=[
            ft.dropdown.Option("FWD (Dianteira)"),
            ft.dropdown.Option("RWD (Traseira)"),
            ft.dropdown.Option("AWD (4x4)"),
        ]
    )

    dropdown_transmissao = ft.Dropdown(
        label="Transmissão",
        value="Corrida (6V)",
        bgcolor=ft.Colors.with_opacity(0.8, "#1E1E2E"),
        options=[
            ft.dropdown.Option("Original"),
            ft.dropdown.Option("Rua"),
            ft.dropdown.Option("Esporte"),
            ft.dropdown.Option("Corrida"),
            ft.dropdown.Option("Corrida (6V)"),
            ft.dropdown.Option("Corrida (7V)"),
            ft.dropdown.Option("Corrida (8V)"),
            ft.dropdown.Option("Corrida (9V)"),
            ft.dropdown.Option("Corrida (10V)"),
        ]
    )

    dropdown_freios = ft.Dropdown(
        label="Freios",
        value="Corrida",
        bgcolor=ft.Colors.with_opacity(0.8, "#1E1E2E"),
        options=[
            ft.dropdown.Option("Original"),
            ft.dropdown.Option("Rua"),
            ft.dropdown.Option("Esportivo"),
            ft.dropdown.Option("Corrida"),
        ]
    )

    dropdown_suspensao = ft.Dropdown(
        label="Suspensão",
        value="Corrida",
        bgcolor=ft.Colors.with_opacity(0.8, "#1E1E2E"),
        options=[
            ft.dropdown.Option("Original"),
            ft.dropdown.Option("Rua"),
            ft.dropdown.Option("Esportiva"),
            ft.dropdown.Option("Corrida"),
            ft.dropdown.Option("Rally"),
            ft.dropdown.Option("Drift"),
        ]
    )

    txt_resultado = ft.Column()

    def calcular_tunagem(e):
        try:
            peso = float(input_peso.value)
            potencia = float(input_potencia.value)
            dist_dianteira = float(input_dist_peso.value) / 100.0
            dist_traseira = 1.0 - dist_dianteira
            modalidade = dropdown_modalidade.value
            tracao = dropdown_tracao.value
            suspensao = dropdown_suspensao.value

            m_min, m_max = peso * 0.015, peso * 0.12
            b_min, b_max = 1.0, 65.0
            r_min, r_max = 3.0, 20.0

            mola_dianteira = (m_max - m_min) * dist_dianteira + m_min
            mola_traseira = (m_max - m_min) * dist_traseira + m_min

            arb_dianteira = (b_max - b_min) * dist_dianteira + b_min
            arb_traseira = (b_max - b_min) * dist_traseira + b_min

            rebound_dianteiro = (r_max - r_min) * dist_dianteira + r_min
            rebound_traseiro = (r_max - r_min) * dist_traseira + r_min

            bump_dianteiro = rebound_dianteiro * 0.6
            bump_traseiro = rebound_traseiro * 0.6

            if modalidade == "Drift" or suspensao == "Drift":
                mola_dianteira *= 1.15
                arb_dianteira *= 1.2
                arb_traseira *= 0.8
                cambagem_diant, cambagem_tras = "-3.5°", "-1.0°"
                toe_diant, toe_tras = "0.2° (Toe-out)", "0.0°"
                caster = "7.0°"
            elif modalidade == "Touge / Serras":
                mola_dianteira *= 1.05
                arb_dianteira *= 1.1
                arb_traseira *= 1.05
                cambagem_diant, cambagem_tras = "-2.5°", "-1.8°"
                toe_diant, toe_tras = "0.1° (Toe-out)", "-0.1°"
                caster = "6.5°"
            elif modalidade in ["Rally (Gravel/Dirt)", "Cross Country"] or suspensao == "Rally":
                mola_dianteira *= 0.85
                mola_traseira *= 0.85
                arb_dianteira *= 0.7
                arb_traseira *= 0.7
                cambagem_diant, cambagem_tras = "-1.5°", "-1.0°"
                toe_diant, toe_tras = "0.0°", "0.0°"
                caster = "5.5°"
            elif modalidade == "Arrancada (Drag)":
                mola_dianteira *= 0.9
                mola_traseira *= 1.3
                arb_dianteira *= 0.5
                arb_traseira *= 1.3
                cambagem_diant, cambagem_tras = "0.0°", "0.0°"
                toe_diant, toe_tras = "0.0°", "0.0°"
                caster = "5.0°"
            else:
                cambagem_diant, cambagem_tras = "-2.0°", "-1.5°"
                toe_diant, toe_tras = "0.0°", "-0.1°"
                caster = "6.0°"

            if tracao == "FWD (Dianteira)":
                dif_txt = "Dianteira: Aceleração 45% | Desaceleração 10%"
            elif tracao == "RWD (Traseira)":
                if modalidade == "Drift":
                    dif_txt = "Traseira: Aceleração 100% | Desaceleração 100%"
                elif modalidade == "Arrancada (Drag)":
                    dif_txt = "Traseira: Aceleração 100% | Desaceleração 0%"
                else:
                    dif_txt = "Traseira: Aceleração 70% | Desaceleração 20%"
            else:
                if modalidade == "Drift":
                    dif_txt = "Diant: Acel 90%/Desacel 0% | Tras: Acel 100%/Desacel 100% | Torque: 85% Traseira"
                elif modalidade in ["Rally (Gravel/Dirt)", "Cross Country"]:
                    dif_txt = "Diant: Acel 50%/Desacel 0% | Tras: Acel 75%/Desacel 10% | Torque: 60% Traseira"
                else:
                    dif_txt = "Diant: Acel 50%/Desacel 0% | Tras: Acel 70%/Desacel 20% | Torque: 65% Traseira"

            relacao_peso_potencia = peso / potencia if potencia > 0 else 0

            resultado_dados = {
                "nome": input_nome.value if input_nome.value else f"Carro {peso}kg",
                "modalidade": modalidade,
                "tracao": tracao,
                "peso_potencia": f"{relacao_peso_potencia:.2f} kg/CV",
                "mola_diant": f"{mola_dianteira:.1f} kg/mm",
                "mola_tras": f"{mola_traseira:.1f} kg/mm",
                "arb_diant": f"{arb_dianteira:.1f}",
                "arb_tras": f"{arb_traseira:.1f}",
                "rebound_diant": f"{rebound_dianteiro:.1f}",
                "rebound_tras": f"{rebound_traseiro:.1f}",
                "bump_diant": f"{bump_dianteiro:.1f}",
                "bump_tras": f"{bump_traseiro:.1f}",
                "cambagem_diant": cambagem_diant,
                "cambagem_tras": cambagem_tras,
                "toe_diant": toe_diant,
                "toe_tras": toe_tras,
                "caster": caster,
                "diferencial": dif_txt
            }

            cor_titulo = getattr(ft.Colors, "CYAN_200", "cyan")
            txt_resultado.controls = [
                ft.Text(f"📊 Setup Calculado: {resultado_dados['nome']}", size=18, weight=ft.FontWeight.BOLD, color=cor_titulo),
                ft.Text(f"Relação Peso/Potência: {resultado_dados['peso_potencia']} | Tração: {tracao}", italic=True),
                ft.Divider(),
                ft.Text(f"🌀 Molas: Dianteira: {resultado_dados['mola_diant']} | Traseira: {resultado_dados['mola_tras']}"),
                ft.Text(f"⚖️ Barras Estabilizadoras: Dianteira: {resultado_dados['arb_diant']} | Traseira: {resultado_dados['arb_tras']}"),
                ft.Text(f"📐 Alinhamento: Cambagem ({cambagem_diant} / {cambagem_tras}) | Toe ({toe_diant} / {toe_tras}) | Caster: {caster}"),
                ft.Text(f"⬆️ Retorno (Rebound): D: {resultado_dados['rebound_diant']} | T: {resultado_dados['rebound_tras']}"),
                ft.Text(f"⬇️ Compressão (Bump): D: {resultado_dados['bump_diant']} | T: {resultado_dados['bump_tras']}"),
                ft.Text(f"⚙️ Diferencial: {dif_txt}"),
                ft.ElevatedButton("💾 Salvar na Garagem", on_click=lambda _: salvar_carro_garagem(resultado_dados))
            ]
            page.update()
        except ValueError:
            cor_erro = getattr(ft.Colors, "RED_400", "red")
            txt_resultado.controls = [ft.Text("⚠️ Digite os valores de Peso e Potência corretamente!", color=cor_erro)]
            page.update()

    def salvar_carro_garagem(dados):
        garagem_list.append(dados)
        salvar_garagem(garagem_list)
        atualizar_aba_garagem()
        page.update()

    lista_garagem_ui = ft.Column()

    def deletar_carro(item):
        garagem_list.remove(item)
        salvar_garagem(garagem_list)
        atualizar_aba_garagem()

    def atualizar_aba_garagem():
        lista_garagem_ui.controls.clear()
        if not garagem_list:
            lista_garagem_ui.controls.append(ft.Text("Sua garagem está vazia.", italic=True))
        else:
            cor_amarelo = getattr(ft.Colors, "YELLOW_400", "yellow")
            cor_cinza = getattr(ft.Colors, "GREY_400", "grey")
            cor_vermelho = getattr(ft.Colors, "RED_400", "red")
            for item in garagem_list:
                card = ft.Card(
                    color=ft.Colors.with_opacity(0.85, "black"),
                    content=ft.Container(
                        padding=15,
                        content=ft.Column([
                            ft.Row([
                                ft.Text(item['nome'], size=16, weight=ft.FontWeight.BOLD, color=cor_amarelo),
                                ft.IconButton(icon="delete", icon_color=cor_vermelho, on_click=lambda _, i=item: deletar_carro(i))
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Text(f"{item['modalidade']} ({item['tracao']}) - {item['peso_potencia']}", size=12, color=cor_cinza),
                            ft.Divider(),
                            ft.Text(f"Molas: D {item['mola_diant']} / T {item['mola_tras']}"),
                            ft.Text(f"Barras: D {item['arb_diant']} / T {item['arb_tras']}"),
                            ft.Text(f"Diferencial: {item['diferencial']}", size=11, italic=True)
                        ])
                    )
                )
                lista_garagem_ui.controls.append(card)
        page.update()

    atualizar_aba_garagem()

    # --- LAYOUT EM DUAS COLUNAS ---
    coluna_esquerda = ft.Column([
        input_peso,
        input_potencia,
        input_dist_peso,
        dropdown_modalidade,
    ], expand=True)

    coluna_direita = ft.Column([
        dropdown_tracao,
        dropdown_transmissao,
        dropdown_freios,
        dropdown_suspensao,
    ], expand=True)

    btn_calcular = ft.Container(
        content=ft.ElevatedButton(
            "⚡ CALCULAR TUNAGEM", 
            on_click=calcular_tunagem,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor="#FF4B4B",
                padding=15
            )
        ),
        alignment=ft.Alignment(0, 0),
        margin=ft.Margin(0, 15, 0, 15)
    )

    aba_calculadora = ft.Container(
        padding=10,
        content=ft.Column([
            ft.Text("🏎️ Calculadora de Tunagem Forza", size=20, weight=ft.FontWeight.BOLD),
            ft.Text("Ajustes precisos de performance para o seu carro", size=12, italic=True, color=getattr(ft.Colors, "GREY_400", "grey")),
            ft.Divider(),
            input_nome,
            ft.Text("📋 Dados do Veículo", size=15, weight=ft.FontWeight.BOLD),
            ft.Row([coluna_esquerda, coluna_direita], spacing=10, alignment=ft.MainAxisAlignment.START),
            btn_calcular,
            ft.Divider(),
            txt_resultado
        ])
    )

    aba_garagem = ft.Container(
        padding=10,
        visible=False,
        content=ft.Column([
            ft.Text("🏎️ Minha Garagem (Salvos)", size=20, weight=ft.FontWeight.BOLD, color=getattr(ft.Colors, "CYAN_200", "cyan")),
            lista_garagem_ui
        ])
    )

    def alternar_aba(nome_aba):
        if nome_aba == "calculadora":
            aba_calculadora.visible = True
            aba_garagem.visible = False
            btn_calc.style = ft.ButtonStyle(color=getattr(ft.Colors, "CYAN_400", "cyan"))
            btn_garagem.style = ft.ButtonStyle(color=getattr(ft.Colors, "WHITE", "white"))
        else:
            aba_calculadora.visible = False
            aba_garagem.visible = True
            btn_calc.style = ft.ButtonStyle(color=getattr(ft.Colors, "WHITE", "white"))
            btn_garagem.style = ft.ButtonStyle(color=getattr(ft.Colors, "CYAN_400", "cyan"))
        page.update()

    btn_calc = ft.TextButton("⚡ Calculadora", on_click=lambda _: alternar_aba("calculadora"), style=ft.ButtonStyle(color=getattr(ft.Colors, "CYAN_400", "cyan")))
    btn_garagem = ft.TextButton("🏎️ Garagem", on_click=lambda _: alternar_aba("garagem"))

    menu_navegacao = ft.Row([btn_calc, btn_garagem], alignment=ft.MainAxisAlignment.CENTER)

    conteudo_principal = ft.Container(
        padding=10,
        margin=5,
        bgcolor=ft.Colors.with_opacity(0.88, "#121214"),
        border_radius=15,
        content=ft.Column([
            menu_navegacao,
            ft.Divider(),
            aba_calculadora,
            aba_garagem
        ], scroll=ft.ScrollMode.AUTO)
    )

    page.add(conteudo_principal)

ft.app(target=main)
