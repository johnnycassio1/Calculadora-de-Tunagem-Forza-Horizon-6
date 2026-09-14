import streamlit as st

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Calculadora Forza",
    page_icon="🏎️",
    layout="centered"
)

st.title("🏎️ Calculadora de Tunagem Forza")
st.caption("Ajustes precisos de performance para o seu carro")

# --- LÓGICA DE CÁLCULO ---
def calcular_transmissao(opcao_trans, potencia_cv):
    if opcao_trans in ["Original", "Rua"]:
        return "Transmissão Bloqueada para ajustes no jogo."
    elif opcao_trans == "Esportiva":
        return "Ajuste apenas a Relação Final (Final Drive): ~3.70"
    
    mapa_marchas = {"Corrida (6v)": 6, "7v": 7, "8v": 8, "9v": 9, "10v": 10}
    num_marchas = mapa_marchas.get(opcao_trans, 6)
    final_drive = max(2.8, 4.2 - (num_marchas * 0.12))
    
    marchas = []
    v_inicio, v_fim = 2.80, 0.75
    passo = (v_inicio - v_fim) / (num_marchas - 1)
    for i in range(num_marchas):
        val_marcha = v_inicio - (passo * i)
        marchas.append(f"**{i+1}ª:** {val_marcha:.2f}")
        
    return f"**Relação Final:** {final_drive:.2f}\n\n" + " | ".join(marchas)

# --- ENTRADA DE DADOS (INTERFACE) ---
st.header("📋 Dados do Veículo")

col1, col2 = st.columns(2)

with col1:
    peso = st.number_input("Peso Total (kg)", min_value=500, max_value=3000, value=1350, step=10)
    potencia = st.number_input("Potência (CV/HP)", min_value=50, max_value=2000, value=450, step=10)
    dist_dianteira_pct = st.number_input("Distribuição Dianteira (%)", min_value=30.0, max_value=70.0, value=52.0, step=0.5)

with col2:
    tracao = st.selectbox("Tração", ["RWD (Traseira)", "FWD (Dianteira)", "AWD (4x4)"])
    transmissao_nome = st.selectbox("Transmissão", ["Original", "Rua", "Esportiva", "Corrida (6v)", "7v", "8v", "9v", "10v"], index=3)
    freio_nome = st.selectbox("Freios", ["Original", "Rua", "Esportivo", "Corrida"], index=3)
    susp_nome = st.selectbox("Suspensão", ["Original", "Rua", "Esportivo", "Corrida", "Rally", "Drift"], index=3)

