import time
# Assumindo que você salvou as funções em adb_utils.py e image_detection.py
from adb_utils import capture_screen, simulate_touch
from image_detection import find_image_on_screen

# Configurações
device_id = 'RXCTB03EXVK'  # Substitua pelo ID do seu dispositivo, se necessário
screenshot_file = "screenshot.png"
template_file = "template.png"
delay_seconds = 2  # Tempo de espera entre as iterações do loop

import subprocess

print("Iniciando o AutoTouchDroid...")

while True:
    print("\nCapturando tela...")
    capture_screen(device_id=device_id, output_path=screenshot_file)

    print("Procurando imagem...")
    image_position = find_image_on_screen(screenshot_file, template_file)

    if image_position:
        x, y, w, h = image_position
        center_x = x + w // 2
        center_y = y + h // 2
        print(f"Imagem encontrada. Simulando toque em ({center_x}, {center_y}).")
        simulate_touch(center_x, center_y, device_id=device_id)
    else:
        print("Imagem não encontrada. Nenhum toque simulado.")

    print(f"Aguardando {delay_seconds} segundos...")
    time.sleep(delay_seconds)