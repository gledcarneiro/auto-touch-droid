# Nome do Arquivo: eee823d0_action_executor.py
# Descrição: Contém a função principal para executar sequências de ações lidas de um arquivo sequence.json.
# Versão: 01.00.06 -> Adicionado tratamento para action_before_find e action_after_find. Adicionado initial_delay para templates. Adicionado click_offset. Melhorados logs.
# Analista: Gemini
# Programador: Gled Carneiro
# -----------------------------------------------------------------------------
import time
import os
import json
import re
import subprocess # Importar subprocess explicitamente

# Assumindo que você tem adb_utils.py e image_detection.py acessíveis
# Importe as funções necessárias
from adb_utils import capture_screen, simulate_touch

# Importando find_image_on_screen diretamente, pois find_and_optionally_click a utiliza
from image_detection import find_image_on_screen


def simulate_scroll(device_id=None, direction="up", duration_ms=500, start_coords=None, end_coords=None):
    """
    Simula um gesto de scroll na tela do dispositivo Android usando adb shell input swipe.

    Args:
        device_id (str, optional): O ID do dispositivo Android. Se None, usa o dispositivo padrão.
        direction (str, optional): A direção do scroll ('up' ou 'down'). Padrão é 'up'. Ignorado se start_coords e end_coords forem fornecidos.
        duration_ms (int, optional): Duração do gesto de swipe em milissegundos.
        start_coords (list, optional): Lista de 2 ints [x, y] para as coordenadas de início do swipe. Se fornecido, direction é ignorado.
        end_coords (list, optional): Lista de 2 ints [x, y] para as coordenadas de fim do swipe. Se fornecido, direction é ignorado.

    Note: Se start_coords e end_coords não forem fornecidos, o scroll usará coordenadas genéricas centrais baseadas em Landscape (2400x1080).
          AJUSTE estas coordenadas genéricas se a resolução do seu dispositivo for diferente.
    """
    final_start_x, final_start_y = 0, 0
    final_end_x, final_end_y = 0, 0

    if start_coords is not None and end_coords is not None and isinstance(start_coords, list) and len(start_coords) == 2 and isinstance(end_coords, list) and len(end_coords) == 2:
        # Usar coordenadas fornecidas
        final_start_x, final_start_y = start_coords
        final_end_x, final_end_y = end_coords
        print(f"Simulando scroll de coordenadas específicas: ({final_start_x}, {final_start_y}) para ({final_end_x}, {final_end_y})")
    else:
        # Usar coordenadas genéricas baseadas na direção (Landscape 2400x1080)
        landscape_width = 2400  # Largura em modo paisagem
        landscape_height = 1080 # Altura em modo paisagem
        center_x_landscape = landscape_width // 2

        if direction == "up":
            # Scroll para cima (conteúdo sobe): Gesto de baixo para cima na tela landscape.
            final_start_x, final_start_y = center_x_landscape, int(landscape_height * 0.8)
            final_end_x, final_end_y = center_x_landscape, int(landscape_height * 0.2)
            print(f"Simulando scroll genérico na direção 'up'.")
        elif direction == "down":
            # Scroll para baixo (conteúdo desce): Gesto de cima para baixo na tela landscape.
            final_start_x, final_start_y = center_x_landscape, int(landscape_height * 0.2)
            final_end_x, final_end_y = center_x_landscape, int(landscape_height * 0.8)
            print(f"Simulando scroll genérico na direção 'down'.")
        else:
            print(f"Aviso: Direção de scroll '{direction}' desconhecida e coordenadas não fornecidas. Pulando scroll.")
            return # Não executa o scroll se a configuração for inválida

    command = ["adb"]
    if device_id:
        command.extend(["-s", device_id])
    # input swipe <x1> <y1> <x2> <y2> [duration_ms]
    command.extend(["shell", "input", "swipe", str(final_start_x), str(final_start_y), str(final_end_x), str(final_end_y), str(duration_ms)])

    print(f"DEBUG simulate_scroll command: {' '.join(command)}")

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=(duration_ms / 1000.0) + 5) # Timeout um pouco maior que a duração do swipe
        print("Scroll simulado com sucesso.")
        # print(f"DEBUG simulate_scroll stdout: {result.stdout.strip()}") # Comentado para evitar muita verbosidade
        # print(f"DEBUG simulate_scroll stderr: {result.stderr.strip()}") # Comentado para evitar muita verbosidade

        # Adicionar um pequeno delay após o scroll para a tela se estabilizar
        time.sleep(duration_ms / 1000.0 + 0.5) # Espera a duração do swipe + 0.5s
    except subprocess.TimeoutExpired as e:
         print(f"Erro de timeout ao simular o scroll: {e.cmd}")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao simular o scroll: {e}")
        print(f"Stderr: {e.stderr.strip()}")
    except FileNotFoundError:
        print("Erro: adb não encontrado. Certifique-se de que o Android SDK está instalado e no PATH.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante a simulação do scroll: {e}")


