import flet as ft
import json

def main(page: ft.Page):
    # Configurações gerais da página para celular e PC
    page.title = "Calculadora de Tuning - Forza"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 15
    page.scroll = ft.ScrollMode.AUTO

    # Bloco try/except global para evitar a "tela branca" e exibir erros na tela
    try:
        # -------------------------------------------------------------
        # 1. GERENCIAMENTO DA GARAGEM (JSON VIA CLIENT_STORAGE DO FLET)
        # -------------------------------------------------------------
        def carregar_garagem():
            """Carrega as afinações salvas do armazenamento do cliente."""
            dados = page.client_storage.get("garagem_tuning")
            if dados:
                try:
                    return json.loads(dados)
                except Exception:
                    return []
            return []

        def salvar_garagem(lista_carros):
            """Salva a lista atualizada de carros na memória do app."""
            page.client_storage.set("garagem_tuning", json.dumps(lista_carros))

        # -------------------------------------------------------------
        # 2. VARIÁVEIS E CAMPOS DE ENTRADA (LÓGICA DE CÁLCULO)
        # -------------------------------------------------------------
        peso_input = ft.TextField(
            label="Peso Total (kg)",
            keyboard_type=ft.KeyboardType.NUMBER,
            value="1200"
        )
        distrib_input = ft.TextField(
            label="Distribuição Dianteira (%)",
            keyboard_type=ft.KeyboardType.NUMBER,
            value="52"
        )
        nome_carro_input = ft.TextField(
            label="Nome do Carro / Setup",
            hint_text="Ex: Nissan Skyline R34 Drift"
        )

        # Campos de Saída de Resultados
        mola_diant_txt = ft.Text("Mola Dianteira: - kgf/mm", size=16, weight=ft.FontWeight.BOLD)
        mola_tras_txt = ft.Text("Mola Traseira: - kgf/mm", size=16, weight=ft.FontWeight.BOLD)
        bar_diant_txt = ft.Text("Barra Anti-rolagem Diant: -", size=16)
        bar_tras_txt = ft.Text("Barra Anti-rolagem Tras: -", size=16)
        rebound_diant_txt = ft.Text("Amortecedor Rebound Diant: -", size=16)
        rebound_tras_txt = ft.Text("Amortecedor Rebound Tras: -", size=16)

        # -------------------------------------------------------------
        # 3. FUNÇÕES DE CÁLCULO E INTERAÇÃO
        # -------------------------------------------------------------
        def calcular_tuning(e):
            try:
                peso = float(peso_input.value.replace(',', '.'))
                distrib_diant = float(distrib_input.value.replace(',', '.')) / 100.0
                distrib_tras = 1.0 - distrib_diant

                # Exemplo de fórmulas base para molas e barras
                mola_diant = (peso * distrib_diant) / 10.0
                mola_tras = (peso * distrib_tras) / 10.0
                bar_diant = 1.0 + (64.0 - 1.0) * distrib_diant
                bar_tras = 1.0 + (64.0 - 1.0) * distrib_tras
                reb_diant = 3.0 + (20.0 - 3.0) * distrib_diant
                reb_tras = 3.0 + (20.0 - 3.0) * distrib_tras

                # Atualizando textos na interface
                mola_diant_txt.value = f"Mola Dianteira: {mola_diant:.1f} kgf/mm"
                mola_tras_txt.value = f"Mola Traseira: {mola_tras:.1f} kgf/mm"
                bar_diant_txt.value = f"Barra Anti-rolagem Diant: {bar_diant:.1f}"
                bar_tras_txt.value = f"Barra Anti-rolagem Tras: {bar_tras:.1f}"
                rebound_diant_txt.value = f"Amortecedor Rebound Diant: {reb_diant:.1f}"
                rebound_tras_txt.value = f"Amortecedor Rebound Tras: {reb_tras:.1f}"

                page.update()
            except ValueError:
                page.snack_bar = ft.SnackBar(ft.Text("Por favor, insira números válidos!"))
                page.snack_bar.open = True
                page.update()

        lista_garagem_ui = ft.Column()

        def atualizar_lista_garagem_ui():
            lista_garagem_ui.controls.clear()
            garagem = carregar_garagem()
            for item in garagem:
                lista_garagem_ui.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.icons.DIRECTIONS_CAR),
                        title=ft.Text(item.get("nome", "Carro Sem Nome")),
                        subtitle=ft.Text(f"Peso: {item.get('peso')}kg | Dianteira: {item.get('distrib')}%")
                    )
                )
            page.update()

        def salvar_na_garagem(e):
            if not nome_carro_input.value:
                page.snack_bar = ft.SnackBar(ft.Text("Digite um nome para o carro antes de salvar!"))
                page.snack_bar.open = True
                page.update()
                return

            garagem = carregar_garagem()
            novo_item = {
                "nome": nome_carro_input.value,
                "peso": peso_input.value,
                "distrib": distrib_input.value
            }
            garagem.append(novo_item)
            salvar_garagem(garagem)
            nome_carro_input.value = ""
            atualizar_lista_garagem_ui()
            page.snack_bar = ft.SnackBar(ft.Text("Tuning salvo na Garagem com sucesso!"))
            page.snack_bar.open = True
            page.update()

        # -------------------------------------------------------------
        # 4. MONTAGEM DA INTERFACE (LAYOUT)
        # -------------------------------------------------------------
        btn_calcular = ft.ElevatedButton("Calcular Tuning", on_click=calcular_tuning, icon=ft.icons.CALCULATE)
        btn_salvar = ft.ElevatedButton("Salvar na Garagem", on_click=salvar_na_garagem, icon=ft.icons.SAVE)

        # Montagem na página principal
        page.add(
            ft.Text("Calculadora de Tuning Forza", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_200),
            ft.Divider(),
            ft.Row([peso_input, distrib_input], wrap=True),
            btn_calcular,
            ft.Divider(),
            ft.Text("Resultados Recomendados:", size=18, weight=ft.FontWeight.BOLD),
            mola_diant_txt,
            mola_tras_txt,
            bar_diant_txt,
            bar_tras_txt,
            rebound_diant_txt,
            rebound_tras_txt,
            ft.Divider(),
            ft.Text("Garagem de Setups", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.AMBER_200),
            nome_carro_input,
            btn_salvar,
            lista_garagem_ui
        )

        # Carrega os itens salvos ao iniciar
        atualizar_lista_garagem_ui()

    except Exception as err:
        # Se ocorrer qualquer falha durante a inicialização, o app exibe o erro na tela em vez de ficar branco
        page.clean()
        page.add(
            ft.Text("Ocorreu um erro ao carregar o aplicativo:", color=ft.colors.RED, size=18, weight=ft.FontWeight.BOLD),
            ft.Text(str(err), color=ft.colors.RED_200)
        )
        page.update()

# Ponto de entrada padrão exigido pelo Flet / serious_python no Android
if __name__ == "__main__":
    ft.app(target=main)
