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
    filenames = ["veiculos.csv", "veiculos_fh6.csv", "dados_carros.csv"]
    for filename in filenames:
        if os.path.exists(filename):
            for encoding in ["utf-8-sig", "utf-8", "latin1"]:
                try:
                    with open(filename, mode="r", encoding=encoding) as f:
                        content = f.read()
                        if not content.strip():
                            continue
                        delimiter = ";" if ";" in content.splitlines()[0] else ","
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

def calcular_marchas(num_marchas, modo="safe"):
    # Tabela de marchas base Safira Spec (6 a 10 marchas)
    tabelas_marchas = {
        6: [2.80, 1.90, 1.40, 1.10, 0.92, 0.78],
        7: [3.15, 2.20, 1.65, 1.30, 1.08, 0.90, 0.78],
        8: [3.40, 2.30, 1.70, 1.35, 1.10, 0.92, 0.78, 0.67],
        9: [3.60, 2.50, 1.85, 1.45, 1.18, 0.98, 0.82, 0.70, 0.58],
        10: [3.80, 2.70, 2.00, 1.60, 1.30, 1.08, 0.90, 0.77, 0.65, 0.55]
    }

    # Transmissões Finais exatas do PapaiZão
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

    # Notificação segura
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

    # Campos do Formulário
    txt_nome = ft.TextField(label="Nome / Veículo", hint_text="Ex: Mustang GT 2018", expand=True)
    txt_peso = ft.TextField(label="Peso (kg)", keyboard_type=ft.KeyboardType.NUMBER, value="1500", expand=True)
    txt_potencia = ft.TextField(label="Potência (CV/HP)", keyboard_type=ft.KeyboardType.NUMBER, value="450", expand=True)
    txt_distribuicao = ft.TextField(label="Distribuição Dianteira (%)", keyboard_type=ft.KeyboardType.NUMBER, value="54", expand=True)
    
    dd_tracao = ft.Dropdown(
        label="Tração",
        options=[
            ft.dropdown.Option("AWD"),
            ft.dropdown.Option("RWD"),
            ft.dropdown.Option("FWD"),
        ],
        value="AWD",
        expand=True
    )

    dd_pneus = ft.Dropdown(
        label="Composto de Pneus",
        options=[
            ft.dropdown.Option("Corrida / Slick"),
            ft.dropdown.Option("Rali / Offroad"),
            ft.dropdown.Option("Semi-Slick"),
            ft.dropdown.Option("Rua"),
            ft.dropdown.Option("Original"),
        ],
        value="Corrida / Slick",
        expand=True
    )

    dd_suspensao = ft.Dropdown(
        label="Molas / Suspensão",
        options=[
            ft.dropdown.Option("Corrida / Pista"),
            ft.dropdown.Option("Rali"),
            ft.dropdown.Option("Offroad"),
            ft.dropdown.Option("Drift"),
        ],
        value="Corrida / Pista",
        expand=True
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
        value="6",
        expand=True
    )

    dd_modo_marchas = ft.Dropdown(
        label="Modo de Escalonamento",
        options=[
            ft.dropdown.Option("Safe"),
            ft.dropdown.Option("Agressivo"),
        ],
        value="Safe",
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

    # Preenchimento Automático via CSV
    opcoes_carros = []
    for v in lista_veiculos:
        marca = v.get("Marca", "") or v.get("MARCA", "")
        modelo = v.get("Modelo / Ano", "") or v.get("Nome do Carro", "") or v.get("MODELO", "")
        nome_c = f"{marca} {modelo}".strip()
        if nome_c and nome_c not in [opt.key for opt in opcoes_carros]:
            opcoes_carros.append(ft.dropdown.Option(key=nome_c, text=nome_c))

    def selecionar_veiculo(e):
        if dd_busca_carro.value:
            for v in lista_veiculos:
                marca = v.get("Marca", "") or v.get("MARCA", "")
                modelo = v.get("Modelo / Ano", "") or v.get("Nome do Carro", "") or v.get("MODELO", "")
                nome_completo = f"{marca} {modelo}".strip()
                
                if nome_completo == dd_busca_carro.value:
                    txt_nome.value = nome_completo
                    
                    # Peso
                    p_str = v.get("Peso de Fábrica (kg)", "") or v.get("Peso", "")
                    p_str = p_str.replace("kg", "").replace(".", "").replace(",", "").strip()
                    if p_str:
                        txt_peso.value = p_str
                    
                    # Potência
                    pot_str = v.get("Potência de Fábrica (CV/HP)", "") or v.get("Potência", "") or v.get("Potencia", "")
                    pot_str = pot_str.lower().replace("cv", "").replace("hp", "").replace(".", "").replace(",", "").strip()
                    if pot_str:
                        txt_potencia.value = pot_str

                    # Distribuição
                    d_str = v.get("Distribuição Dianteira (%)", "") or v.get("Distribuição", "") or v.get("Distribuiçao", "")
                    d_str = d_str.replace("%", "").replace(",", ".").strip()
                    if d_str:
                        txt_distribuicao.value = d_str
                    
                    # Tração
                    tr = (v.get("opção 2", "") or v.get("Tração", "") or v.get("Tracao", "")).upper().strip()
                    if tr in ["AWD", "RWD", "FWD"]:
                        dd_tracao.value = tr
                    
                    page.update()
                    break

    dd_busca_carro = ft.Dropdown(
        label="Carregar Veículo da Base de Dados (Opcional)",
        options=opcoes_carros,
        expand=True
    )
    dd_busca_carro.on_change = selecionar_veiculo

    # Área de Resultados
    container_resultados = ft.Column(spacing=10)

    def calcular_tunagem(e):
        nonlocal ultimo_setup_calculado
        try:
            peso = float(txt_peso.value.replace(",", "."))
            potencia = float(txt_potencia.value.replace(",", "."))
            dist_diant = float(txt_distribuicao.value.replace(",", "."))
            tracao = dd_tracao.value
            pneu_tipo = dd_pneus.value
            susp_tipo = dd_suspensao.value
            num_m = int(dd_marchas.value)
            modo_m = dd_modo_marchas.value
            aero_pct = slider_aero.value
        except ValueError:
            mostrar_snack("Por favor, preencha peso, potência e distribuição com números válidos!")
            return

        dist_traseira = 100.0 - dist_diant

        # 1. Pressão dos Pneus
        if "Rali" in pneu_tipo or "Offroad" in pneu_tipo:
            pneu_d, pneu_t = 1.7, 1.7  # bar
        elif "Rua" in pneu_tipo or "Original" in pneu_tipo:
            pneu_d, pneu_t = 2.1, 2.0
        else:  # Slick / Corrida / Semi-Slick
            pneu_d, pneu_t = 1.9, 1.9

        pneu_d_psi, pneu_t_psi = round(pneu_d * 14.5038, 1), round(pneu_t * 14.5038, 1)

        # 2. Alinhamento
        if "Rali" in susp_tipo or "Offroad" in susp_tipo:
            camber_d, camber_t = -1.0, -0.5
            toe_d, toe_t = 0.0, 0.0
            caster = 6.0
        elif "Drift" in susp_tipo:
            camber_d, camber_t = -3.0, -1.0
            toe_d, toe_t = 0.2, -0.1
            caster = 7.0
        else:  # Corrida / Pista
            camber_d, camber_t = -1.5, -1.0
            toe_d, toe_t = 0.0, 0.0
            caster = 6.0

        # 3. Barras Estabilizadoras (ARBs / STB)
        arb_diant = round(1.0 + (dist_diant / 100.0) * 64.0, 1)
        arb_tras = round(1.0 + (dist_traseira / 100.0) * 64.0, 1)

        # 4. Molas e Altura
        mola_diant = round((dist_diant / 100.0) * (peso * 0.15), 1)
        mola_tras = round((dist_traseira / 100.0) * (peso * 0.15), 1)
        altura_str = "Elevada (Máximo Aderência)" if "Rali" in susp_tipo or "Offroad" in susp_tipo else "Mínima / Pista"

        # 5. Amortecedores (Rebound e Bump)
        reb_diant = round(min(20.0, max(1.0, 0.2 * mola_diant)), 1)
        reb_tras = round(min(20.0, max(1.0, 0.2 * mola_tras)), 1)
        bump_diant = round(0.6 * reb_diant, 1)
        bump_tras = round(0.6 * reb_tras, 1)

        # 6. Aerodinâmica (Downforce em kgf)
        aero_d_kgf = round(75 + (aero_pct / 100.0) * 125)
        aero_t_kgf = round(100 + (aero_pct / 100.0) * 180)

        # 7. Freios
        freio_str = "Balanço: 50% Dianteira | Pressão: 100%"

        # 8. Diferencial por Tração (Safira Spec)
        if tracao == "AWD":
            diff_str = "Dianteiro: Acel 25% / Desacel 0%\nTraseiro: Acel 75% / Desacel 15%\nTorque Central: 65% Traseira"
        elif tracao == "RWD":
            diff_str = "Aceleração: 45% / Desaceleração: 10%"
        else:  # FWD
            diff_str = "Aceleração: 35% / Desaceleração: 0%"

        # 9. Câmbio e Marchas (Safira Spec)
        final_drive, lista_m = calcular_marchas(num_m, modo_m)

        marchas_txt = f"Transmissão Final: {final_drive:.2f}\n"
        for idx, m_val in enumerate(lista_m, start=1):
            marchas_txt += f" - {idx}ª Marcha: {m_val:.2f}\n"

        ultimo_setup_calculado = {
            "nome": txt_nome.value if txt_nome.value else "Carro sem nome",
            "peso": peso,
            "potencia": potencia,
            "distribuicao": dist_diant,
            "tracao": tracao,
            "pneus_info": f"Dianteiro: {pneu_d:.1f} bar ({pneu_d_psi} psi) | Traseiro: {pneu_t:.1f} bar ({pneu_t_psi} psi) - [{pneu_tipo}]",
            "alinhamento": f"Cambagem D/T: {camber_d}° / {camber_t}° | Toe D/T: {toe_d}° / {toe_t}° | Caster: {caster}°",
            "arbs": f"Dianteira: {arb_diant} | Traseira: {arb_tras}",
            "molas": f"Dianteira: {mola_diant} kgf/mm | Traseira: {mola_tras} kgf/mm | Altura: {altura_str}",
            "amortecimento": f"Rebound D/T: {reb_diant} / {reb_tras} | Bump D/T: {bump_diant} / {bump_tras}",
            "aerodinamica": f"Downforce D/T: {aero_d_kgf} kgf / {aero_t_kgf} kgf ({aero_pct:.0f}% Equilíbrio)",
            "freios": freio_str,
            "diferencial": diff_str,
            "marchas": marchas_txt.strip()
        }

        container_resultados.controls.clear()
        container_resultados.controls.append(
            ft.Card(
                content=ft.Container(
                    padding=15,
                    content=ft.Column([
                        ft.Text(f"🏁 Setup Calculado: {ultimo_setup_calculado['nome']}", size=18, weight="bold", color="greenAccent"),
                        ft.Text(f"📊 {peso:.0f} kg | {potencia:.0f} CV | {dist_diant:.0f}% Dianteira | Tração {tracao}", size=13, color="white70"),
                        ft.Divider(),
                        ft.Text(f"🛞 Pneus: {ultimo_setup_calculado['pneus_info']}"),
                        ft.Text(f"📐 Alinhamento: {ultimo_setup_calculado['alinhamento']}"),
                        ft.Text(f"⚖️ STB (ARBs): {ultimo_setup_calculado['arbs']}"),
                        ft.Text(f"⚙️ Molas: {ultimo_setup_calculado['molas']}"),
                        ft.Text(f"📉 Amortecedores: {ultimo_setup_calculado['amortecimento']}"),
                        ft.Text(f"✈️ Aerodinâmica: {ultimo_setup_calculado['aerodinamica']}"),
                        ft.Text(f"🛑 Freios: {ultimo_setup_calculado['freios']}"),
                        ft.Text(f"🎯 Diferencial ({tracao}):\n{diff_str}"),
                        ft.Text(f"🚦 Câmbio ({num_m} Marchas - {modo_m}):\n{marchas_txt.strip()}"),
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
            mostrar_snack("Setup salvo na garagem com sucesso!")

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
                            padding=12,
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(f"🚗 {item['nome']}", size=16, weight="bold"),
                                    ft.IconButton(
                                        icon=getattr(ft.Icons, "DELETE_OUTLINED", getattr(ft.Icons, "DELETE", None)),
                                        icon_color="red",
                                        tooltip="Excluir",
                                        on_click=deletar_item
                                    )
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Text(f"Molas: {item['molas']}", size=12),
                                ft.Text(f"Amortecedores: {item['amortecimento']}", size=12),
                                ft.Text(f"Marchas:\n{item['marchas']}", size=12),
                            ])
                        )
                    )
                )

    atualizar_view_garagem()

    # Conteúdo das Vistas
    conteudo_calculadora = ft.Container(
        padding=10,
        content=ft.Column([
            ft.Row([dd_busca_carro]),
            ft.Row([txt_nome]),
            ft.Row([txt_peso, txt_potencia, txt_distribuicao]),
            ft.Row([dd_tracao, dd_pneus, dd_suspensao]),
            ft.Row([dd_marchas, dd_modo_marchas]),
            ft.Text("Equilíbrio Aerodinâmico:", weight="bold"),
            slider_aero,
            lbl_aero_status,
            ElevatedButton("Calcular Tunagem", icon="speed", on_click=calcular_tunagem, style=ft.ButtonStyle(color="white", bgcolor="blueAccent")),
            ft.Divider(),
            container_resultados
        ])
    )

    conteudo_garagem = ft.Container(
        padding=10,
        visible=False,
        content=ft.Column([
            ft.Text("🏎️ Minha Garagem de Setups", size=18, weight="bold"),
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
