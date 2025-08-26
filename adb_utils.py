import subprocess
import os

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

# Exemplo de uso:
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
    except subprocess.CalledCProcessError as e:
        print(f"Erro ao simular o toque: {e}")
    except FileNotFoundError:
        print("Erro: adb não encontrado. Certifique-se de que o Android SDK está instalado e no PATH.")

# Exemplo de uso:
# if image_position:
#     x, y, w, h = image_position
#     center_x = x + w // 2
#     center_y = y + h // 2
#     simulate_touch(center_x, center_y, device_id='RXCTB03EXVK')


def get_action_sequence(action_folder_path):
    """
    Lista os arquivos de imagem (.png) em uma pasta de ação, ordenados pelo nome.

    Args:
        action_folder_path (str): O caminho para a pasta contendo as imagens da sequência.
    """
    image_files = []
    if not os.path.isdir(action_folder_path):
        print(f"Erro: Pasta de ação não encontrada: {action_folder_path}")
        return image_files

    try:
        # Lista todos os arquivos na pasta
        files = os.listdir(action_folder_path)
        # Filtra apenas os arquivos .png e ordena pelo nome
        image_files = sorted([os.path.join(action_folder_path, f) for f in files if f.endswith('.png')])
    except Exception as e:
        print(f"Ocorreu um erro ao listar os arquivos na pasta {action_folder_path}: {e}")
        return []

    return image_files

# Exemplo de uso:
# Crie uma pasta chamada 'acoes/exemplo_acao' e coloque alguns arquivos .png nela
# action_folder = "acoes/exemplo_acao"
# sequence = get_action_sequence(action_folder)
# print(f"Sequência de imagens encontrada: {sequence}")

# Você precisará criar a pasta e os arquivos de imagem de exemplo para testar