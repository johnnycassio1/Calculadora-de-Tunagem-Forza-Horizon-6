import flet as ft
import os
import sqlite3
import csv
import io
import re

# ---------------------------------------------------------
# CAMINHOS & DADOS EMBUTIDOS EM MEMÓRIA (FALLBACK PARA APK)
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "veiculos.db")
CSV_PATH = os.path.join(BASE_DIR, "veiculos.csv")

# Base de dados embutida diretamente no código para garantir que o APK carregue offline
DADOS_CSV_EMBUTIDOS = """Marca,Modelo / Ano,Classe & IP Original,Peso de Fábrica (kg),Potência de Fábrica (CV/HP),Distribuição Dianteira (%),Tração
Abarth,Abarth Fiat 131 de 1980,D 399,1010,140 cv,53%,RWD
Abarth,Abarth 695 Biposto 2016,B 540,997,190 cv,64%,FWD
Abarth,Abarth 124 Spider 2017,C 450,1060,170 cv,51%,RWD
Abarth,1968 Abarth 595 esseesse,D 100,535,32 cv,38%,RWD
Acura,Acura RSX Type S 2002,C 462,1256,200 cv,61%,FWD
Acura,Acura NSX Tipo S 2022,S1 734,1754,600 cv,42%,AWD
Acura,Acura Integra Type R 2001,C 471,1180,195 cv,62%,FWD
Acura,Acura Integra A-Spec 2023,C 484,1394,200 cv,60%,FWD
Alfa Romeo,Alfa Romeo SE 048SP de 1990,R 978,820,600 cv,43%,RWD
Alfa Romeo,Alfa Romeo Giulia TZ2 de 1965,B 532,620,170 cv,48%,RWD
Alfa Romeo,Alfa Romeo Giulia Sprint GTA Stradale 1965,D 379,740,113 cv,53%,RWD
Alfa Romeo,Alfa Romeo Giulia Quadrifoglio 2017,A 667,1580,505 cv,53%,RWD
Alfa Romeo,Alfa Romeo Giulia GTAm 2021,S1 711,1520,532 cv,50%,RWD
Alfa Romeo,Alfa Romeo Autodelta Tipo 33/2 Daytona 1968,A 696,580,270 cv,42%,RWD
Alfa Romeo,Alfa Romeo 4C 2014,A 644,1020,237 cv,41%,RWD
Alfa Romeo,Alfa Romeo 33 Stradale 1968,B 593,700,230 cv,48%,RWD
Alfa Romeo,Alfa Romeo 155 Q4 de 1992,C 439,1370,187 cv,60%,AWD
Alfa Romeo,2007 Alfa Romeo 8C Competizione,A 635,1585,444 cv,52%,RWD
Alumicraft,Carro de Corrida Alumicraft Classe 10 2015,B 532,975,195 cv,42%,RWD
Alumicraft,Caminhonete Trucada Alumicraft #6165 2022,C 485,2155,525 cv,45%,RWD
Alumicraft,Alumicraft #122 Buggy Classe 1 2021,B 571,1588,625 cv,38%,RWD
Apollo,2019 Apollo Intensa Emozione,R 916,1250,780 cv,43%,RWD
Ariel,Ariel Atom 500 V8 2013,S2 825,650,475 cv,42%,RWD
Ariel,2016 Ariel Nomad,A 601,670,235 cv,39%,RWD
Aston Martin,Aston Martin Vulcan AMR Pro 2017,S2 898,1350,820 cv,49%,RWD
Aston Martin,Aston Martin Vulcan 2016,S2 884,1350,820 cv,49%,RWD
Aston Martin,Aston Martin Vantage 2019,A 696,1530,503 cv,50%,RWD
Aston Martin,Aston Martin Valkyrie AMR Pro 2022,R 989,1000,1000 cv,45%,RWD
Aston Martin,Aston Martin Valkyrie 2023,R 924,1095,1139 cv,44%,RWD
Aston Martin,Aston Martin Valhalla Concept Car 2019,R 960,1550,986 cv,42%,AWD
Aston Martin,Aston Martin DBX 2021,A 618,2245,542 cv,54%,AWD
Aston Martin,Aston Martin DBS Superleggera 2019,S1 736,1693,715 cv,51%,RWD
Aston Martin,Aston Martin DB7 GT 2003,B 566,1780,435 cv,54%,RWD
Aston Martin,Aston Martin DB5 de 1964,C 416,1502,282 cv,50%,RWD
Aston Martin,Aston Martin DB11 2017,A 679,1770,600 cv,51%,RWD
Audi,Audi R8 V10 Performance 2020,S1 738,1595,612 cv,43%,AWD
Audi,Audi TT RS Coupé 2010,B 593,1450,335 cv,60%,AWD
Audi,Audi Sport quattro de 1984,B 526,1298,302 cv,56%,AWD
Audi,Audi S1 2015,B 527,1315,228 cv,60%,AWD
Audi,Audi RS e-tron GT 2021,A 677,2347,637 cv,50%,AWD
Audi,Audi RS 7 Sportback 2021,A 655,2065,591 cv,56%,AWD
Audi,Audi RS 7 Sportback 2013,A 619,1930,552 cv,56%,AWD
Audi,Audi RS 6 Avant 2021,A 650,2075,591 cv,56%,AWD
Audi,Audi RS 6 Avant 2015,A 640,1950,552 cv,56%,AWD
Audi,Audi RS 6 2009,B 598,1985,572 cv,58%,AWD
Audi,Audi RS 6 2003,B 556,1840,444 cv,59%,AWD
Audi,Audi RS 5 Coupé 2011,A 613,1715,444 cv,57%,AWD
Audi,Audi RS 4 Avant 2018,A 637,1715,444 cv,56%,AWD
Audi,Audi RS 4 Avant 2013,A 607,1795,444 cv,56%,AWD
Audi,Audi RS 4 Avant 2001,B 544,1620,375 cv,60%,AWD
Audi,Audi RS 4 2006,B 593,1650,414 cv,58%,AWD
Audi,Audi RS 3 Sportback 2011,B 565,1575,335 cv,60%,AWD
Audi,Audi RS 3 Sedã 2020,A 617,1570,394 cv,59%,AWD
Audi,Audi R8 V10 Plus 2016,S1 731,1555,602 cv,43%,AWD
BMW,BMW M4 Competition Coupé 2021,A 666,1725,503 cv,52%,RWD
BMW,BMW M3 2008,A 608,1600,414 cv,52%,RWD
BMW,BMW M2 Coupé 2020,A 656,1575,405 cv,52%,RWD
Chevrolet,Chevrolet Corvette Z06 2023,S1 763,1561,670 cv,40%,RWD
Chevrolet,Chevrolet Camaro ZL1 2024,S1 718,1761,650 cv,54%,RWD
Dodge,Dodge Challenger SRT Demon 2018,A 678,1941,840 cv,58%,RWD
Ferrari,Ferrari SF90 Stradale 2020,S2 851,1570,986 cv,45%,AWD
Ferrari,Ferrari 488 Pista 2019,S2 803,1385,710 cv,42%,RWD
Ford,Ford GT 2017,S1 757,1385,647 cv,43%,RWD
Ford,Ford Mustang GT 2024,A 628,1735,486 cv,54%,RWD
Honda,Honda Civic Type R 2023,A 620,1447,315 cv,62%,FWD
Lamborghini,Lamborghini Revuelto 2024,S2 829,1772,1001 cv,44%,AWD
Lamborghini,Lamborghini Huracán STO 2020,S1 783,1339,631 cv,42%,RWD
Nissan,Nissan GT-R Nismo 2020,S1 780,1720,600 cv,54%,AWD
Porsche,Porsche 911 GT3 RS 2023,S1 785,1450,525 cv,39%,RWD
Toyota,Toyota GR Supra 2020,A 680,1540,335 cv,52%,RWD
"""

