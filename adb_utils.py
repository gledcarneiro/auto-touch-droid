import subprocess

def capture_screen(device_id=None, output_path="screenshot.png"):
    """
    Captura a tela do dispositivo Android usando adb.

    Args:
        device_id (str, optional): O ID do dispositivo. Se None, usa o dispositivo padrão.
        output_path (str, optional): O caminho para salvar a screenshot.
    """
    command = ["adb"]
    if device_id:
        command.extend(["-s", device_id])
    command.extend(["exec-out", "screencap -p > /sdcard/screenshot.png"])

    try:
        subprocess.run(command, check=True)
        print(f"Screenshot capturada e salva em /sdcard/screenshot.png no dispositivo.")

        # Pull the screenshot from the device to the local machine
        pull_command = ["adb"]
        if device_id:
            pull_command.extend(["-s", device_id])
        pull_command.extend(["pull", "/sdcard/screenshot.png", output_path])

        subprocess.run(pull_command, check=True)
        print(f"Screenshot copiada para {output_path} no PC.")

    except subprocess.CalledProcessError as e:
        print(f"Erro ao capturar a tela: {e}")
    except FileNotFoundError:
        print("Erro: adb não encontrado. Certifique-se de que o Android SDK está instalado e no PATH.")


# Exemplo de uso (substitua 'YOUR_DEVICE_ID' pelo ID do seu dispositivo, se tiver mais de um)
# capture_screen(device_id='RXCTB03EXVK', output_path='screenshot.png')
# capture_screen(output_path='screenshot.png') # Usando o dispositivo padrão

def simulate_touch(x, y, device_id=None):
    """
    Simula um toque na tela do dispositivo Android usando adb.

    Args:
        x (int): Coordenada X do toque.
        y (int): Coordenada Y do toque.
        device_id (str, optional): O ID do dispositivo. Se None, usa o dispositivo padrão.
    """
    command = ["adb"]
    if device_id:
        command.extend(["-s", device_id])
    # O comando 'input tap' simula um toque nas coordenadas (x, y)
    command.extend(["shell", "input", "tap", str(x), str(y)])

    try:
        subprocess.run(command, check=True)
        print(f"Toque simulado nas coordenadas ({x}, {y}).")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao simular o toque: {e}")
    except FileNotFoundError:
        print("Erro: adb não encontrado. Certifique-se de que o Android SDK está instalado e no PATH.")

# Exemplo de uso (substitua as coordenadas X e Y e o device_id, se necessário)
# simulate_touch(500, 800, device_id='YOUR_DEVICE_ID')
# Para usar com as coordenadas do centro da imagem detectada na célula anterior:
# if image_position:
#     x, y, w, h = image_position
#     center_x = x + w // 2
#     center_y = y + h // 2
#     simulate_touch(center_x, center_y)