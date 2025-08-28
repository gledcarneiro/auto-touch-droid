import time
import os
import json
import re
import subprocess # Importar subprocess explicitamente

# Assumindo que você tem adb_utils.py e image_detection.py acessíveis
# Importe as funções necessárias
from adb_utils import capture_screen, simulate_touch

# Importando find_image_on_screen diretamente, pois find_and_confirm_click a utiliza
from image_detection import find_image_on_screen


def simulate_scroll(device_id=None, direction="up", duration_ms=500):
    """
    Simula um gesto de scroll na tela do dispositivo Android usando adb shell input swipe.
    Assume uma posição inicial/final central para o scroll. Pode precisar de refinamento.

    Args:
        device_id (str, optional): O ID do dispositivo Android. Se None, usa o dispositivo padrão.
        direction (str, optional): A direção do scroll ('up' ou 'down'). Padrão é 'up'.
        duration_ms (int, optional): Duração do gesto de swipe em milissegundos.

    Note: As coordenadas de início/fim do swipe abaixo são exemplos.
          Você pode precisar ajustá-las com base na resolução e orientação do seu dispositivo
          para cobrir a área que você quer rolar. Estas são apenas para um scroll "genérico".
          Para scrolls mais precisos, talvez precisemos de coordenadas fixas de início/fim.
          Considerando o dispositivo DEITADO (Landscape).
    """
    # Usando dimensões típicas para um dispositivo em Landscape (Ex: 1080p de altura na vertical vira 1080 de largura, e 2400 de largura vira 2400 de altura)
    # AJUSTE estes valores para a resolução real do seu dispositivo em LANDSCAPE.
    # Ex: 1080x2400 portrait -> 2400x1080 landscape
    landscape_width = 2400  # Largura em modo paisagem
    landscape_height = 1080 # Altura em modo paisagem

    # Para scroll vertical em Landscape, o gesto é ao longo do eixo Y, no centro X.
    center_x_landscape = landscape_width // 2

    swipe_start_y = 0
    swipe_end_y = 0

    if direction == "up":
        # Scroll para cima (conteúdo sobe): Gesto de baixo para cima na tela landscape.
        # Do Y maior para o Y menor, no centro X.
        swipe_start_y = int(landscape_height * 0.8) # Y maior (parte inferior da tela landscape)
        swipe_end_y = int(landscape_height * 0.2)   # Y menor (parte superior da tela landscape)
    elif direction == "down":
        # Scroll para baixo (conteúdo desce): Gesto de cima para baixo na tela landscape.
        # Do Y menor para o Y maior, no centro X.
        swipe_start_y = int(landscape_height * 0.2) # Y menor (parte superior da tela landscape)
        swipe_end_y = int(landscape_height * 0.8)   # Y maior (parte inferior da tela landscape)
    else:
        print(f"Aviso: Direção de scroll '{direction}' desconhecida. Usando 'up'.")
        direction = "up"
        swipe_start_y = int(landscape_height * 0.8)
        swipe_end_y = int(landscape_height * 0.2)


    command = ["adb"]
    if device_id:
        command.extend(["-s", device_id])
    # input swipe <x1> <y1> <x2> <y2> [duration_ms]
    # Passando as coordenadas na ordem correta: início X, início Y, fim X, fim Y
    command.extend(["shell", "input", "swipe", str(center_x_landscape), str(swipe_start_y), str(center_x_landscape), str(swipe_end_y), str(duration_ms)])

    print(f"Simulando scroll na direção '{direction}' com duração de {duration_ms}ms...")
    print(f"DEBUG simulate_scroll command: {' '.join(command)}") # Print the exact command


    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("Scroll simulado com sucesso.")
        print(f"DEBUG simulate_scroll stdout: {result.stdout.strip()}") # Print stdout
        print(f"DEBUG simulate_scroll stderr: {result.stderr.strip()}") # Print stderr

        # Adicionar um pequeno delay após o scroll para a tela se estabilizar
        time.sleep(duration_ms / 1000.0 + 0.5) # Espera a duração do swipe + 0.5s
    except subprocess.CalledProcessError as e:
        print(f"Erro ao simular o scroll: {e}")
        print(f"Stderr: {e.stderr}")
    except FileNotFoundError:
        print("Erro: adb não encontrado. Certifique-se de que o Android SDK está instalado e no PATH.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante a simulação do scroll: {e}")


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
    # find_image_on_screen já lida com erros de leitura de arquivo de imagem dentro dela
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
        return (False, None)


