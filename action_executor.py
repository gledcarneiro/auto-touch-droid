import time
import os

# Assumindo que você tem adb_utils.py e image_detection.py acessíveis
# Importe as funções necessárias
from adb_utils import capture_screen, simulate_touch
from image_detection import find_image_on_screen

def find_and_confirm_click(template_path, device_id=None, screenshot_path="temp_screenshot_for_find_click.png", click_delay=1):
    """
    Captura a tela, procura por um template de imagem, e se encontrado, clica no centro dele.

    Args:
        template_path (str): O caminho para o arquivo do template de imagem a ser procurado.
        device_id (str, optional): O ID do dispositivo Android. Se None, usa o dispositivo padrão.
        screenshot_path (str, optional): Caminho temporário para salvar a screenshot.
        click_delay (int, optional): Tempo de espera em segundos após o clique.

    Returns:
        tuple: Retorna (True, (center_x, center_y)) se a imagem foi encontrada e clicada,
               (False, None) caso contrário.
    """
    print(f"Procurando template: {template_path}")

    # 1. Capturar a tela
    if not capture_screen(device_id=device_id, output_path=screenshot_path):
        print("Falha ao capturar a tela.")
        # Clean up temp screenshot if capture failed and left a file
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)
        return (False, None)

    # 2. Procurar pela imagem (template) na screenshot
    image_position = find_image_on_screen(screenshot_path, template_path)

    # Clean up temp screenshot after find_image_on_screen is done with it
    if os.path.exists(screenshot_path):
        os.remove(screenshot_path)
        print(f"Arquivo temporário {screenshot_path} removido.")


    # 3. Se a imagem for encontrada, calcular o centro e clicar
    if image_position:
        x, y, w, h = image_position
        center_x = x + w // 2
        center_y = y + h // 2
        print(f"Template encontrado em ({x}, {y}). Simulando clique no centro ({center_x}, {center_y}).")

        simulate_touch(center_x, center_y, device_id=device_id)

        # Opcional: Adicionar um pequeno delay após o clique
        if click_delay > 0:
            time.sleep(click_delay)

        return (True, (center_x, center_y)) # Retorna True e as coordenadas do centro
    else:
        print("Template não encontrado na tela.")
        return (False, None) # Retorna False e None

# # Exemplo de uso (descomente para testar):
# # Substitua 'caminho/para/seu/template.png' pelo caminho real de um template que você criou
# # Substitua 'RXCTB03EXVK' pelo ID do seu dispositivo
# # success, coords = find_and_confirm_click('acoes/sua_acao/01_template.png', device_id='RXCTB03EXVK')
# # if success:
# #     print(f"Imagem encontrada e clicada com sucesso nas coordenadas: {coords}.")
# # else:
# #     print("Imagem não encontrada ou falha ao clicar.")