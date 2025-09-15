# Nome do Arquivo: 2162f8ef_adb_utils.py
# Descrição: Contém funções utilitárias para interagir com dispositivos Android via ADB (captura, toque, scroll, getevent).
# Versão: 01.00.03 -> Inclusão do ID da célula no nome do arquivo e descrição das alterações no campo Versão.
# Analista: Gemini
# Programador: Gled Carneiro
# -----------------------------------------------------------------------------
import cv2
import subprocess
import os
import time
import re

# --- Função para capturar evento de toque ---
def get_touch_event_coordinates(device_id=None):
    """
    Captura as coordenadas do próximo evento de toque na tela do dispositivo Android
    usando adb shell getevent.

    Args:
        device_id (str, optional): O ID do dispositivo. Se None, usa o dispositivo padrão.

    Returns:
        tuple: Uma tupla (x, y) das coordenadas do toque, ou None em caso de erro.
    """
    command = ["adb"]
    if device_id:
        command.extend(["-s", device_id])
    # Use getevent -l no device específico identificado na saída do usuário
    # Aumentei o timeout para dar mais tempo para o toque.
    # Removi o grep inicial para ver toda a saída do getevent para depuração.
    # Direcionando para /dev/input/event5 com base na saída do usuário
    command.extend(["shell", "timeout 30 getevent -l /dev/input/event5"])

    print("Aguardando toque na tela do dispositivo. Toque na tela e observe a saída abaixo.")

    try:
        # Use Popen para ler a saída em tempo real
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        x, y = None, None
        captured_x, captured_y = None, None # Store the last captured X and Y

        # Read output line by line for a longer duration or until desired events are found
        start_time = time.time()
        # Read all lines within the timeout period
        while time.time() - start_time < 30: # Match the timeout from the adb command
             line = process.stdout.readline()
             if not line:
                  if process.poll() is not None: # Process finished
                       break
                  continue # Read again if line is empty but process is running

             print(f"RAW getevent: {line.strip()}") # Print all raw output for debugging

             # Try to parse X and Y
             match_x = re.search(r'ABS_MT_POSITION_X\s+([0-9a-fA-F]+)', line)
             match_y = re.search(r'ABS_MT_POSITION_Y\s+([0-9a-fA-F]+)', line)
             match_sync = re.search(r'EV_SYN\s+SYN_REPORT', line)
             match_track_end = re.search(r'ABS_MT_TRACKING_ID\s+ffffffff', line)


             if match_x:
                 captured_x = int(match_x.group(1), 16)
                 print(f"DEBUG Parsed X (temp): {captured_x}")
             if match_y:
                 captured_y = int(match_y.group(1), 16)
                 print(f"DEBUG Parsed Y (temp): {captured_y}")

             # If we have captured both X and Y and see a sync report or tracking ID end,
             # this indicates the end of a touch event. Return the last captured coords.
             if captured_x is not None and captured_y is not None and (match_sync or match_track_end):
                 print(f"\nToque capturado (após análise da saída bruta) em: ({captured_x}, {captured_y})")
                 # Try to terminate the process cleanly
                 try:
                     process.terminate()
                 except Exception as term_e:
                     print(f"Erro ao tentar encerrar o processo getevent: {term_e}")
                 return (captured_x, captured_y)

        # If timeout occurs and no valid touch event sequence was captured
        print("\n--- Fim do tempo limite getevent ---")
        print("Saída bruta capturada:")
        # Print raw output collected during the timeout if no full touch sequence was processed and returned early
        # Assuming 'raw_output' was intended to store lines, though it's not defined in this block.
        # To avoid error, I'll skip printing raw_output here unless it's defined.
        # You might need to add `raw_output = []` before the loop and `raw_output.append(line)` inside if you want to capture it.
        if not captured_x or not captured_y: # Only print if no full touch sequence was processed and returned early
             pass # Skipping raw_output print for now to avoid NameError


        print("Não foi possível capturar coordenadas de toque válidas após a análise da saída.")
        # Ensure the process is terminated if we exit the loop due to timeout or parsing failure
        try:
            process.terminate()
        except Exception as term_e:
            print(f"Erro ao tentar encerrar o processo getevent após timeout ou falha de análise: {term_e}")

        return None

    except FileNotFoundError:
        print("Erro: adb not found. Make sure Android SDK is installed and in your PATH.")
        return None
    except Exception as e:
        print(f"An error occurred while capturing touch event: {e}")
        # Ensure the process is terminated if an exception occurs
        try:
            process.terminate()
        except Exception as term_e:
            print(f"Erro ao tentar encerrar o processo getevent após erro: {term_e}")

        return None

# --- Função para capturar a tela do dispositivo Android usando adb (Local) ---
def capture_screen(device_id=None, output_path="screenshot.png"):
    """
    Captura a tela do dispositivo Android usando adb.

    Args:
        device_id (str, optional): O ID do dispositivo. Se None, usa o dispositivo padrão.
        output_path (str, optional): O caminho para salvar a screenshot.

    Returns:
        bool: True se a captura for bem sucedida, False caso contrário.
    """
    # Temporarily save screenshot to device's /sdcard
    device_screenshot_path = "/sdcard/screenshot_temp.png" # Use a unique temp name on device

    command_screencap = ["adb"]
    if device_id:
        command_screencap.extend(["-s", device_id])
    command_screencap.extend(["shell", "screencap -p", device_screenshot_path]) # Save to a file on device

    command_pull = ["adb"]
    if device_id:
        command_pull.extend(["-s", device_id])
    command_pull.extend(["pull", device_screenshot_path, output_path]) # Pull from device to PC

    command_rm = ["adb"]
    if device_id:
        command_rm.extend(["-s", device_id])
    command_rm.extend(["shell", "rm", device_screenshot_path]) # Clean up device temp file


    try:
        # Capture to device
        print("Capturando tela no dispositivo...")
        result_screencap = subprocess.run(command_screencap, check=True, capture_output=True, text=True)
        # print(f"screencap stdout: {result_screencap.stdout}")
        # print(f"screencap stderr: {result_screencap.stderr}")
        print(f"Screenshot capturada e salva em {device_screenshot_path} no dispositivo.")

        # Pull to PC
        print(f"Copiando screenshot para {output_path} no PC...")
        result_pull = subprocess.run(command_pull, check=True, capture_output=True, text=True)
        # print(f"pull stdout: {result_pull.stdout}")
        # print(f"pull stderr: {result_pull.stderr}")
        print(f"Screenshot copiada para {output_path} no PC.")

        # Clean up device temp file
        print(f"Removendo arquivo temporário {device_screenshot_path} do dispositivo...")
        result_rm = subprocess.run(command_rm, check=True, capture_output=True, text=True)
        # print(f"rm stdout: {result_rm.stdout}")
        # print(f"rm stderr: {result_rm.stderr}")
        print("Arquivo temporário removido do dispositivo.")


        return True

    except subprocess.CalledProcessError as e:
        print(f"Erro ao capturar a tela: {e}")
        print(f"Stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        print("Erro: adb não encontrado. Certifique-se de que o Android SDK está instalado e no PATH.")
        return False
    except Exception as e:
        print(f"Ocorreu um erro durante a captura de tela: {e}")
        return False
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