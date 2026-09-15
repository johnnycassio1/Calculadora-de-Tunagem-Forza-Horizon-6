import streamlit as st
import json
import os

DB_FILE = "garagem_setups.json"

def carregar_garagem():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def salvar_garagem(setups):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(setups, f, ensure_ascii=False, indent=4)

# Configuração visual do Streamlit
st.set_page_config(
    page_title="Calculadora de Tunagem Forza - Safira Spec",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Calculadora de Tunagem Forza - Safira Spec")
st.caption("Ajustes precisos de performance para o seu carro")

# Inicialização da garagem na sessão
if "setups_salvos" not in st.session_state:
    st.session_state.setups_salvos = carregar_garagem()

# Abas iguais ao aplicativo Flet
tab_calc, tab_garagem = st.tabs(["⚡ Calculadora", "🏎️ Garagem de Setups"])

# ---------------------------------------------------------
# ABA 1: CALCULADORA
# ---------------------------------------------------------
with tab_calc:
    st.subheader("📋 Dados do Veículo")
    
    col1, col2 = st.columns(2)

    with col1:
        car_name = st.text_input("Nome do Carro / Projeto (Opcional)", value="", placeholder="Ex: Nissan Skyline GT-R")
        weight_input = st.number_input("Peso Total (kg)", value=1350.0, step=10.0)
        power_input = st.number_input("Potência (CV/HP)", value=450.0, step=10.0)
        front_bias_input = st.number_input("Distribuição Dianteira (%)", value=52.00, step=0.5, min_value=10.0, max_value=90.0)
        
        modality = st.selectbox(
            "Modalidade",
            ["Pista / Asfalto (Grip)", "Drift", "Rally / Off-road", "Arrancada (Drag)"]
        )

        has_aero = st.selectbox("Possui Kit Aerodinâmico?", ["Não", "Sim"])
        
        front_bumper = "Não"
        rear_wing = "Não"
        if has_aero == "Sim":
            front_bumper = st.selectbox("Para-choque Dianteiro de Corrida", ["Sim", "Não"])
            rear_wing = st.selectbox("Aerofólio de Corrida", ["Sim", "Não"])

    with col2:
        drivetrain = st.selectbox("Tração", ["RWD (Traseira)", "FWD (Dianteira)", "AWD (Integral)"])
        transmission = st.selectbox(
            "Transmissão",
            [
                "Original", 
                "Rua", 
                "Esporte", 
                "Corrida (6V)", 
                "Corrida (7V)", 
                "Corrida (8V)", 
                "Corrida (9V)", 
                "Corrida (10V)"
            ]
        )
        brakes = st.selectbox("Freios", ["Original", "Corrida"])
        suspension = st.selectbox("Suspensão", ["Original", "Rua", "Esporte", "Corrida", "Drift", "Rally"])

    st.write("")
    if st.button("⚡ CALCULAR TUNAGEM", type="primary", use_container_width=True):
        peso = float(weight_input)
        potencia = float(power_input)
        pct_dian = float(front_bias_input)
        bias = pct_dian / 100.0
        bias_tras = 1.0 - bias
        relacao_peso_pot = peso / potencia if potencia > 0 else 0

        pneu_diant = 1.95
        pneu_tras = 1.90 if "RWD" in drivetrain else 1.95

        # ---------------------------------------------------------
        # CÁLCULO DE TRANSMISSÃO E ESCALONAMENTO DE MARCHAS
        # ---------------------------------------------------------
        if relacao_peso_pot < 2.0:
            final_drive = 3.20
        elif relacao_peso_pot < 3.0:
            final_drive = 3.55
        elif relacao_peso_pot < 4.0:
            final_drive = 3.80
        else:
            final_drive = 4.10

        if "Arrancada" in modality:
            final_drive -= 0.30
        elif "Drift" in modality:
            final_drive += 0.20

        if transmission in ["Original", "Rua"]:
            gear_setting = "🔒 Bloqueado (Sem ajustes disponíveis)"
        elif transmission == "Esporte":
            gear_setting = f"Marcha Final (Final Drive): {final_drive:.2f} | Marchas Individuais: 🔒 Bloqueadas"
        else:
            num_marchas = 6
            if "7V" in transmission: num_marchas = 7
            elif "8V" in transmission: num_marchas = 8
            elif "9V" in transmission: num_marchas = 9
            elif "10V" in transmission: num_marchas = 10

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
        # OUTROS CÁLCULOS
        # ---------------------------------------------------------
        if "Drift" in modality:
            cambagem = "Dianteira: -5.0° | Traseira: -1.0°"
            convergencia = "Dianteira: 0.2° (Out) | Traseira: -0.1° (In)"
            caster = "7.0°"
        elif "Rally" in modality:
            cambagem = "Dianteira: -1.0° | Traseira: -0.8°"
            convergencia = "Dianteira: 0.0° | Traseira: 0.0°"
            caster = "6.0°"
        elif "Arrancada" in modality:
            cambagem = "Dianteira: 0.0° | Traseira: 0.0°"
            convergencia = "Dianteira: 0.0° | Traseira: 0.0°"
            caster = "5.0°"
        else:
            cambagem = "Dianteira: -2.0° | Traseira: -1.5°"
            convergencia = "Dianteira: 0.0° | Traseira: -0.1° (In)"
            caster = "6.0°"

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

        if has_aero == "Sim":
            downforce_dian_val = peso * 0.08
            downforce_tras_val = peso * 0.12
            f_val = f"{downforce_dian_val:.1f} kgf" if front_bumper == "Sim" else "🔒 Bloqueado"
            r_val = f"{downforce_tras_val:.1f} kgf" if rear_wing == "Sim" else "🔒 Bloqueado"
            aero_summary = f"Dianteira [{f_val}] | Traseira [{r_val}]"
            aero_setting = f"Dianteira: {f_val} | Traseira: {r_val}"
        else:
            aero_summary = "🔒 Bloqueado (Sem Kit Aerodinâmico instalado)"
            aero_setting = "Dianteira: 🔒 Bloqueado | Traseira: 🔒 Bloqueado"

        freio_bal = pct_dian
        freio_press = 100

        if "RWD" in drivetrain:
            diff_text = "Aceleração: 65% | Desaceleração: 15%"
        elif "FWD" in drivetrain:
            diff_text = "Aceleração: 45% | Desaceleração: 10%"
        else:
            diff_text = "Dianteira (Acc: 30% / Desacc: 0%) | Traseira (Acc: 50% / Desacc: 10%) | Balanço Central: 65% Traseira"

        car_label = car_name if car_name else "Carro sem nome"

        detalhes_str = (
            f"📊 RESUMO DE PERFORMANCE:\n"
            f"• Relação Peso/Potência: {relacao_peso_pot:.2f} kg/CV | Tração: {drivetrain}\n"
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
            f"🔹 Molas: Dianteira {mola_diant:.1f} kgf/mm | Traseira {mola_tras:.1f} kgf/mm\n"
            f"🔹 Amortecimento (Rebound): Dianteira {rebound_diant:.1f} | Traseira {rebound_tras:.1f}\n"
            f"🔹 Amortecimento (Bump/Carga): Dianteira {bump_diant:.1f} | Traseira {bump_tras:.1f}\n"
            f"🔹 Aerodinâmica (Downforce): {aero_setting}\n"
            f"🔹 Freios: Balanço {freio_bal:.1f}% | Pressão {freio_press}%\n"
            f"🔹 Diferencial: {diff_text}"
        )

        st.session_state["ultimo_setup"] = {
            "nome": car_label,
            "modalidade": modality,
            "tracao": drivetrain,
            "detalhes": detalhes_str
        }

    if "ultimo_setup" in st.session_state:
        setup = st.session_state["ultimo_setup"]
        st.success(f"💾 Setup Calculado: {setup['nome']}")
        st.code(setup["detalhes"], language="text")

        if st.button("💾 SALVAR NA GARAGEM", use_container_width=True):
            st.session_state.setups_salvos.append(dict(setup))
            salvar_garagem(st.session_state.setups_salvos)
            st.toast("Setup salvo com sucesso na garagem! ✅")

# ---------------------------------------------------------
# ABA 2: GARAGEM
# ---------------------------------------------------------
with tab_garagem:
    st.subheader("🏎️ Garagem de Setups Salvos")
    
    if not st.session_state.setups_salvos:
        st.info("Nenhum setup salvo na garagem ainda.")
    else:
        for idx, item in enumerate(st.session_state.setups_salvos):
            with st.expander(f"🏎️ {item['nome']} - ({item['modalidade']} | {item['tracao']})"):
                st.code(item['detalhes'], language="text")
                if st.button(f"🗑️ Remover {item['nome']}", key=f"del_{idx}"):
                    st.session_state.setups_salvos.pop(idx)
                    salvar_garagem(st.session_state.setups_salvos)
                    st.rerun()
