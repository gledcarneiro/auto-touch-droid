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
        tuple: Uma tupla (x, y) das coordenadas do toque, ou None em caso de erro/timeout.
    """
    command = ["adb"]
    if device_id:
        command.extend(["-s", device_id])
    # Use getevent -l no device específico identificado na saída do usuário
    # Aumentei o timeout para dar mais tempo para o toque.
    # Removi o grep inicial para ver toda a saída do getevent para depuração.
    # Direcionando para /dev/input/event5 com base na saída do usuário
    # Reduzi o timeout para 15s, se 30s for muito longo em alguns casos. Ajuste conforme necessário.
    command.extend(["shell", "timeout 15 getevent -l /dev/input/event5"])

    print("Aguardando toque na tela do dispositivo. Toque na tela.")

    try:
        # Use Popen para ler a saída em tempo real
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        x, y = None, None
        captured_x, captured_y = None, None # Store the last captured X and Y

        # Read output line by line within the timeout period
        start_time = time.time()
        while time.time() - start_time < 15: # Match the timeout from the adb command
             line = process.stdout.readline()
             if not line:
                  if process.poll() is not None: # Process finished
                       break
                  continue # Read again if line is empty but process is running

             # print(f"RAW getevent: {line.strip()}") # Comentado para evitar muita verbosidade

             # Try to parse X and Y
             match_x = re.search(r'ABS_MT_POSITION_X\s+([0-9a-fA-F]+)', line)
             match_y = re.search(r'ABS_MT_POSITION_Y\s+([0-9a-fA-F]+)', line)
             match_sync = re.search(r'EV_SYN\s+SYN_REPORT', line)
             # match_track_end = re.search(r'ABS_MT_TRACKING_ID\s+ffffffff', line) # Nem sempre presente/confiável como SYN_REPORT


             if match_x:
                 captured_x = int(match_x.group(1), 16)
                 # print(f"DEBUG Parsed X (temp): {captured_x}") # Comentado para evitar muita verbosidade
             if match_y:
                 captured_y = int(match_y.group(1), 16)
                 # print(f"DEBUG Parsed Y (temp): {captured_y}") # Comentado para evitar muita verbosidade

             # If we have captured both X and Y and see a sync report,
             # this indicates the end of a touch event. Return the last captured coords.
             if captured_x is not None and captured_y is not None and match_sync:
                 print(f"\nToque capturado em: ({captured_x}, {captured_y})")
                 # Try to terminate the process cleanly
                 try:
                     process.terminate()
                     process.wait() # Wait for the process to actually terminate
                 except Exception as term_e:
                     print(f"Aviso: Erro ao tentar encerrar o processo getevent: {term_e}")
                 return (captured_x, captured_y)

        # If timeout occurs and no valid touch event sequence was captured
        print("\n--- Fim do tempo limite getevent ---")
        print("Não foi possível capturar coordenadas de toque válidas após a análise da saída dentro do tempo limite.")
        # Ensure the process is terminated if we exit the loop due to timeout or parsing failure
        try:
            process.terminate()
            process.wait() # Wait for the process to actually terminate
        except Exception as term_e:
            print(f"Aviso: Erro ao tentar encerrar o processo getevent após timeout ou falha de análise: {term_e}")

        return None

    except FileNotFoundError:
        print("Erro: adb not found. Make sure Android SDK is installed and in your PATH.")
        return None
    except Exception as e:
        print(f"An error occurred while capturing touch event: {e}")
        # Ensure the process is terminated if an exception occurs
        try:
            process.terminate()
            process.wait() # Wait for the process to actually terminate
        except Exception as term_e:
            print(f"Aviso: Erro ao tentar encerrar o processo getevent após erro: {term_e}")

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
    # Use a unique temp name on device to avoid conflicts if multiple instances run or fail to clean up
    device_screenshot_path = f"/sdcard/screenshot_temp_{os.getpid()}_{int(time.time())}.png"

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
        # Timeout for screencap command (e.g., 10 seconds)
        result_screencap = subprocess.run(command_screencap, check=True, capture_output=True, text=True, timeout=10)
        # print(f"screencap stdout: {result_screencap.stdout}") # Comentado para evitar muita verbosidade
        # print(f"screencap stderr: {result_screencap.stderr}") # Comentado para evitar muita verbosidade
        # print(f"Screenshot capturada e salva em {device_screenshot_path} no dispositivo.")

        # Pull to PC
        # print(f"Copiando screenshot para {output_path} no PC...")
        # Timeout for pull command (e.g., 10 seconds)
        result_pull = subprocess.run(command_pull, check=True, capture_output=True, text=True, timeout=10)
        # print(f"pull stdout: {result_pull.stdout}") # Comentado para evitar muita verbosidade
        # print(f"pull stderr: {result_pull.stderr}") # Comentado para evitar muita verbosidade
        # print(f"Screenshot copiada para {output_path} no PC.")

        # Clean up device temp file
        # print(f"Removendo arquivo temporário {device_screenshot_path} do dispositivo...")
        # Timeout for rm command (e.g., 5 seconds)
        result_rm = subprocess.run(command_rm, check=True, capture_output=True, text=True, timeout=5)
        # print(f"rm stdout: {result_rm.stdout}") # Comentado para evitar muita verbosidade
        # print(f"rm stderr: {result_rm.stderr}") # Comentado para evitar muita verbosidade
        # print("Arquivo temporário removido do dispositivo.")


        return True

    except subprocess.TimeoutExpired as e:
        print(f"Erro de timeout ao executar comando adb: {e.cmd}")
        if e.stderr:
            print(f"Stderr: {e.stderr.strip()}")
        # Attempt to clean up the temp file on the device even after a timeout
        try:
             subprocess.run(command_rm, timeout=5)
             print("Tentativa de remover arquivo temporário no dispositivo após timeout.")
        except Exception as rm_e:
             print(f"Aviso: Falha ao tentar remover arquivo temporário no dispositivo após timeout: {rm_e}")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Erro ao capturar a tela: {e}")
        if e.stderr:
            print(f"Stderr: {e.stderr.strip()}")
        # Attempt to clean up the temp file on the device even after an error
        try:
             subprocess.run(command_rm, timeout=5)
             print("Tentativa de remover arquivo temporário no dispositivo após erro.")
        except Exception as rm_e:
             print(f"Aviso: Falha ao tentar remover arquivo temporário no dispositivo após erro: {rm_e}")
        return False
    except FileNotFoundError:
        print("Erro: adb não encontrado. Certifique-se de que o Android SDK está instalado e no PATH.")
        return False
    except Exception as e:
        print(f"Ocorreu um erro durante a captura de tela: {e}")
        # Attempt to clean up the temp file on the device even after an unexpected error
        try:
             subprocess.run(command_rm, timeout=5)
             print("Tentativa de remover arquivo temporário no dispositivo após erro inesperado.")
        except Exception as rm_e:
             print(f"Aviso: Falha ao tentar remover arquivo temporário no dispositivo após erro inesperado: {rm_e}")
        return False

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
        # Adicionado um pequeno timeout para o comando adb input
        subprocess.run(command, check=True, timeout=5)
        # print(f"Toque simulado nas coordenadas ({x}, {y}).")
    except subprocess.TimeoutExpired as e:
        print(f"Erro de timeout ao simular o toque: {e.cmd}")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao simular o toque: {e}")
        if e.stderr:
            print(f"Stderr: {e.stderr.strip()}")
        # Lança exceção para ser capturada pelo sistema de reconexão
        raise
    except FileNotFoundError:
        print("Erro: adb não encontrado. Certifique-se de que o Android SDK está instalado e no PATH.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante a simulação do toque: {e}")


def get_action_sequence(action_folder_path):
    """
    Lista os arquivos de imagem (.png) em uma pasta de ação, ordenados pelo nome.
    (Esta função pode não ser mais estritamente necessária se a lógica for toda baseada no JSON)

    Args:
        action_folder_path (str): O caminho para a pasta contendo as imagens da sequência.
    """
    image_files = []
    if not os.path.isdir(action_folder_path):
        # print(f"Aviso: Pasta de ação não encontrada para listar imagens: {action_folder_path}") # Comentado, pois a lógica agora foca no JSON
        return image_files

    try:
        # Lista todos os arquivos na pasta
        files = os.listdir(action_folder_path)
        # Filtra apenas os arquivos .png e ordena pelo nome
        image_files = sorted([os.path.join(action_folder_path, f) for f in files if f.endswith('.png')])
    except Exception as e:
        print(f"Ocorreu um erro ao listar os arquivos .png na pasta {action_folder_path}: {e}")
        return []

    return image_files

# Removidos exemplos de uso direto. As funções agora são importadas e usadas em outros scripts.
# # Exemplo de uso:
# # capture_screen(device_id='RXCTB03EXVK', output_path='screenshot.png')
# # capture_screen(output_path='screenshot.png') # Usando o dispositivo padrão

# # if image_position:
# #     x, y, w, h = image_position
# #     center_x = x + w // 2
# #     center_y = y + h // 2
# #     simulate_touch(center_x, center_y, device_id='RXCTB03EXVK')

# # action_folder = "acoes/exemplo_acao"
# # sequence = get_action_sequence(action_folder)
# # print(f"Sequência de imagens encontrada: {sequence}")