def execultar_acoes(action_name, device_id=None):
    """
    Executa uma sequência de ações lendo um arquivo sequence.json
    na pasta da ação, onde cada item no JSON define um passo
    (template matching, clique, scroll, etc.).

    Args:
        action_name (str): O nome da ação a ser executada (corresponde ao nome da pasta).
        device_id (str, optional): O ID do dispositivo Android.
    """
    action_folder = os.path.join("acoes", action_name)
    sequence_filepath = os.path.join(action_folder, "sequence.json")

    if not os.path.isdir(action_folder):
        print(f"Erro: Pasta de ação '{action_folder}' não encontrada.")
        return

    if not os.path.exists(sequence_filepath):
        print(f"Erro: Arquivo de sequência '{sequence_filepath}' não encontrado.")
        print("Certifique-se de que você criou e configurou o arquivo sequence.json para esta ação.")
        return

    # Carregar a sequência de ações do arquivo JSON
    try:
        with open(sequence_filepath, 'r', encoding='utf-8') as f:
            action_sequence = json.load(f)
        print(f"Sequência de ações carregada de: {sequence_filepath}")

        if not isinstance(action_sequence, list):
             print(f"Erro: O conteúdo do arquivo '{sequence_filepath}' não é uma lista.")
             return
        if not action_sequence:
             print(f"Aviso: A lista de ações no arquivo '{sequence_filepath}' está vazia. Nenhuma ação para executar.")
             return


    except json.JSONDecodeError:
        print(f"Erro ao decodificar o arquivo JSON '{sequence_filepath}'. Verifique a sintaxe.")
        return
    except Exception as e:
        print(f"Ocorreu um erro ao carregar o arquivo de sequência '{sequence_filepath}': {e}")
        return

    print(f"\nExecutando a ação: {action_name}")

    for i, step_config in enumerate(action_sequence):
        step_number = i + 1
        step_name = step_config.get("name", f"Passo {step_number}") # Usar nome do JSON ou default

        print(f"\n--- Executando {step_name} ---")

        step_type = step_config.get("type")

        if step_type == "template":
            template_filename = step_config.get("template_file")
            action_on_found = step_config.get("action_on_found")
            click_delay = step_config.get("click_delay", 0.5) # Default delay

            if not template_filename:
                print(f"Erro: Passo {step_number} ('{step_name}') do tipo 'template' não especifica 'template_file'. Pulando passo.")
                continue # Pula para o próximo passo se faltar o template_file

            template_path = os.path.join(action_folder, template_filename)

            # --- Processar action_before_find ---
            print(f"DEBUG: Verificando action_before_find para {step_name}...") # Debug print
            action_before = step_config.get("action_before_find")
            if action_before and isinstance(action_before, dict):
                 before_type = action_before.get("type")
                 if before_type == "scroll":
                      scroll_direction = action_before.get("direction", "up")
                      scroll_duration = action_before.get("duration_ms", 500)
                      # Permitir configurar o delay após o scroll no JSON
                      delay_after_scroll = action_before.get("delay_after_scroll", 0.5) # Default 0.5s

                      print(f"DEBUG: action_before_find detectado: type='scroll', direction='{scroll_direction}', duration_ms={scroll_duration}, delay_after_scroll={delay_after_scroll}") # Debug print

                      # Add a small delay BEFORE the scroll command
                      print("DEBUG: Adicionando delay de 0.2s ANTES do scroll.") # Debug print
                      time.sleep(0.2) # Small delay before scrolling


                      print(f"Executando ação antes de encontrar template: Scroll na direção '{scroll_direction}'.")
                      # Chamar a nova função de scroll
                      simulate_scroll(device_id=device_id, direction=scroll_direction, duration_ms=scroll_duration)
                      # Adicionar o delay CONFIGURÁVEL após o scroll
                      print(f"DEBUG: Adicionando delay de {delay_after_scroll}s após o scroll.") # Debug print
                      time.sleep(delay_after_scroll)


                 # TODO: Adicionar outros tipos de actions_before_find here (ex: wait)
                 else:
                      print(f"Aviso: Tipo de action_before_find '{before_type}' no {step_name} desconhecido/não implementado.")


            # --- Tentar encontrar o template e executar a ação ---
            print(f"DEBUG: Chamando find_and_confirm_click para {template_filename}...") # Debug print
            success, coords = find_and_confirm_click(template_path, device_id=device_id, click_delay=click_delay)

            if success:
                if action_on_found == "click":
                    # simulate_touch já foi chamado dentro de find_and_confirm_click
                    print(f"{step_name} ({template_filename}) concluído com sucesso.")
                # TODO: Adicionar outros tipos de action_on_found aqui (ex: swipe a partir do template)
                else:
                    print(f"Aviso: Tipo de action_on_found '{action_on_found}' no {step_name} desconhecido/não implementado.")
                    print(f"{step_name} ({template_filename}) template encontrado, mas ação desconhecida.")

            else:
                print(f"Erro: {step_name} ({template_filename}) template NÃO encontrado.")
                # TODO: Implementar lógica de tentativas (max_attempts) ou fallbacks aqui
                # Por enquanto, paramos a execução como antes
                print("Parando execução da ação devido a template não encontrado.")
                break # Para a execução se o template não for encontrado


        # TODO: Adicionar outros tipos de passo aqui (ex: type="coords", type="wait")
        elif step_type == "coords":
             # Implementar lógica para clicar em coordenadas diretas
             coords = step_config.get("coordinates")
             click_delay_coords = step_config.get("click_delay", 0.5)
             if isinstance(coords, list) and len(coords) == 2:
                  x, y = coords
                  print(f"Executando {step_name}: Clicar em coordenadas diretas ({x}, {y}).")
                  simulate_touch(x, y, device_id=device_id)
                  if click_delay_coords > 0:
                       time.sleep(click_delay_coords)
                  print(f"{step_name} (coordenadas diretas) concluído com sucesso.")
             else:
                  print(f"Erro: Passo {step_number} ('{step_name}') do tipo 'coords' não especifica 'coordinates' válidas ([x, y]). Pulando passo.")


        elif step_type == "wait":
             # Implementar lógica para esperar um tempo fixo
             wait_time = step_config.get("duration_seconds")
             if isinstance(wait_time, (int, float)) and wait_time > 0:
                  print(f"Executando {step_name}: Esperando por {wait_time} segundos.")
                  time.sleep(wait_time)
                  print(f"{step_name} (espera) concluído com sucesso.")
             else:
                  print(f"Erro: Passo {step_number} ('{step_name}') do tipo 'wait' não especifica 'duration_seconds' válida. Pulando passo.")


        else:
            print(f"Erro: Passo {step_number} ('{step_name}') tem tipo '{step_type}' desconhecido ou faltando. Pulando passo.")
            continue # Pula para o próximo passo se o tipo for inválido

    print(f"\nExecução da ação '{action_name}' finalizada.")


# Exemplo de uso (descomente para testar após criar a pasta da ação, templates e sequence.json):
action_to_execute = "coleta_item" # Substitua pelo nome da ação
device_id_execution = 'RXCTB03EXVK' # Substitua pelo ID do seu dispositivo
execultar_acoes(action_to_execute, device_id=device_id_execution)

# Exemplo de teste da nova função simulate_scroll (descomente para testar):
# device_id_scroll_test = 'RXCTB03EXVK' # Substitua pelo ID do seu dispositivo
# print("\nTestando scroll para cima...")
# simulate_scroll(device_id=device_id_scroll_test, direction="up", duration_ms=800)
# print("\nTestando scroll para baixo...")
# simulate_scroll(device_id=device_id_scroll_test, direction="down", duration_ms=800)