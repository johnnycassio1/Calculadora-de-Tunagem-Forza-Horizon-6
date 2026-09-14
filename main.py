import flet as ft
import json
import os

DB_FILE = "garagem_forza.json"

# CAMINHO AUTOMÁTICO DA IMAGEM
URL_IMAGEM_FUNDO = os.path.join(os.path.dirname(__file__), "fundo_fh6.jpg")

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
    page.title = "Calculadora de Tunagem Forza Horizon - Safira Spec"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0

    garagem_list = carregar_garagem()

    # --- CAMPOS DE ENTRADA ---
    txt_nome_carro = ft.TextField(
        label="Nome do Carro / Projeto", 
        hint_text="Ex: Skyline GT-R - Touge",
        bgcolor=ft.Colors.with_opacity(0.7, "black")
    )
    
    dropdown_modalidade = ft.Dropdown(
        label="Modalidade de Corrida",
        value="Pista / Asfalto (Grip)",
        bgcolor=ft.Colors.with_opacity(0.8, "black"),
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
        label="Tipo de Tração",
        value="AWD (4x4)",
        bgcolor=ft.Colors.with_opacity(0.8, "black"),
        options=[
            ft.dropdown.Option("FWD (Dianteira)"),
            ft.dropdown.Option("RWD (Traseira)"),
            ft.dropdown.Option("AWD (4x4)"),
        ]
    )

    input_peso = ft.TextField(label="Peso Total (kg)", value="1300", keyboard_type=ft.KeyboardType.NUMBER, bgcolor=ft.Colors.with_opacity(0.7, "black"), expand=True)
    input_dist_peso = ft.TextField(label="Distribuição (% Diant)", value="52", keyboard_type=ft.KeyboardType.NUMBER, bgcolor=ft.Colors.with_opacity(0.7, "black"), expand=True)

    input_mola_min = ft.TextField(label="Mola Min", value="20.0", keyboard_type=ft.KeyboardType.NUMBER, bgcolor=ft.Colors.with_opacity(0.7, "black"), expand=True)
    input_mola_max = ft.TextField(label="Mola Max", value="180.0", keyboard_type=ft.KeyboardType.NUMBER, bgcolor=ft.Colors.with_opacity(0.7, "black"), expand=True)

    input_barras_min = ft.TextField(label="Barra Min", value="1.0", keyboard_type=ft.KeyboardType.NUMBER, bgcolor=ft.Colors.with_opacity(0.7, "black"), expand=True)
    input_barras_max = ft.TextField(label="Barra Max", value="65.0", keyboard_type=ft.KeyboardType.NUMBER, bgcolor=ft.Colors.with_opacity(0.7, "black"), expand=True)

    input_rebound_min = ft.TextField(label="Rebound Min", value="3.0", keyboard_type=ft.KeyboardType.NUMBER, bgcolor=ft.Colors.with_opacity(0.7, "black"), expand=True)
    input_rebound_max = ft.TextField(label="Rebound Max", value="20.0", keyboard_type=ft.KeyboardType.NUMBER, bgcolor=ft.Colors.with_opacity(0.7, "black"), expand=True)

    txt_resultado = ft.Column()

    def calcular_tunagem(e):
        try:
            peso = float(input_peso.value)
            dist_dianteira = float(input_dist_peso.value) / 100.0
            dist_traseira = 1.0 - dist_dianteira
            modalidade = dropdown_modalidade.value
            tracao = dropdown_tracao.value

            m_min, m_max = float(input_mola_min.value), float(input_mola_max.value)
            mola_dianteira = (m_max - m_min) * dist_dianteira + m_min
            mola_traseira = (m_max - m_min) * dist_traseira + m_min

            b_min, b_max = float(input_barras_min.value), float(input_barras_max.value)
            arb_dianteira = (b_max - b_min) * dist_dianteira + b_min
            arb_traseira = (b_max - b_min) * dist_traseira + b_min

            r_min, r_max = float(input_rebound_min.value), float(input_rebound_max.value)
            rebound_dianteiro = (r_max - r_min) * dist_dianteira + r_min
            rebound_traseiro = (r_max - r_min) * dist_traseira + r_min

            bump_dianteiro = rebound_dianteiro * 0.6
            bump_traseiro = rebound_traseiro * 0.6

            if modalidade == "Drift":
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
            elif modalidade == "Rally (Gravel/Dirt)":
                mola_dianteira *= 0.85
                mola_traseira *= 0.85
                arb_dianteira *= 0.7
                arb_traseira *= 0.7
                cambagem_diant, cambagem_tras = "-1.5°", "-1.0°"
                toe_diant, toe_tras = "0.0°", "0.0°"
                caster = "5.5°"
            elif modalidade == "Cross Country":
                mola_dianteira *= 0.95
                mola_traseira *= 0.95
                arb_dianteira *= 0.6
                arb_traseira *= 0.6
                bump_dianteiro *= 1.2
                bump_traseiro *= 1.2
                cambagem_diant, cambagem_tras = "-1.0°", "-0.8°"
                toe_diant, toe_tras = "0.0°", "0.0°"
                caster = "5.0°"
            elif modalidade == "Arrancada (Drag)":
                mola_dianteira *= 0.9
                mola_traseira *= 1.3
                arb_dianteira *= 0.5
                arb_traseira *= 1.3
                cambagem_diant, cambagem_tras = "0.0°", "0.0°"
                toe_diant, toe_tras = "0.0°", "0.0°"
                caster = "5.0°"
            elif modalidade == "Corrida de Rua (Street Race)":
                mola_dianteira *= 0.98
                mola_traseira *= 0.98
                cambagem_diant, cambagem_tras = "-2.2°", "-1.6°"
                toe_diant, toe_tras = "-0.1°", "-0.1°"
                caster = "6.0°"
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
                elif modalidade == "Touge / Serras":
                    dif_txt = "Diant: Acel 40%/Desacel 0% | Tras: Acel 80%/Desacel 15% | Torque: 70% Traseira"
                else:
                    dif_txt = "Diant: Acel 50%/Desacel 0% | Tras: Acel 70%/Desacel 20% | Torque: 65% Traseira"

            resultado_dados = {
                "nome": txt_nome_carro.value if txt_nome_carro.value else "Carro sem nome",
                "modalidade": modalidade,
                "tracao": tracao,
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
                ft.Text(f"📊 Setup Calculado: {resultado_dados['nome']}", size=20, weight=ft.FontWeight.BOLD, color=cor_titulo),
                ft.Text(f"Modalidade: {modalidade} | Tração: {tracao}", italic=True),
                ft.Divider(),
                ft.Text(f"🌀 Molas: Dianteira: {resultado_dados['mola_diant']} | Traseira: {resultado_dados['mola_tras']}"),
                ft.Text(f"⚖️ Barras Estabilizadoras: Dianteira: {resultado_dados['arb_diant']} | Traseira: {resultado_dados['arb_tras']}"),
                ft.Text(f"📐 Alinhamento: Cambagem D/T ({cambagem_diant} / {cambagem_tras}) | Toe D/T ({toe_diant} / {toe_tras}) | Caster: {caster}"),
                ft.Text(f"⬆️ Retorno (Rebound): Dianteiro: {resultado_dados['rebound_diant']} | Traseiro: {resultado_dados['rebound_tras']}"),
                ft.Text(f"⬇️ Compressão (Bump): Dianteiro: {resultado_dados['bump_diant']} | Traseiro: {resultado_dados['bump_tras']}"),
                ft.Text(f"⚙️ Diferencial: {dif_txt}"),
                ft.ElevatedButton("💾 Salvar na Garagem", on_click=lambda _: salvar_carro_garagem(resultado_dados))
            ]
            page.update()
        except ValueError:
            cor_erro = getattr(ft.Colors, "RED_400", "red")
            txt_resultado.controls = [ft.Text("⚠️ Preencha todos os campos numéricos corretamente!", color=cor_erro)]
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
            lista_garagem_ui.controls.append(ft.Text("Sua garagem está vazia. Calcule uma tunagem e clique em Salvar!", italic=True))
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
                                ft.Text(item['nome'], size=18, weight=ft.FontWeight.BOLD, color=cor_amarelo),
                                ft.IconButton(icon="delete", icon_color=cor_vermelho, on_click=lambda _, i=item: deletar_carro(i))
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Text(f"Modalidade: {item['modalidade']} ({item['tracao']})", size=12, color=cor_cinza),
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

    aba_calculadora = ft.Container(
        padding=15,
        content=ft.Column([
            txt_nome_carro,
            dropdown_modalidade,
            dropdown_tracao,
            ft.Row([input_peso, input_dist_peso]),
            ft.Text("Limites do Carro (Jogo):", weight=ft.FontWeight.BOLD, color=getattr(ft.Colors, "CYAN_400", "cyan")),
            ft.Row([input_mola_min, input_mola_max]),
            ft.Row([input_barras_min, input_barras_max]),
            ft.Row([input_rebound_min, input_rebound_max]),
            ft.ElevatedButton("⚡ Calcular Tunagem", on_click=calcular_tunagem),
            ft.Divider(),
            txt_resultado
        ])
    )

    aba_garagem = ft.Container(
        padding=15,
        visible=False,
        content=ft.Column([
            ft.Text("🏎️ Minha Garagem (Salvos)", size=22, weight=ft.FontWeight.BOLD, color=getattr(ft.Colors, "CYAN_200", "cyan")),
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
        padding=20,
        margin=15,
        bgcolor=ft.Colors.with_opacity(0.85, "#121212"),
        border_radius=15,
        content=ft.Column([
            menu_navegacao,
            ft.Divider(),
            aba_calculadora,
            aba_garagem
        ], scroll=ft.ScrollMode.AUTO)
    )

    layout_fundo = ft.Stack([
        ft.Image(
            src=URL_IMAGEM_FUNDO,
            fit="cover",
            expand=True,
            width=page.width,
            height=page.height
        ),
        conteudo_principal
    ], expand=True)

    page.add(layout_fundo)

ft.app(target=main, assets_dir=".")
