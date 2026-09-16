import flet as ft


def main(page: ft.Page):
    page.title = "Calculadora de Tunagem - Forza Horizon 6"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    # ---------- Campos de entrada ----------
    weight_input = ft.TextField(
        label="Peso Total do Carro (kg)",
        hint_text="Ex: 1300",
        keyboard_type=ft.KeyboardType.NUMBER,
        width=320,
    )
    front_bias_input = ft.TextField(
        label="Distribuição Dianteira (%)",
        hint_text="Ex: 52",
        keyboard_type=ft.KeyboardType.NUMBER,
        width=320,
    )

    # ---------- Painel de resultado ----------
    result_text = ft.Text(
        value="Preencha os dados e clique em calcular.",
        size=16,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.LIGHT_BLUE_200,
        selectable=True,
    )

    painel_resultado = ft.Container(
        content=result_text,
        padding=15,
        border_radius=10,
        border=ft.border.all(1, ft.Colors.BLUE_GREY_700),
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
    )

    # ---------- Funções auxiliares ----------
    def converter_para_float(valor, nome_campo):
        try:
            return float(valor)
        except (TypeError, ValueError):
            raise ValueError(f"O campo '{nome_campo}' precisa de um número válido.")

    # ---------- Função de cálculo ----------
    def calcular(e):
        try:
            peso = converter_para_float(weight_input.value, "Peso Total")
            bias = converter_para_float(front_bias_input.value, "Distribuição Dianteira")

            if peso <= 0:
                raise ValueError("O peso total deve ser maior que zero.")
            if not 1 <= bias <= 99:
                raise ValueError("A distribuição dianteira deve ficar entre 1% e 99%.")

            frac_dianteira = bias / 100
            frac_traseira = 1.0 - frac_dianteira

            peso_dianteiro = peso * frac_dianteira
            peso_traseiro = peso * frac_traseira

            # Fórmula-base de exemplo — substitua pelos seus cálculos reais
            mola_dianteira = peso_dianteiro * 0.1
            mola_traseira = peso_traseiro * 0.1

            result_text.value = (
                "--- RESULTADOS DA TUNAGEM ---\n"
                f"Peso eixo dianteiro: {peso_dianteiro:.0f} kg\n"
                f"Peso eixo traseiro:  {peso_traseiro:.0f} kg\n"
                f"Mola dianteira: {mola_dianteira:.1f} kgf/mm\n"
                f"Mola traseira:  {mola_traseira:.1f} kgf/mm"
            )
            result_text.color = ft.Colors.GREEN_400
        except ValueError as erro:
            result_text.value = str(erro)
            result_text.color = ft.Colors.RED_400

        page.update()

    # ---------- Botão limpar ----------
    def limpar(e):
        weight_input.value = ""
        front_bias_input.value = ""
        result_text.value = "Preencha os dados e clique em calcular."
        result_text.color = ft.Colors.LIGHT_BLUE_200
        page.update()

    # Enter também dispara o cálculo
    weight_input.on_submit = calcular
    front_bias_input.on_submit = calcular

    botao_calcular = ft.ElevatedButton(
        text="Calcular Tunagem",
        icon=ft.Icons.CALCULATE,
        on_click=calcular,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
    )
    botao_limpar = ft.OutlinedButton(
        text="Limpar",
        icon=ft.Icons.CLEAR,
        on_click=limpar,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
    )

    # ---------- Tela ----------
    page.add(
        ft.Text("Calculadora de Tunagem FH6", size=24, weight=ft.FontWeight.BOLD),
        ft.Text(
            "Suspensão calculada a partir do peso e da distribuição do carro",
            size=13,
            color=ft.Colors.BLUE_GREY_300,
        ),
        ft.Divider(),
        weight_input,
        front_bias_input,
        ft.Container(height=10),
        ft.Row([botao_calcular, botao_limpar], spacing=10),
        ft.Container(height=15),
        painel_resultado,
    )


if __name__ == "__main__":
    # Flet 1.0+ usa ft.run(); versões anteriores usam ft.app()
    if hasattr(ft, "run"):
        ft.run(main)
    else:
        ft.app(main)