# Função auxiliar para encontrar e, opcionalmente, clicar em um template com tentativas
def find_and_optionally_click(template_path, device_id=None, screenshot_path="temp_screenshot_for_find.png", max_attempts=1, attempt_delay=1, initial_delay=0):
    """
    Tenta encontrar um template em capturas de tela repetidas.

    Args:
        template_path (str): O caminho para o arquivo do template de imagem a ser procurado.
        device_id (str, optional): O ID do dispositivo Android. Se None, usa o dispositivo padrão.
        screenshot_path (str, optional): Caminho temporário para salvar a screenshot.
        max_attempts (int, optional): Número máximo de tentativas para encontrar o template.
        attempt_delay (float, optional): Tempo de espera em segundos entre as tentativas.
        initial_delay (float, optional): Tempo de espera em segundos antes da primeira tentativa.

    Returns:
        tuple: Retorna (True, (center_x, center_y)) se a imagem foi encontrada,
               (False, None) caso contrário. As coordenadas são None se não for encontrada.
    """
    print(f"Procurando template: {os.path.basename(template_path)}") # Printa só o nome do arquivo

    # Adicionar um atraso antes da primeira tentativa
    if initial_delay > 0:
        print(f"Aguardando {initial_delay} segundos antes da primeira tentativa...")
        time.sleep(initial_delay)

    # Ensure the directory for the temp screenshot exists
    temp_dir = os.path.dirname(screenshot_path)
    if temp_dir and not os.path.exists(temp_dir):
        try:
            os.makedirs(temp_dir)
            print(f"Diretório temporário criado: {temp_dir}")
        except OSError as e:
             print(f"Erro ao criar diretório temporário {temp_dir}: {e}. Usando o diretório atual para a screenshot temporária.")
             screenshot_path = os.path.basename(screenshot_path) # Fallback to current directory


    found_position = None # Initialize found_position outside the loop

    for attempt in range(1, max_attempts + 1):
        print(f"Tentativa {attempt}/{max_attempts} para encontrar o template '{os.path.basename(template_path)}'.")

        # 1. Capturar a tela
        if not capture_screen(device_id=device_id, output_path=screenshot_path):
            print(f"Falha ao capturar a tela na tentativa {attempt}. ")
            # Clean up temp screenshot if capture failed and left a file
            if os.path.exists(screenshot_path):
                try:
                    os.remove(screenshot_path)
                except PermissionError:
                     print(f"Aviso: Não foi possível remover o arquivo temporário '{screenshot_path}' devido a erro de permissão.")
                except Exception as e:
                     print(f"Aviso: Erro ao remover arquivo temporário '{screenshot_path}': {e}")

            if attempt < max_attempts:
                 print(f"Aguardando {attempt_delay} segundos antes da próxima tentativa...")
                 time.sleep(attempt_delay)
            continue # Tenta novamente se a captura falhou


        # 2. Procurar pela imagem (template) na screenshot
        # find_image_on_screen já lida com erros de leitura de arquivo de imagem dentro dela
        image_position = find_image_on_screen(screenshot_path, template_path)

        # Clean up temp screenshot after find_image_on_screen is done with it
        if os.path.exists(screenshot_path):
            try:
                os.remove(screenshot_path)
                # print(f"Arquivo temporário {screenshot_path} removido.") # Comentado para evitar muita verbosidade
            except PermissionError:
                 print(f"Aviso: Não foi possível remover o arquivo temporário '{screenshot_path}' devido a erro de permissão.")
            except Exception as e:
                 print(f"Aviso: Erro ao remover arquivo temporário '{screenshot_path}': {e}")


        # 3. Se a imagem for encontrada, retornar as coordenadas
        if image_position:
            x, y, w, h = image_position
            center_x = x + w // 2
            center_y = y + h // 2
            found_position = (True, (center_x, center_y))
            print(f"Template '{os.path.basename(template_path)}' encontrado na tentativa {attempt} em ({x}, {y}).")
            break # Sai do loop de tentativas se encontrar

        else:
            # print(f"Template '{os.path.basename(template_path)}' não encontrado na tentativa {attempt}.") # Comentado para evitar muita verbosidade
            if attempt < max_attempts:
                 print(f"Aguardando {attempt_delay} segundos antes da próxima tentativa...")
                 time.sleep(attempt_delay)
            # Continue o loop para a próxima tentativa se não for a última


    # Se o loop terminar (encontrou ou excedeu tentativas)
    if found_position:
        return found_position
    else:
        print(f"Template '{os.path.basename(template_path)}' não encontrado após {max_attempts} tentativas.")
        return (False, None) # Retorna False se o template não foi encontrado após todas as tentativas


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
            action_on_found = step_config.get("action_on_found", "click") # Default action is click
            click_delay = step_config.get("click_delay", 0.5) # Default delay
            click_offset = step_config.get("click_offset", [0, 0]) # Obter o offset do JSON, default [0, 0]
            max_attempts = step_config.get("max_attempts", 1) # Default 1 attempt
            attempt_delay = step_config.get("attempt_delay", 1.0) # Default 1 second delay between attempts
            initial_delay = step_config.get("initial_delay", 0) # Novo campo para atraso inicial

            if not template_filename:
                print(f"Erro: Passo {step_number} ('{step_name}') do tipo 'template' não especifica 'template_file'. Pulando passo.")
                continue # Pula para o próximo passo se faltar o template_file

            template_path = os.path.join(action_folder, template_filename)

            # --- Processar action_before_find ---
            action_before = step_config.get("action_before_find")
            if action_before and isinstance(action_before, dict):
                 before_type = action_before.get("type")
                 if before_type == "scroll":
                      scroll_direction = action_before.get("direction", "up")
                      scroll_duration = action_before.get("duration_ms", 500)
                      delay_after_scroll = action_before.get("delay_after_scroll", 0.5)
                      scroll_start_coords = action_before.get("start_coords") # Pode ser None
                      scroll_end_coords = action_before.get("end_coords") # Pode ser None

                      print(f"Executando ação antes de encontrar template: Scroll.")
                      simulate_scroll(
                          device_id=device_id,
                          direction=scroll_direction,
                          duration_ms=scroll_duration,
                          start_coords=scroll_start_coords, # Passa as coords específicas se existirem
                          end_coords=scroll_end_coords
                      )
                      time.sleep(delay_after_scroll) # Delay após o scroll

                 elif before_type == "wait":
                      wait_duration = action_before.get("duration_seconds")
                      if isinstance(wait_duration, (int, float)) and wait_duration > 0:
                          print(f"Executando ação antes de encontrar template: Esperando por {wait_duration} segundos.")
                          time.sleep(wait_duration)
                      else:
                          print(f"Aviso: Configuração inválida para action_before_find wait em {step_name}.")

                 else:
                      # Ignora chaves que começam com '#' (usadas para comentários no JSON)
                      if not before_type or not before_type.startswith("#"):
                           print(f"Aviso: Tipo de action_before_find '{before_type}' no {step_name} desconhecido/não implementado.")


            # --- Tentar encontrar o template ---
            # Usando a função find_and_optionally_click que inclui tentativas e atraso inicial
            found, coords = find_and_optionally_click(
                template_path,
                device_id=device_id,
                max_attempts=max_attempts,
                attempt_delay=attempt_delay,
                initial_delay=initial_delay # Passando o novo parâmetro
            )

            if found:
                if action_on_found == "click":
                    # Se o template foi encontrado, simulamos o clique usando as coordenadas retornadas
                    center_x, center_y = coords

                    # Aplicar o click_offset, se for uma lista válida de 2 elementos
                    if isinstance(click_offset, list) and len(click_offset) == 2:
                         final_click_x = center_x + click_offset[0]
                         final_click_y = center_y + click_offset[1]
                         print(f"Aplicando offset [{click_offset[0]}, {click_offset[1]}]. Clicando em ({final_click_x}, {final_click_y}).")
                         simulate_touch(final_click_x, final_click_y, device_id=device_id)
                    else:
                         # Validar se click_offset foi especificado mas não é uma lista de 2 ints
                         if "click_offset" in step_config:
                              print(f"Aviso: Configuração de click_offset inválida ({click_offset}) em {step_name}. Esperado [x, y].")
                         print(f"Clicando no centro do template ({center_x}, {center_y}).")
                         simulate_touch(center_x, center_y, device_id=device_id) # Clica no centro se o offset for inválido ou não especificado

                    if click_delay > 0:
                         time.sleep(click_delay)
                    print(f"{step_name} ({os.path.basename(template_path)}) concluído com sucesso (Template Encontrado, Clicado).")
                # TODO: Adicionar outros tipos de action_on_found aqui (ex: swipe a partir do template)
                else:
                    # Ignora chaves que começam com '#'
                    if not action_on_found or not action_on_found.startswith("#"):
                        print(f"Aviso: Tipo de action_on_found '{action_on_found}' no {step_name} desconhecido/não implementado. Template encontrado, mas ação não executada.")


            else:
                print(f"Erro: {step_name} ({os.path.basename(template_path)}) template NÃO encontrado após {max_attempts} tentativas.")
                # Por enquanto, paramos a execução se o template essencial não for encontrado
                # No futuro, podemos adicionar opções de fallback ou continuar dependendo da configuração
                print("Parando execução da ação devido a template não encontrado.")
                return # Sai da função de execução da ação


            # --- Processar action_after_find ---
            action_after = step_config.get("action_after_find")
            if action_after and isinstance(action_after, dict):
                 after_type = action_after.get("type")
                 if after_type == "scroll":
                      scroll_direction = action_after.get("direction", "down")
                      scroll_duration = action_after.get("duration_ms", 500)
                      delay_after_scroll_after = action_after.get("delay_after_scroll", 0.5) # Delay config for after scroll
                      scroll_start_coords = action_after.get("start_coords") # Pode ser None
                      scroll_end_coords = action_after.get("end_coords") # Pode ser None


                      print(f"Executando ação após encontrar template: Scroll.")
                      simulate_scroll(
                           device_id=device_id,
                           direction=scroll_direction,
                           duration_ms=scroll_duration,
                           start_coords=scroll_start_coords, # Passa as coords específicas se existirem
                           end_coords=scroll_end_coords
                      )
                      time.sleep(delay_after_scroll_after) # Delay após o scroll

                 elif after_type == "wait":
                      wait_duration = action_after.get("duration_seconds")
                      if isinstance(wait_duration, (int, float)) and wait_duration > 0:
                          print(f"Executando ação após encontrar template: Esperando por {wait_duration} segundos.")
                          time.sleep(wait_duration)
                      else:
                          print(f"Aviso: Configuração inválida para action_after_find wait em {step_name}.")


                 else:
                      # Ignora chaves que começam com '#'
                      if not after_type or not after_type.startswith("#"):
                           print(f"Aviso: Tipo de action_after_find '{after_type}' no {step_name} desconhecido/não implementado.")


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
             # Ignora chaves que começam com '#'
             if not step_type or not step_type.startswith("#"):
                  print(f"Erro: Passo {step_number} ('{step_name}') tem tipo '{step_type}' desconhecido ou faltando. Pulando passo.")
             continue # Pula para o próximo passo se o tipo for inválido/não implementado (ou for um comentário)

    print(f"\nExecução da ação '{action_name}' finalizada.")

# Removidos exemplos de uso direto. As funções agora são importadas e usadas em outros scripts.
# # Exemplo de uso (descomente para testar após criar a pasta da ação, templates e sequence.json):
# # action_to_execute = "coleta_item" # Substitua pelo nome da ação
# # device_id_execution = 'RXCTB03EXVK' # Substitua pelo ID do seu dispositivo
# # execultar_acoes(action_to_execute, device_id=device_id_execution)

# # Exemplo de teste da nova função simulate_scroll (descomente para testar):
# # device_id_scroll_test = 'RXCTB03EXVK' # Substitua pelo ID do seu dispositivo
# # print("\nTestando scroll para cima...")
# # simulate_scroll(device_id=device_id_scroll_test, direction="up", duration_ms=800)
# # print("\nTestando scroll para baixo...")
# # simulate_scroll(device_id=device_id_scroll_test, direction="down", duration_ms=800)
# # print("\nTestando scroll com coordenadas específicas (exemplo)...")
# # simulate_scroll(device_id=device_id_scroll_test, start_coords=[500, 800], end_coords=[500, 200], duration_ms=800)