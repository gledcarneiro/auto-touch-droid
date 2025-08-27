import cv2
import subprocess
import os
import time
import re

# --- Funções auxiliares (reutilizando do adb_utils, se estiverem em arquivos separados, importe-as) ---
# Mantendo get_action_sequence e simulate_touch importados, mas movendo capture_screen localmente
from adb_utils import simulate_touch, get_action_sequence

# --- Configurações do Dispositivo ---
# Ajuste estes valores de acordo com a resolução do seu dispositivo e o range de getevent
DEVICE_SCREEN_WIDTH = 1080  # Largura da tela em pixels
DEVICE_SCREEN_HEIGHT = 2400 # Altura da tela em pixels

# Estes são valores de exemplo do range MÁXIMO que o getevent pode reportar para X e Y.
# Você pode precisar ajustar estes valores com base na saída de 'adb shell getevent -l /dev/input/event5'
# tocando nos cantos superior esquerdo e inferior direito da tela.
# Para o toque (3282, 4010) em uma tela de 1080x2400, esses ranges parecem maiores que 4096.
# Como ponto de partida, vamos tentar estimar os fatores de escala usando o toque capturado.
# No entanto, é altamente recomendável determinar o range máximo real do getevent.
# Exemplo de como calcular o range máximo:
# Execute adb shell getevent -l /dev/input/event5
# Toque no canto superior esquerdo: observe o menor X e menor Y
# Toque no canto inferior direito: observe o maior X e maior Y
# USE ESSES VALORES PARA DEFINIR GETEVENT_MAX_X e GETEVENT_MAX_Y ABAIXO.
# Por enquanto, usaremos valores de exemplo que parecem compatíveis com o toque visto.
# Vamos usar 4095 como um chute educado para o range máximo, mas pode precisar de ajuste.
GETEVENT_MAX_X = 4085 # Exemplo, ajuste com base nos seus testes
GETEVENT_MAX_Y = 4075 # Exemplo, ajuste com base nos seus testes

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
        # Print raw output collected during the timeout if no touch was fully detected
        if not captured_x or not captured_y: # Only print if no full touch sequence was processed and returned early
            # Limit printing of raw output to avoid flooding if it's very long
            for i, line in enumerate(raw_output):
                if i < 100: # Print up to 100 lines
                    print(line)
                elif i == 100:
                    print("...(output truncated)...")
                    break
            print("--- Fim da saída bruta ---")

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


# --- Script Principal para Captura e Criação de Templates via Toque ---

