import flet as ft
import csv
import json
import os

# Compatibilidade de botões para Flet 0.x e Flet 1.0+
ElevatedButton = getattr(ft, "ElevatedButton", getattr(ft, "Button", None))

# Ficheiro para persistência de garagem local
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
    filename = "veiculos.csv"
    if os.path.exists(filename):
        try:
            with open(filename, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    veiculos.append(row)
        except Exception as e:
            print(f"Erro ao carregar CSV: {e}")
    return veiculos

def calcular_marchas(num_marchas, modo="safe"):
    # Tabela de marchas base Safira Spec (6 a 10 marchas)
    tabelas_marchas = {
        6: [2.80, 1.90, 1.40, 1.10, 0.92, 0.78],
        7: [3.15, 2.20, 1.65, 1.30, 1.08, 0.90, 0.78],
        8: [3.40, 2.30, 1.70, 1.35, 1.10, 0.92, 0.78, 0.67],
        9: [3.60, 2.50, 1.85, 1.45, 1.18, 0.98, 0.82, 0.70, 0.58],
        10: [3.80, 2.70, 2.00, 1.60, 1.30, 1.08, 0.90, 0.77, 0.65, 0.55]
    }

    # Transmissões Finais exatas enviadas pelo PapaiZão
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
        # Padrão de segurança para caixas de velocidades menores
        return 3.70, [2.80, 1.90, 1.40, 1.10, 0.92][:num]

def criar_aba(titulo, icone, conteudo):
    try:
        return ft.Tab(label=titulo, icon=icone, content=conteudo)
    except TypeError:
        return ft.Tab(text=titulo, icon=icone, content=conteudo)

def main(page: ft.Page):
    page.title = "Calculadora de Tunagem Forza - Safira Spec"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 15
    page.scroll = ft.ScrollMode.AUTO

    setups_salvos = carregar_garagem()
    ultimo_setup_calculado = {}

    lista_veiculos = carregar_veiculos_csv()

    # Campos do formulário
    txt_nome = ft.TextField(label="Nome / Veículo", hint_text="Ex: Mustang GT 2018", expand=True)
    txt_peso = ft.TextField(label="Peso (kg)", keyboard_type=ft.KeyboardType.NUMBER, value="1500")
    txt_distribuicao = ft.TextField(label="Distribuição Dianteira (%)", keyboard_type=ft.KeyboardType.NUMBER, value="54")
    
    dd_tracao = ft.Dropdown(
        label="Tração",
        options=[
            ft.dropdown.Option("AWD"),
            ft.dropdown.Option("RWD"),
            ft.dropdown.Option("FWD"),
        ],
        value="AWD"
    )

    dd_marchas = ft.Dropdown(
        label="Câmbio (Marchas)",
        options=[
            ft.dropdown.Option("6"),
            ft.dropdown.Option("7"),
            ft.dropdown.Option("8"),
            ft.dropdown.Option("9"),
            ft.dropdown.Option("10"),
        ],
        value="6"
    )

    dd_modo_marchas = ft.Dropdown(
        label="Modo de Escalonamento",
        options=[
            ft.dropdown.Option("Safe"),
            ft.dropdown.Option("Agressivo"),
        ],
        value="Safe"
    )

    slider_aero = ft.Slider(
        min=0,
        max=100,
        divisions=10,
        value=50,
        label="{value}% (Velocidade vs Curva)"
    )

    lbl_aero_status = ft.Text("[ Velocidade | █ █ █ ░ ░ | Curva ]", weight=ft.FontWeight.BOLD, color="cyan")

    def on_aero_change(e):
        val = int(slider_aero.value)
        blocos = int(val / 20)
        vazia = 5 - blocos
        bar = "█ " * blocos + "░ " * vazia
        lbl_aero_status.value = f"[ Velocidade | {bar.strip()} | Curva ] ({val}%)"
        page.update()

    slider_aero.on_change = on_aero_change

    # Seleção rápida via CSV
    def selecionar_veiculo(e):
        if dd_busca_carro.value:
            for v in lista_veiculos:
                nome_completo = f"{v.get('Marca','')} {v.get('Modelo / Ano','')}".strip()
                if nome_completo == dd_busca_carro.value:
                    txt_nome.value = nome_completo
                    p_str = v.get("Peso de Fábrica (kg)", "1500").replace("kg", "").replace(".", "").strip()
                    txt_peso.value = p_str if p_str else "1500"
                    
                    d_str = v.get("Distribuição Dianteira (%)", "54").replace("%", "").strip()
                    txt_distribuicao.value = d_str if d_str else "54"
                    
                    tr = v.get("opção 2", "AWD").upper().strip()
                    if tr in ["AWD", "RWD", "FWD"]:
                        dd_tracao.value = tr
                    page.update()
                    break

    opcoes_carros = []
    for v in lista_veiculos:
        nome_c = f"{v.get('Marca','')} {v.get('Modelo / Ano','')}".strip()
        if nome_c:
            opcoes_carros.append(ft.dropdown.Option(nome_c))

    dd_busca_carro = ft.Dropdown(
        label="Carregar Veículo da Base de Dados (Opcional)",
        options=opcoes_carros,
        expand=True
    )
    dd_busca_carro.on_change = selecionar_veiculo

    # Área de resultados
    container_resultados = ft.Column(spacing=10)

    def calcular_tunagem(e):
        nonlocal ultimo_setup_calculado
        try:
            peso = float(txt_peso.value.replace(",", "."))
            dist_diant = float(txt_distribuicao.value.replace(",", "."))
            tracao = dd_tracao.value
            num_m = int(dd_marchas.value)
            modo_m = dd_modo_marchas.value
            aero_pct = slider_aero.value
        except ValueError:
            page.snack_bar = ft.SnackBar(ft.Text("Por favor, preencha peso e distribuição com números válidos!"))
            page.snack_bar.open = True
            page.update()
            return

        dist_traseira = 100.0 - dist_diant

        # 1. Molas e Pressão dos Pneus
        mola_diant = (dist_diant / 100.0) * (peso * 0.15)
        mola_tras = (dist_traseira / 100.0) * (peso * 0.15)

        # 2. Barras Estabilizadoras (ARBs)
        arb_diant = 1 + (dist_diant / 100.0) * 38.0
        arb_tras = 1 + (dist_traseira / 100.0) * 38.0

        # 3. Amortecimento (Rebound e Bump)
        reb_diant = 0.2 * mola_diant
        reb_tras = 0.2 * mola_tras
        bump_diant = 0.6 * reb_diant
        bump_tras = 0.6 * reb_tras

        # 4. Diferencial por Tração
        if tracao == "AWD":
            diff_str = "Dianteiro: Acel 25% / Desacel 0%\nTraseiro: Acel 75% / Desacel 15%\nTorque Central: 65% Traseira"
        elif tracao == "RWD":
            diff_str = "Aceleração: 45% / Desaceleração: 10%"
        else: # FWD
            diff_str = "Aceleração: 35% / Desaceleração: 0%"

        # 5. Câmbio e Marchas
        final_drive, lista_m = calcular_marchas(num_m, modo_m)

        marchas_txt = f"Transmissão Final: {final_drive:.2f}\n"
        for idx, m_val in enumerate(lista_m, start=1):
            marchas_txt += f" - {idx}ª Marcha: {m_val:.2f}\n"

        # 6. Aerodinâmica
        aero_str = f"Ajuste Geral: {aero_pct:.0f}% (Balanceado conforme preferência)"

        ultimo_setup_calculado = {
            "nome": txt_nome.value if txt_nome.value else "Carro sem nome",
            "peso": peso,
            "distribuicao": dist_diant,
            "tracao": tracao,
            "molas": f"Dianteira: {mola_diant:.1f} kgf/mm | Traseira: {mola_tras:.1f} kgf/mm",
            "arbs": f"Dianteira: {arb_diant:.1f} | Traseira: {arb_tras:.1f}",
            "amortecimento": f"Rebound D/T: {reb_diant:.1f} / {reb_tras:.1f} | Bump D/T: {bump_diant:.1f} / {bump_tras:.1f}",
            "diferencial": diff_str,
            "marchas": marchas_txt.strip(),
            "aerodinamica": aero_str
        }

        container_resultados.controls.clear()
        container_resultados.controls.append(
            ft.Card(
                content=ft.Container(
                    padding=15,
                    content=ft.Column([
                        ft.Text(f"🏁 Setup Calculado: {ultimo_setup_calculado['nome']}", size=18, weight=ft.FontWeight.BOLD, color="greenAccent"),
                        ft.Divider(),
                        ft.Text(f"⚙️ Molas: {ultimo_setup_calculado['molas']}"),
                        ft.Text(f"STB (ARBs): {ultimo_setup_calculado['arbs']}"),
                        ft.Text(f"📉 Amortecedores: {ultimo_setup_calculado['amortecimento']}"),
                        ft.Text(f"🎯 Diferencial ({tracao}):\n{diff_str}"),
                        ft.Text(f"🚦 Escalonamento de Marchas ({num_m} Marchas - {modo_m}):\n{marchas_txt.strip()}"),
                        ft.Text(f"✈️ Aerodinâmica: {aero_str}"),
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
            page.snack_bar = ft.SnackBar(ft.Text("Setup salvo na garagem com sucesso!"))
            page.snack_bar.open = True
            page.update()

    # View da Garagem
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
                            padding=10,
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(f"🚗 {item['nome']}", size=16, weight=ft.FontWeight.BOLD),
                                    ft.IconButton(icon="delete", icon_color="red", on_click=deletar_item)
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Text(f"Molas: {item['molas']}", size=12),
                                ft.Text(f"Marchas:\n{item['marchas']}", size=12),
                            ])
                        )
                    )
                )

    atualizar_view_garagem()

    # Layout com Abas usando a função adaptativa
    tab_calculadora = criar_aba(
        "Calculadora",
        "calculate",
        ft.Container(
            padding=10,
            content=ft.Column([
                ft.Row([dd_busca_carro]),
                ft.Row([txt_nome]),
                ft.Row([txt_peso, txt_distribuicao]),
                ft.Row([dd_tracao, dd_marchas, dd_modo_marchas]),
                ft.Text("Equilíbrio Aerodinâmico:", weight=ft.FontWeight.BOLD),
                slider_aero,
                lbl_aero_status,
                ElevatedButton("Calcular Tunagem", icon="speed", on_click=calcular_tunagem, style=ft.ButtonStyle(color="white", bgcolor="blueAccent")),
                ft.Divider(),
                container_resultados
            ])
        )
    )

    tab_garagem = criar_aba(
        "Garagem",
        "directions_car",
        ft.Container(
            padding=10,
            content=ft.Column([
                ft.Text("🏎️ Minha Garagem de Setups", size=18, weight=ft.FontWeight.BOLD),
                garagem_list_view
            ])
        )
    )

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[tab_calculadora, tab_garagem],
        expand=True
    )

    page.add(tabs)

if hasattr(ft, "run"):
    ft.run(main)
elif hasattr(ft, "app") and callable(getattr(ft, "app")):
    ft.app(target=main)