# --- BOTÃO DE CÁLCULO ---
if st.button("🚀 CALCULAR TUNAGEM", use_container_width=True, type="primary"):
    dist_dianteira = dist_dianteira_pct / 100.0
    dist_traseira = 1.0 - dist_dianteira

    # 1. Pneus
    pneu_f = 1.9 + (peso / 2000.0) * dist_dianteira
    pneu_t = 1.9 + (peso / 2000.0) * dist_traseira
    if "RWD" in tracao: pneu_t -= 0.1
    elif "FWD" in tracao: pneu_f -= 0.1

    # 2. Suspensão e Alinhamento
    if "Rally" in susp_nome:
        mola_b = peso * 0.28
        mola_f, mola_t = mola_b * dist_dianteira, mola_b * dist_traseira
        reb_f, reb_t = 7.0 * dist_dianteira + 1.0, 7.0 * dist_traseira + 1.0
        bmp_f, bmp_t = reb_f * 0.5, reb_t * 0.5
        camb_f, camb_t, toe_f, toe_t, caster = -1.2, -0.5, 0.0, 0.0, 6.0
        susp_info = f"**Molas:** F {mola_f:.1f} / T {mola_t:.1f} kgf/mm | **Altura:** Elevada\n\n**Rebound:** F {reb_f:.1f} / T {reb_t:.1f} | **Bump:** F {bmp_f:.1f} / T {bmp_t:.1f}"
    elif "Drift" in susp_nome:
        mola_b = peso * 0.42
        mola_f, mola_t = mola_b * dist_dianteira, mola_b * dist_traseira
        reb_f, reb_t = 11.0 * dist_dianteira + 1.0, 10.0 * dist_traseira + 1.0
        bmp_f, bmp_t = reb_f * 0.6, reb_t * 0.6
        camb_f, camb_t, toe_f, toe_t, caster = -3.5, -1.0, 0.2, -0.1, 7.0
        susp_info = f"**Molas:** F {mola_f:.1f} / T {mola_t:.1f} kgf/mm | **Altura:** Baixa\n\n**Rebound:** F {reb_f:.1f} / T {reb_t:.1f} | **Bump:** F {bmp_f:.1f} / T {bmp_t:.1f}"
    elif "Original" in susp_nome or "Rua" in susp_nome:
        camb_f, camb_t, toe_f, toe_t, caster = -1.0, -0.8, 0.0, 0.0, 5.5
        susp_info = "Molas e Amortecedores Bloqueados no jogo."
    else:
        mola_b = peso * 0.40
        mola_f, mola_t = mola_b * dist_dianteira, mola_b * dist_traseira
        reb_f, reb_t = 12.0 * dist_dianteira + 1.0, 12.0 * dist_traseira + 1.0
        bmp_f, bmp_t = reb_f * 0.6, reb_t * 0.6
        camb_f, camb_t, toe_f, toe_t, caster = -1.8, -1.2, 0.0, 0.0, 6.0
        susp_info = f"**Molas:** F {mola_f:.1f} / T {mola_t:.1f} kgf/mm | **Altura:** Mínima\n\n**Rebound:** F {reb_f:.1f} / T {reb_t:.1f} | **Bump:** F {bmp_f:.1f} / T {bmp_t:.1f}"

    # 3. ARB
    arb_min, arb_max = 1.0, 65.0
    if "FWD" in tracao:
        arb_f = (arb_max - arb_min) * dist_dianteira * 0.75
        arb_t = (arb_max - arb_min) * dist_traseira * 1.25
    else:
        arb_f = (arb_max - arb_min) * dist_dianteira + arb_min
        arb_t = (arb_max - arb_min) * dist_traseira + arb_min

    # 4. Outros componentes
    trans_info = calcular_transmissao(transmissao_nome, potencia)
    freio_info = "Ajustes Bloqueados" if "Original" in freio_nome or "Rua" in freio_nome else f"**Equilíbrio:** {int(dist_dianteira_pct)}% | **Pressão:** 100%"
    
    if "RWD" in tracao: diff_info = f"**Aceleração:** {min(80, 35 + int(potencia / 12))}% | **Desaceleração:** 15%"
    elif "FWD" in tracao: diff_info = "**Aceleração:** 40% | **Desaceleração:** 10%"
    else: diff_info = "**Dianteiro:** 40%/0% | **Traseiro:** 65%/15% | **Balanço Central:** 65%"

    # --- RESULTADOS EXIBIDOS EM CARDS ---
    st.divider()
    st.subheader("🛠️ Ficha de Tunagem Resultante")

    st.markdown(f"**1. PNEUS:** Frente `{pneu_f:.1f} BAR` | Trás `{pneu_t:.1f} BAR`")
    st.markdown(f"**2. ALINHAMENTO:** Cambagem F `{camb_f}°` / T `{camb_t}°` | Convergência F `{toe_f}°` / T `{toe_t}°` | Caster `{caster}°`")
    st.markdown(f"**3. BARRAS ESTABILIZADORAS:** Frente `{arb_f:.1f}` | Trás `{arb_t:.1f}`")
    
    with st.expander("4. SUSPENSÃO E AMORTECIMENTO", expanded=True):
        st.markdown(susp_info)
        
    with st.expander("5. TRANSMISSÃO", expanded=True):
        st.markdown(trans_info)
        
    st.markdown(f"**6. FREIOS:** {freio_info}")
    st.markdown(f"**7. DIFERENCIAL:** {diff_info}")