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
    page.title = "Calculadora de Tunagem Forza Horizon 6"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    garagem_list = carregar_garagem()

    # --- CAMPOS DE ENTRADA ---
    txt_nome_carro = ft.TextField(label="Nome do Carro / Projeto", hint_text="Ex: Nissan Skyline GT-R - Drift", icon=ft.icons.DIRECTIONS_CAR)
    
    dropdown_modalidade = ft.Dropdown(
        label="Modalidade de Corrida",
        value="Pista / Asfalto (Grip)",
        options=[
            ft.dropdown.Option("Pista / Asfalto (Grip)"),
            ft.dropdown.Option("Rally / Off-Road"),
            ft.dropdown.Option("Drift"),
            ft.dropdown.Option("Arrancada (Drag)"),
        ],
        icon=ft.icons.SPORTS_SCORE
    )

    dropdown_tracao = ft.Dropdown(
        label="Tipo de Tração",
        value="AWD (4x4)",
        options=[
            ft.dropdown.Option("FWD (Dianteira)"),
            ft.dropdown.Option("RWD (Traseira)"),
            ft.dropdown.Option("AWD (4x4)"),
        ],
        icon=ft.icons.SETTINGS
    )

    input_peso = ft.TextField(label="Peso Total do Carro (kg)", value="1300", keyboard_type=ft.KeyboardType.NUMBER)
    input_dist_peso = ft.TextField(label="Distribuição de Peso (% Dianteira)", value="52", keyboard_type=ft.KeyboardType.NUMBER)
    
    input_pressao_pneus_min = ft.TextField(label="Pressão Mínima dos Pneus (PSI)", value="1.0", keyboard_type=ft.KeyboardType.NUMBER)
    input_pressao_pneus_max = ft.TextField(label="Pressão Máxima dos Pneus (PSI)", value="3.8", keyboard_type=ft.KeyboardType.NUMBER)

    input_mola_min = ft.TextField(label="Mola Mínima (kg/mm)", value="20.0", keyboard_type=ft.KeyboardType.NUMBER)
    input_mola_max = ft.TextField(label="Mola Máxima (kg/mm)", value="180.0", keyboard_type=ft.KeyboardType.NUMBER)

    input_barras_min = ft.TextField(label="Barra Estabilizadora Mínima", value="1.0", keyboard_type=ft.KeyboardType.NUMBER)
    input_barras_max = ft.TextField(label="Barra Estabilizadora Máxima", value="65.0", keyboard_type=ft.KeyboardType.NUMBER)

    input_rebound_min = ft.TextField(label="Retorno/Rebound Mínimo", value="3.0", keyboard_type=ft.KeyboardType.NUMBER)
    input_rebound_max = ft.TextField(label="Retorno/Rebound Máximo", value="20.0", keyboard_type=ft.KeyboardType.NUMBER)

    # Conteúdo do Resultado
    txt_resultado = ft.Column()

    def calcular_tunagem(e):
        try:
            peso = float(input_peso.value)
            dist_dianteira = float(input_dist_peso.value) / 100.0
            dist_traseira = 1.0 - dist_dianteira
            modalidade = dropdown_modalidade.value
            tracao = dropdown_tracao.value

            # Molas
            m_min = float(input_mola_min.value)
            m_max = float(input_mola_max.value)
            mola_dianteira = (m_max - m_min) * dist_dianteira + m_min
            mola_traseira = (m_max - m_min) * dist_traseira + m_min

            # Barras Estabilizadoras (ARBs)
            b_min = float(input_barras_min.value)
            b_max = float(input_barras_max.value)
            arb_dianteira = (b_max - b_min) * dist_dianteira + b_min
            arb_traseira = (b_max - b_min) * dist_traseira + b_min

            # Amortecedores (Rebound & Bump)
            r_min = float(input_rebound_min.value)
            r_max = float(input_rebound_max.value)
            rebound_dianteiro = (r_max - r_min) * dist_dianteira + r_min
            rebound_traseiro = (r_max - r_min) * dist_traseira + r_min

            bump_dianteiro = rebound_dianteiro * 0.6
            bump_traseiro = rebound_traseiro * 0.6

            # Ajustes por Modalidade
            if modalidade == "Drift":
                mola_dianteira *= 1.15
                arb_dianteira *= 1.2
                arb_traseira *= 0.8
                cambagem_diant = "-3.5°"
                cambagem_tras = "-1.0°"
                toe_diant = "0.2° (Toe-out)"
                toe_tras = "0.0°"
                caster = "7.0°"
            elif modalidade == "Rally / Off-Road":
                mola_dianteira *= 0.85
                mola_traseira *= 0.85
                arb_dianteira *= 0.7
                arb_traseira *= 0.7
                cambagem_diant = "-1.5°"
                cambagem_tras = "-1.0°"
                toe_diant = "0.0°"
                toe_tras = "0.0°"
                caster = "5.5°"
            elif modalidade == "Arrancada (Drag)":
                mola_dianteira *= 0.9
                mola_traseira *= 1.3
                arb_dianteira *= 0.5
                arb_traseira *= 1.3
                cambagem_diant = "0.0°"
                cambagem_tras = "0.0°"
                toe_diant = "0.0°"
                toe_tras = "0.0°"
                caster = "5.0°"
            else: # Pista / Grip
                cambagem_diant = "-2.0°"
                cambagem_tras = "-1.5°"
                toe_diant = "0.0°"
                toe_tras = "-0.1°"
                caster = "6.0°"

            # Diferencial
            if tracao == "FWD (Dianteira)":
                dif_txt = "Dianteira: Aceleração 45% | Desaceleração 10%"
            elif tracao == "RWD (Traseira)":
                if modalidade == "Drift":
                    dif_txt = "Traseira: Aceleração 100% | Desaceleração 100%"
                elif modalidade == "Arrancada (Drag)":
                    dif_txt = "Traseira: Aceleração 100% | Desaceleração 0%"
                else:
                    dif_txt = "Traseira: Aceleração 70% | Desaceleração 20%"
            else: # AWD
                if modalidade == "Drift":
                    dif_txt = "Diant: Acel 90%/Desacel 0% | Tras: Acel 100%/Desacel 100% | Torque: 85% Traseira"
                elif modalidade == "Rally / Off-Road":
                    dif_txt = "Diant: Acel 50%/Desacel 0% | Tras: Acel 75%/Desacel 10% | Torque: 60% Traseira"
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

            txt_resultado.controls = [
                ft.Text(f"📊 Setup Calculado: {resultado_dados['nome']}", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.CYAN_200),
                ft.Text(f"Modalidade: {modalidade} | Tração: {tracao}", italic=True),
                ft.Divider(),
                ft.Text(f"🌀 Molas: Dianteira: {resultado_dados['mola_diant']} | Traseira: {resultado_dados['mola_tras']}"),
                ft.Text(f"⚖️ Barras Estabilizadoras: Dianteira: {resultado_dados['arb_diant']} | Traseira: {resultado_dados['arb_tras']}"),
                ft.Text(f"📐 Alinhamento: Cambagem D/T ({cambagem_diant} / {cambagem_tras}) | Toe D/T ({toe_diant} / {toe_tras}) | Caster: {caster}"),
                ft.Text(f"⬆️ Retorno (Rebound): Dianteiro: {resultado_dados['rebound_diant']} | Traseiro: {resultado_dados['rebound_tras']}"),
                ft.Text(f"⬇️ Compressão (Bump): Dianteiro: {resultado_dados['bump_diant']} | Traseiro: {resultado_dados['bump_tras']}"),
                ft.Text(f"⚙️ Diferencial: {dif_txt}"),
                ft.ElevatedButton("💾 Salvar na Garagem", icon=ft.icons.SAVE, on_click=lambda _: salvar_carro_garagem(resultado_dados))
            ]
            page.update()
        except ValueError:
            txt_resultado.controls = [ft.Text("⚠️ Preencha todos os campos numéricos corretamente!", color=ft.colors.RED_400)]
            page.update()

    def salvar_carro_garagem(dados):
        garagem_list.append(dados)
        salvar_garagem(garagem_list)
        atualizar_aba_garagem()
        page.show_snack_bar(ft.SnackBar(ft.Text(f"'{dados['nome']}' salvo na Garagem!")))

    lista_garagem_ui = ft.Column()

    def deletar_carro(item):
        garagem_list.remove(item)
        salvar_garagem(garagem_list)
        atualizar_aba_garagem()
        page.show_snack_bar(ft.SnackBar(ft.Text(f"'{item['nome']}' removido da Garagem.")))

    def atualizar_aba_garagem():
        lista_garagem_ui.controls.clear()
        if not garagem_list:
            lista_garagem_ui.controls.append(ft.Text("Sua garagem está vazia. Calcule uma tunagem e clique em Salvar!", italic=True))
        else:
            for item in garagem_list:
                card = ft.Card(
                    content=ft.Container(
                        padding=15,
                        content=ft.Column([
                            ft.Row([
                                ft.Text(item['nome'], size=18, weight=ft.FontWeight.BOLD, color=ft.colors.YELLOW_400),
                                ft.IconButton(ft.icons.DELETE, icon_color=ft.colors.RED_400, on_click=lambda _, i=item: deletar_carro(i))
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Text(f"Modalidade: {item['modalidade']} ({item['tracao']})", size=12, color=ft.colors.GREY_400),
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

    # ABA CALCULADORA
    aba_calculadora = ft.Container(
        padding=10,
        content=ft.Column([
            txt_nome_carro,
            dropdown_modalidade,
            dropdown_tracao,
            ft.Row([input_peso, input_dist_peso]),
            ft.Text("Limites do Carro (Jogo):", weight=ft.FontWeight.BOLD, color=ft.colors.CYAN_400),
            ft.Row([input_mola_min, input_mola_max]),
            ft.Row([input_barras_min, input_barras_max]),
            ft.Row([input_rebound_min, input_rebound_max]),
            ft.ElevatedButton("⚡ Calcular Tunagem", icon=ft.icons.CALCULATE, on_click=calcular_tunagem, style=ft.ButtonStyle(bgcolor=ft.colors.BLUE_700, color=ft.colors.WHITE)),
            ft.Divider(),
            txt_resultado
        ])
    )

    # ABA GARAGEM
    aba_garagem = ft.Container(
        padding=10,
        content=ft.Column([
            ft.Text("🏎️ Minha Garagem (Salvos)", size=22, weight=ft.FontWeight.BOLD, color=ft.colors.CYAN_200),
            lista_garagem_ui
        ])
    )

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(text="Calculadora", icon=ft.icons.CALCULATE, content=aba_calculadora),
            ft.Tab(text="Garagem", icon=ft.icons.DIRECTIONS_CAR, content=aba_garagem),
        ],
        expand=1,
    )

    page.add(tabs)

ft.app(target=main)
