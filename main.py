import flet as ft

def main(page: ft.Page):
    page.title = "Calculadora Forza"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 15

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
            marchas.append(f"{i+1}ª: {val_marcha:.2f}")
            
        return f"Relação Final: {final_drive:.2f}\n" + " | ".join(marchas)

    def processar_calculo(e):
        try:
            peso = float(entry_peso.value)
            potencia = float(entry_potencia.value)
            dist_dianteira_pct = float(entry_dist.value)
            
            tracao = drop_tracao.value
            transmissao_nome = drop_trans.value
            freio_nome = drop_freio.value
            susp_nome = drop_susp.value

            dist_dianteira = dist_dianteira_pct / 100.0
            dist_traseira = 1.0 - dist_dianteira

            # Pneus
            pneu_f = 1.9 + (peso / 2000.0) * dist_dianteira
            pneu_t = 1.9 + (peso / 2000.0) * dist_traseira
            if "RWD" in tracao: pneu_t -= 0.1
            elif "FWD" in tracao: pneu_f -= 0.1

            # Suspensão
            if "Rally" in susp_nome:
                mola_b = peso * 0.28
                mola_f, mola_t = mola_b * dist_dianteira, mola_b * dist_traseira
                reb_f, reb_t = 7.0 * dist_dianteira + 1.0, 7.0 * dist_traseira + 1.0
                bmp_f, bmp_t = reb_f * 0.5, reb_t * 0.5
                camb_f, camb_t, toe_f, toe_t, caster = -1.2, -0.5, 0.0, 0.0, 6.0
                susp_info = f"Molas: F {mola_f:.1f} / T {mola_t:.1f} kgf/mm\nRebound: F {reb_f:.1f} / T {reb_t:.1f} | Bump: F {bmp_f:.1f} / T {bmp_t:.1f}"
            elif "Drift" in susp_nome:
                mola_b = peso * 0.42
                mola_f, mola_t = mola_b * dist_dianteira, mola_b * dist_traseira
                reb_f, reb_t = 11.0 * dist_dianteira + 1.0, 10.0 * dist_traseira + 1.0
                bmp_f, bmp_t = reb_f * 0.6, reb_t * 0.6
                camb_f, camb_t, toe_f, toe_t, caster = -3.5, -1.0, 0.2, -0.1, 7.0
                susp_info = f"Molas: F {mola_f:.1f} / T {mola_t:.1f} kgf/mm\nRebound: F {reb_f:.1f} / T {reb_t:.1f} | Bump: F {bmp_f:.1f} / T {bmp_t:.1f}"
            elif "Original" in susp_nome or "Rua" in susp_nome:
                camb_f, camb_t, toe_f, toe_t, caster = -1.0, -0.8, 0.0, 0.0, 5.5
                susp_info = "Molas/Amortecedores Bloqueados"
            else:
                mola_b = peso * 0.40
                mola_f, mola_t = mola_b * dist_dianteira, mola_b * dist_traseira
                reb_f, reb_t = 12.0 * dist_dianteira + 1.0, 12.0 * dist_traseira + 1.0
                bmp_f, bmp_t = reb_f * 0.6, reb_t * 0.6
                camb_f, camb_t, toe_f, toe_t, caster = -1.8, -1.2, 0.0, 0.0, 6.0
                susp_info = f"Molas: F {mola_f:.1f} / T {mola_t:.1f} kgf/mm\nRebound: F {reb_f:.1f} / T {reb_t:.1f} | Bump: F {bmp_f:.1f} / T {bmp_t:.1f}"

            # ARB
            arb_min, arb_max = 1.0, 65.0
            if "FWD" in tracao:
                arb_f = (arb_max - arb_min) * dist_dianteira * 0.75
                arb_t = (arb_max - arb_min) * dist_traseira * 1.25
            else:
                arb_f = (arb_max - arb_min) * dist_dianteira + arb_min
                arb_t = (arb_max - arb_min) * dist_traseira + arb_min

            trans_info = calcular_transmissao(transmissao_nome, potencia)
            freio_info = "Bloqueado" if "Original" in freio_nome or "Rua" in freio_nome else f"Equilíbrio: {int(dist_dianteira_pct)}% | Pressão: 100%"
            
            if "RWD" in tracao: diff_info = f"Aceleração: {min(80, 35 + int(potencia / 12))}% | Desaceleração: 15%"
            elif "FWD" in tracao: diff_info = "Aceleração: 40% | Desaceleração: 10%"
            else: diff_info = "Dianteiro: 40%/0% | Traseiro: 65%/15% | Balanço Central: 65%"

            res = (
                f"1. PNEUS: Frente {pneu_f:.1f} BAR | Trás {pneu_t:.1f} BAR\n\n"
                f"2. ALINHAMENTO: Cambagem F {camb_f}° / T {camb_t}° | Convergência F {toe_f}° / T {toe_t}° | Caster: {caster}°\n\n"
                f"3. BARRAS ESTABILIZADORAS: Frente {arb_f:.1f} | Trás {arb_t:.1f}\n\n"
                f"4. SUSPENSÃO:\n{susp_info}\n\n"
                f"5. TRANSMISSÃO:\n{trans_info}\n\n"
                f"6. FREIOS: {freio_info}\n\n"
                f"7. DIFERENCIAL: {diff_info}"
            )
            
            txt_resultado.value = res

        except ValueError:
            txt_resultado.value = "Preencha todos os campos corretamente!"
        
        page.update()

    # Layout
    titulo = ft.Text("🏎️ Tunagem Forza", size=22, weight=ft.FontWeight.BOLD)
    
    entry_peso = ft.TextField(label="Peso Total (kg)", value="1350", keyboard_type=ft.KeyboardType.NUMBER)
    entry_potencia = ft.TextField(label="Potência (CV/HP)", value="450", keyboard_type=ft.KeyboardType.NUMBER)
    entry_dist = ft.TextField(label="Distribuição Dianteira (%)", value="52", keyboard_type=ft.KeyboardType.NUMBER)
    
    drop_tracao = ft.Dropdown(label="Tração", value="RWD (Traseira)", options=[ft.dropdown.Option("RWD (Traseira)"), ft.dropdown.Option("FWD (Dianteira)"), ft.dropdown.Option("AWD (4x4)")])
    drop_trans = ft.Dropdown(label="Transmissão", value="Corrida (6v)", options=[ft.dropdown.Option("Original"), ft.dropdown.Option("Rua"), ft.dropdown.Option("Esportiva"), ft.dropdown.Option("Corrida (6v)"), ft.dropdown.Option("7v"), ft.dropdown.Option("8v"), ft.dropdown.Option("9v"), ft.dropdown.Option("10v")])
    drop_freio = ft.Dropdown(label="Freios", value="Corrida", options=[ft.dropdown.Option("Original"), ft.dropdown.Option("Rua"), ft.dropdown.Option("Esportivo"), ft.dropdown.Option("Corrida")])
    drop_susp = ft.Dropdown(label="Suspensão", value="Corrida", options=[ft.dropdown.Option("Original"), ft.dropdown.Option("Rua"), ft.dropdown.Option("Esportivo"), ft.dropdown.Option("Corrida"), ft.dropdown.Option("Rally"), ft.dropdown.Option("Drift")])

    btn_calcular = ft.ElevatedButton("CALCULAR TUNAGEM", icon=ft.Icons.CALCULATE, on_click=processar_calculo)
    txt_resultado = ft.TextField(label="Resultado", multiline=True, read_only=True, min_lines=6)

    page.add(titulo, entry_peso, entry_potencia, entry_dist, drop_tracao, drop_trans, drop_freio, drop_susp, ft.Divider(), btn_calcular, ft.Divider(), txt_resultado)

ft.app(target=main)
