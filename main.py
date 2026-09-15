import flet as ft

def main(page: ft.Page):
    page.title = "Calculadora de Tunagem - Forza Horizon 6"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    # Campos de Entrada (Inputs)
    weight_input = ft.TextField(
        label="Peso Total do Carro (kg)",
        keyboard_type=ft.KeyboardType.NUMBER,
        width=300
    )
    front_bias_input = ft.TextField(
        label="Distribuição Dianteira (%)",
        hint_text="Ex: 52",
        keyboard_type=ft.KeyboardType.NUMBER,
        width=300
    )
    
    # Campo de Resultado
    result_text = ft.Text(
        value="Preencha os dados e clique em calcular.",
        size=16,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.LIGHT_BLUE_200
    )

    # Função de Cálculo
    def calcular_tunagem(e):
        try:
            peso = float(weight_input.value)
            dianteira_pct = float(front_bias_input.value) / 100
            traseira_pct = 1.0 - dianteira_pct

            # Exemplo de lógica base de suspensão (ajuste com suas fórmulas reais)
            mola_dianteira = peso * dianteira_pct * 0.1
            mola_traseira = peso * traseira_pct * 0.1

            result_text.value = (
                f"--- RESULTADOS DA TUNAGEM ---\n"
                f"Mola Dianteira: {mola_dianteira:.1f} kgf/mm\n"
                f"Mola Traseira: {mola_traseira:.1f} kgf/mm"
            )
            result_text.color = ft.Colors.GREEN_400
        except (ValueError, TypeError):
            result_text.value = "Erro: Digite valores numéricos válidos nos campos acima!"
            result_text.color = ft.Colors.RED_400
        
        page.update()

    # Botão de Ação
    calc_button = ft.ElevatedButton(
        text="Calcular Tunagem",
        on_click=calcular_tunagem,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
    )

    # Adiciona os elementos na tela do aplicativo
    page.add(
        ft.Text("Calculadora de Tunagem FH6", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        weight_input,
        front_bias_input,
        ft.Container(height=10),
        calc_button,
        ft.Container(height=15),
        result_text
    )

# Ponto de entrada padrão exigido pelo Flet 1.0.0
if __name__ == "__main__":
    ft.run(main)