def conectar_banco():
    return sqlite3.connect(DB_NAME)

def inicializar_banco():
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Tabela principal para os veículos
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
    
    # Tabela para a Garagem de Setups Salvos
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
    
    # Garante a limpeza do banco antigo caso ele tenha ficado vazio anteriormente
    cursor.execute("SELECT COUNT(*) FROM veiculos")
    total = cursor.fetchone()[0]
    
    if total == 0:
        linhas = []
        # Tenta ler do arquivo local se ele existir no APK
        if os.path.exists(CSV_PATH):
            try:
                with open(CSV_PATH, mode="r", encoding="utf-8") as file:
                    reader = list(csv.reader(file))
                    if len(reader) > 1:
                        linhas = reader[1:]
            except Exception:
                linhas = []
        
        # Se não achou arquivo no disco, lê os dados da memória embutida
        if not linhas:
            stream = io.StringIO(DADOS_CSV_EMBUTIDOS.strip())
            reader = list(csv.reader(stream))
            if len(reader) > 1:
                linhas = reader[1:]
        
        for linha in linhas:
            if len(linha) >= 6:
                marca = linha[0].strip()
                modelo = linha[1].strip()
                classe = linha[2].strip()
                peso = linha[3].strip()
                potencia = linha[4].strip()
                distribuicao = linha[5].strip()
                tracao = linha[6].strip() if len(linha) > 6 else "RWD"
                
                cursor.execute("""
                    INSERT INTO veiculos (marca, modelo, classe, pi_original, peso_fabrica, potencia, distribuicao_dianteira, tracao)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (marca, modelo, classe, 0, peso, potencia, distribuicao, tracao))
        conn.commit()
        
    conn.close()

# Executa a inicialização do banco
inicializar_banco()

def carregar_lista_veiculos():
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
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
    car_name = ft.TextField(label="Nome do Carro / Projeto", width=320, border_radius=8)
    weight_input = ft.TextField(label="Peso Total (kg)", value="1350", width=320, border_radius=8, keyboard_type=ft.KeyboardType.NUMBER)
    power_input = ft.TextField(label="Potência (CV/HP)", value="450", width=320, border_radius=8, keyboard_type=ft.KeyboardType.NUMBER)
    front_bias_input = ft.TextField(label="Distribuição Dianteira (%)", value="52.00", width=320, border_radius=8, keyboard_type=ft.KeyboardType.NUMBER)
    
    # Carrega os carros cadastrados no SQLite
    veiculos_db = carregar_lista_veiculos()
    opcoes_veiculos = [ft.dropdown.Option(key=str(row[0]), text=f"{row[1]} - {row[2]}") for row in veiculos_db]

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
                
                w_clean = re.sub(r'[^0-9.]', '', str(peso))
                p_clean = re.sub(r'[^0-9.]', '', str(potencia))
                d_clean = re.sub(r'[^0-9.]', '', str(distribuicao))
                
                if w_clean: weight_input.value = w_clean
                if p_clean: power_input.value = p_clean
                if d_clean: front_bias_input.value = d_clean
                
                if tracao:
                    if "Traseira" in str(tracao) or "RWD" in str(tracao):
                        drivetrain_dd.value = "RWD (Traseira)"
                    elif "Dianteira" in str(tracao) or "FWD" in str(tracao):
                        drivetrain_dd.value = "FWD (Dianteira)"
                    elif "Integral" in str(tracao) or "AWD" in str(tracao):
                        drivetrain_dd.value = "AWD (Integral)"
                page.update()

    veiculo_dropdown = ft.Dropdown(
        label="🔍 Selecionar Carro da Planilha",
        width=320,
        border_radius=8,
        options=opcoes_veiculos
    )
    veiculo_dropdown.on_change = on_veiculo_change

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
    result_details = ft.Text(value="Selecione um carro ou preencha os dados acima e clique em Calcular Tunagem.", size=13, color=ft.Colors.WHITE_70)

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
                    ratio = first_gear - (i * (first_gear - last_gear) / (num_marchas - 1)) if num_marchas > 1 else first_gear
                    gears.append(f"{i+1}ª: {ratio:.2f}")

                gear_setting = f"Marcha Final: {final_drive:.2f}\n    - Escalonamento: {' | '.join(gears)}"

            if "Drift" in mod:
                cambagem = "Dianteira: -5.0° | Traseira: -1.0°"
                convergencia = "Dianteira: 0.2° (Out) | Traseira: -0.1° (In)"
                caster = "7.0°"
                altura_carro = "Dianteira: Baixa | Traseira: Média-Baixa"
            elif "Rally" in mod:
                cambagem = "Dianteira: -1.0° | Traseira: -0.8°"
                convergencia = "Dianteira: 0.0° | Traseira: 0.0°"
                caster = "6.0°"
                altura_carro = "Dianteira: Alta | Traseira: Alta"
            elif "Arrancada" in mod:
                cambagem = "Dianteira: 0.0° | Traseira: 0.0°"
                convergencia = "Dianteira: 0.0° | Traseira: 0.0°"
                caster = "5.0°"
                altura_carro = "Dianteira: Baixa | Traseira: Média"
            else:
                cambagem = "Dianteira: -2.0° | Traseira: -1.5°"
                convergencia = "Dianteira: 0.0° | Traseira: -0.1° (In)"
                caster = "6.0°"
                altura_carro = "Dianteira: Baixa | Traseira: Baixa"

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
                aero_summary = "🔒 Bloqueado (Sem Kit Aerodinâmico)"
                aero_setting = "Dianteira: 🔒 Bloqueado | Traseira: 🔒 Bloqueado"

            freio_bal = pct_dian
            freio_press = 100

            if "RWD" in drivetrain_dd.value:
                diff_text = "Aceleração: 65% | Desaceleração: 15%"
            elif "FWD" in drivetrain_dd.value:
                diff_text = "Aceleração: 45% | Desaceleração: 10%"
            else:
                diff_text = "Dianteira (Acc: 30% / Desacc: 0%) | Traseira (Acc: 50% / Desacc: 10%)"

            car_label = car_name.value if car_name.value else "Carro sem nome"
            result_title.value = f"💾 Setup Calculado: {car_label} ({peso}kg)"
            
            detalhes_str = (
                f"📊 RESUMO DE PERFORMANCE:\n"
                f"• Relação Peso/Potência: {relacao_peso_pot:.2f} kg/CV | Tração: {drivetrain_dd.value}\n"
                f"• Aerodinâmica: {aero_summary}\n\n"
                f"⚙️ AJUSTES RECOMENDADOS:\n"
                f"------------------------------------------------------------------------\n"
                f"🔹 Pressão Pneus: Dianteira {pneu_diant:.2f} bar | Traseira {pneu_tras:.2f} bar\n"
                f"🔹 Transmissão:\n    - {gear_setting}\n"
                f"🔹 Alinhamento:\n    - Cambagem: {cambagem}\n    - Convergência: {convergencia}\n    - Caster: {caster}\n"
                f"🔹 Barras Estabilizadoras: Dianteira {arb_diant:.2f} | Traseira {arb_tras:.2f}\n"
                f"🔹 Molas e Altura:\n    - Rigidez: Dianteira {mola_diant:.1f} | Traseira {mola_tras:.1f} kgf/mm\n    - Altura: {altura_carro}\n"
                f"🔹 Amortecimento (Rebound): Dianteira {rebound_diant:.1f} | Traseira {rebound_tras:.1f}\n"
                f"🔹 Amortecimento (Bump): Dianteira {bump_diant:.1f} | Traseira {bump_tras:.1f}\n"
                f"🔹 Aerodinâmica: {aero_setting}\n"
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
            result_details.value = "Por favor, verifique os valores numéricos de Peso, Potência e Distribuição."
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
            veiculo_dropdown,
            car_name, weight_input, power_input, front_bias_input, modality_dd, aero_kit_dd, front_bumper_dd, rear_wing_dd
        ],
        spacing=10
    )

    right_column = ft.Column(
        controls=[
            ft.Container(height=35),
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