def create_action_template_by_touch(action_folder, device_id=None, template_size=(100, 100)):
    """
    Script auxiliar para capturar a tela do Android e permitir a seleção e salvamento
    de templates de imagem em uma pasta de ação usando toques na tela do dispositivo.

    Args:
        action_folder (str): O caminho para a pasta onde os templates serão salvos.
                             A pasta será criada se não existir.
        device_id (str, optional): O ID do dispositivo Android.
        template_size (tuple, optional): O tamanho (largura, altura) da área a ser
                                         recortada ao redor do ponto de toque. Padrão é (100, 100).
    """
    if not os.path.exists(action_folder):
        os.makedirs(action_folder)
        print(f"Pasta de ação '{action_folder}' criada.")

    print(f"\n--- Modo de criação de templates por toque para a ação: {action_folder} ---")
    print("Prepare a tela do seu dispositivo Android para o próximo passo da ação.")
    print("Pressione 'Enter' no terminal para capturar a tela e depois toque no local do template.")
    print("Pressione 'q' e depois 'Enter' para sair.")

    step_counter = 1
    # Determine the next sequential filename based on existing files
    existing_files = get_action_sequence(action_folder)
    if existing_files:
        last_file = os.path.basename(existing_files[-1])
        try:
            # Extract the number from the filename (e.g., 01_template.png)
            last_num_match = re.match(r'(\d+)_', last_file)
            if last_num_match:
                last_num = int(last_num_match.group(1))
                step_counter = last_num + 1
            else:
                 print("Aviso: Não foi possível determinar o próximo número sequencial a partir dos nomes de arquivos existentes. Iniciando do 1.")
                 step_counter = 1 # Reset if file names don't follow the pattern
        except (ValueError, IndexError):
             print("Aviso: Não foi possível determinar o próximo número sequencial a partir dos nomes de arquivos existentes. Iniciando do 1.")
             step_counter = 1 # Reset on error

    while True:
        user_input = input(f"Pronto para o template (Passo {step_counter})? Pressione Enter ou 'q' para sair: ")

        if user_input.lower() == 'q':
            print("Saindo do modo de criação de templates.")
            break
        elif user_input == '':
            screenshot_temp_path = "screenshot_temp_for_template_touch.png"
            print("\nCapturando tela para seleção...")
            # Use the local capture_screen function
            if capture_screen(device_id=device_id, output_path=screenshot_temp_path):
                print(f"Screenshot capturada e salva em {screenshot_temp_path}.")

                # >>> Call the function to wait for touch coordinates <<<
                # Now we wait for touch AFTER capturing the screenshot
                print("AGORA, toque na tela do dispositivo no centro da área que você quer usar como template.")
                touch_coords = get_touch_event_coordinates(device_id=device_id)

                # --- Moved the file removal logic here ---
                # Remove the temporary screenshot file ONLY if touch capture failed
                # If touch capture succeeded, we need the file for cropping.
                # The file will be removed AFTER successful cropping and saving.
                if touch_coords is None and os.path.exists(screenshot_temp_path):
                     os.remove(screenshot_temp_path)
                     print(f"Arquivo temporário {screenshot_temp_path} removido, pois o toque não foi capturado.")


                if touch_coords:
                    center_x_raw, center_y_raw = touch_coords
                    print(f"Toque RAW capturado em: ({center_x_raw}, {center_y_raw})")

                    # Load the screenshot captured moments before the touch
                    # The file should still exist here because we only remove it if touch_coords is None
                    original_img = cv2.imread(screenshot_temp_path)
                    if original_img is not None:
                        img_height, img_width, _ = original_img.shape
                        print(f"DEBUG Screenshot size: {img_width}x{img_height}")

                        # --- Coordinate Scaling/Adjustment ---
                        # These scaling factors are ESTIMATES. You might need to adjust them
                        # based on the actual range of getevent coordinates on your device.
                        # A better approach is to determine GETEVENT_MAX_X and GETEVENT_MAX_Y
                        # by touching corners and calculating:
                        # scale_x = DEVICE_SCREEN_WIDTH / GETEVENT_MAX_X
                        # scale_y = DEVICE_SCREEN_HEIGHT / GETEVENT_MAX_Y

                        # As a starting point, let's assume a common getevent range (e.g., 0-4095)
                        # and see how it works, or use the touch coords to estimate range if needed.
                        # Based on your previous touch (3282, 4010), the range seems larger than 4095.
                        # Let's try a direct ratio based on the captured touch and screen size as a first guess.
                        # NOTE: This might be inaccurate if the touch wasn't exactly in the middle or near max bounds.
                        # We'll use the GETEVENT_MAX_X/Y variables defined at the top, which you should ideally set.
                        scale_x = DEVICE_SCREEN_WIDTH / GETEVENT_MAX_X if GETEVENT_MAX_X > 0 else 1
                        scale_y = DEVICE_SCREEN_HEIGHT / GETEVENT_MAX_Y if GETEVENT_MAX_Y > 0 else 1

                        # Apply the scaling
                        adjusted_x = int(center_x_raw * scale_x)
                        adjusted_y = int(center_y_raw * scale_y)

                        # Ensure adjusted coordinates are within screen bounds
                        adjusted_x = max(0, min(adjusted_x, img_width - 1))
                        adjusted_y = max(0, min(adjusted_y, img_height - 1))

                        print(f"DEBUG Adjusted coordinates (based on screen size {DEVICE_SCREEN_WIDTH}x{DEVICE_SCREEN_HEIGHT} and assumed getevent range {GETEVENT_MAX_X}x{GETEVENT_MAX_Y}): ({adjusted_x}, {adjusted_y})")


                        # Calculate the cropping region based on adjusted touch coordinates and template size
                        template_w, template_h = template_size

                        # Ensure the crop region is within the image boundaries
                        # Using adjusted_x and adjusted_y as the center point for cropping
                        x1 = max(0, adjusted_x - template_w // 2)
                        y1 = max(0, adjusted_y - template_h // 2)
                        x2 = min(img_width, adjusted_x + template_w // 2)
                        y2 = min(img_height, adjusted_y + template_h // 2)

                         # Adjust crop region size if it hit boundaries
                         # This is important to try and get a template of the desired size
                        if (x2 - x1) < template_w:
                            x1 = max(0, x2 - template_w)
                        if (y2 - y1) < template_h:
                            y1 = max(0, y2 - template_h)
                        # Re-calculate x2 and y2 based on adjusted x1, y1 and desired size
                        x2 = x1 + template_w
                        y2 = y1 + template_h

                        # Final check to ensure bounds are not exceeded after adjustment
                        x2 = min(img_width, x2)
                        y2 = min(img_height, y2)
                        x1 = min(x1, x2 - template_w) # Ensure x1 is not greater than x2 adjusted by template_w
                        y1 = min(y1, y2 - template_h) # Ensure y1 is not greater than y2 adjusted by template_h

                        # Ensure crop coordinates are valid (non-negative)
                        x1 = max(0, x1)
                        y1 = max(0, y1)

                        print(f"DEBUG Cropping region: ({x1}, {y1}, {x2}, {y2})")


                        # Perform the crop
                        # Ensure crop coordinates are valid before slicing
                        if y1 >= 0 and y2 <= img_height and x1 >= 0 and x2 <= img_width and y2 > y1 and x2 > x1:
                             cropped_img = original_img[y1:y2, x1:x2]

                             # Ensure the cropped image is not empty
                             if cropped_img.shape[0] > 0 and cropped_img.shape[1] > 0:
                                 # Format the filename (e.g., 01_template.png, 02_template.png)
                                 template_filename = f"{step_counter:02d}_template.png"
                                 template_save_path = os.path.join(action_folder, template_filename)

                                 cv2.imwrite(template_save_path, cropped_img)
                                 print(f"Template salvo como: {template_save_path}")
                                 step_counter += 1 # Increment only on successful save

                                 # --- Remove the temporary screenshot file AFTER successful save ---
                                 if os.path.exists(screenshot_temp_path):
                                      os.remove(screenshot_temp_path)
                                      print(f"Arquivo temporário {screenshot_temp_path} removido após salvar template.")
                             else:
                                  print(f"Erro: Imagem recortada vazia ou inválida. Verifique as coordenadas de recorte.")
                                  # Keep temp file for debugging if crop resulted in empty image
                                  print(f"Manter arquivo temporário {screenshot_temp_path} para depuração.")

                        else:
                             print(f"Erro: Coordenadas de recorte calculadas são inválidas: ({x1}, {y1}, {x2}, {y2}). Verifique o ponto de toque e o tamanho do template.")
                             # Keep temp file for debugging if crop coordinates were invalid
                             print(f"Manter arquivo temporário {screenshot_temp_path} para depuração.")


                    else:
                        print("Erro: Não foi possível recarregar a screenshot para recortar. O arquivo pode ter sido removido prematuramente ou houve outro problema.")
                        # Keep temp file for debugging if load failed
                        print(f"Manter arquivo temporário {screenshot_temp_path} para depuração, pois o carregamento da screenshot falhou.")


                else:
                    print("Não foi possível capturar as coordenadas do toque. O template não foi salvo.")
                    # Note: File removal for failed touch capture is handled above


        else:
            print("Entrada inválida. Pressione Enter ou 'q'.")

# Exemplo de uso do script auxiliar:
# Crie uma pasta para a nova ação, por exemplo 'acoes/nova_acao'
action_folder_name = "acoes/nova_acao_toque"
create_action_template_by_touch(action_folder_name, device_id='RXCTB03EXVK', template_size=(100, 100)) # Substitua pelo seu device_id