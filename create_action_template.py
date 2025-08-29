# Nome do Arquivo: 42427df3_create_action_template.py
# Descrição: Contém funções auxiliares para criar templates de imagem manualmente e gravar sequências assistidas.
# Versão: 01.00.04 -> Inclusão de valores default para action_before_find e action_after_find em passos template gravados.
# Analista: Gemini
# Programador: Gled Carneiro
# -----------------------------------------------------------------------------
import cv2
import subprocess
import os
import time
import re
import shutil # Importar shutil para copiar arquivos
import json # Importar json para lidar com arquivos de sequência

# --- Funções auxiliares ---
# Assumindo que adb_utils.py e action_executor.py estão acessíveis para importar
from adb_utils import simulate_touch, get_touch_event_coordinates, capture_screen
# from action_executor import find_and_confirm_click # Removido temporariamente se a lógica for separada

# --- Configurações do Dispositivo ---
# Mantenho as configurações de getevent aqui por referência, embora não afetem diretamente a gravação de templates ou JSON
# As coordenadas de toque RAW do getevent (se usadas para gravar coords diretas) precisam ser ajustadas.
DEVICE_SCREEN_WIDTH = 2400 # Largura da tela em pixels (na orientação deitada, largura é a altura na retrato)
DEVICE_SCREEN_HEIGHT = 1080 # Altura da tela em pixels (na orientação deitada, altura é a largura na retrato)
GETEVENT_MAX_X = 4584 # Ajuste com base nos seus testes (maior X observado no teste central)
GETEVENT_MAX_Y = 4218 # Ajuste com base nos seus testes (maior Y observado no teste central)
# --- Fim das Configurações do Dispositivo ---


# --- Função para criar template manualmente (recortando de screenshot) ---
def create_action_template_manual_crop(action_name, step_number, device_id=None):
    """
    Captura a tela do dispositivo, salva como screenshot_temp_<step_number>.png
    e instrui o usuário a recortar a imagem do template manualmente, salvando-a
    com um nome sequencial na pasta da ação.

    Args:
        action_name (str): O nome da ação (será usado para criar/acessar a pasta).
        step_number (int): O número do passo atual na sequência (usado para nomes de arquivo).
        device_id (str, optional): O ID do dispositivo Android.

    Returns:
        str: O caminho completo para o arquivo de template criado, ou None em caso de falha.
    """
    action_folder = os.path.join("acoes", action_name)
    if not os.path.exists(action_folder):
        os.makedirs(action_folder)
        print(f"Pasta de ação '{action_folder}' criada/verificada.")

    screenshot_temp_path = os.path.join(action_folder, f"screenshot_temp_{step_number:02d}.png") # Screenshot temporária na pasta da ação
    template_manual_path = os.path.join(action_folder, f"template_step_{step_number:02d}.png") # Nome sugerido para o template manual

    print(f"\n--- Criando Template Manual para o Passo {step_number} da ação '{action_name}' ---")
    print("Prepare a tela do seu dispositivo para o estado deste passo.")
    input("Pressione 'Enter' para capturar a tela para criar o template...")

    if capture_screen(device_id=device_id, output_path=screenshot_temp_path):
        print(f"\nScreenshot capturada e salva como '{screenshot_temp_path}'.")
        print(f"\n--> INSTRUÇÕES <--")
        print(f"1. Abra o arquivo '{screenshot_temp_path}' em um editor de imagem.")
        print(f"2. Recorte a área exata que você quer usar como template para este passo.")
        print(f"3. Salve o recorte como '{os.path.basename(template_manual_path)}' DENTRO da pasta da ação: '{action_folder}'")
        print(f"4. Volte aqui e aguarde. O script detectará o arquivo.")
        print(f"------------------")

        print(f"\nAguardando arquivo '{template_manual_path}' ser criado/atualizado...")

        # Esperar pelo arquivo template ser criado/atualizado
        wait_time = 0
        last_modified_time = None
        if os.path.exists(template_manual_path):
             last_modified_time = os.path.getmtime(template_manual_path)
             print(f"Arquivo '{template_manual_path}' já existe. Aguardando modificação...")
        else:
             print(f"Aguardando criação do arquivo '{template_manual_path}'...")


        while True:
             time.sleep(1) # Espera 1 segundo
             wait_time += 1

             if os.path.exists(template_manual_path):
                  current_modified_time = os.path.getmtime(template_manual_path)
                  # Check if file is new or has been modified since we last checked/started waiting
                  if last_modified_time is None or current_modified_time > last_modified_time + 1: # Add a small buffer for saving process
                       print(f"\nArquivo '{template_manual_path}' detectado/modificado após {wait_time}s de espera!")
                       last_modified_time = current_modified_time # Update the last modified time
                       break # Exit the waiting loop

             if wait_time % 5 == 0: # Imprime uma mensagem a cada 5 segundos
                 print(f"Ainda aguardando por '{template_manual_path}'... ({wait_time}s)")

        # Remover a screenshot temporária APÓS o usuário criar o template
        if os.path.exists(screenshot_temp_path):
            os.remove(screenshot_temp_path)
            print(f"Arquivo temporário '{screenshot_temp_path}' removido.")

        # Retorna o caminho completo para o template criado manualmente
        return template_manual_path

    else:
        print("Falha ao capturar a tela para criar o template.")
        # Não há arquivo temporário para remover neste caso
        return None


# --- Função principal para gravar a sequência de ações (usando assistentes) ---
def record_action_sequence_assisted(action_name, device_id=None):
    """
    Script principal para gravar uma sequência de ações, guiando o usuário
    na criação de templates ou na gravação de coordenadas, e salvando
    a configuração de cada passo em um arquivo sequence.json na pasta da ação.

    Args:
        action_name (str): O nome da ação (será usado para criar/acessar a pasta).
        device_id (str, optional): O ID do dispositivo Android.
    """
    action_folder = os.path.join("acoes", action_name)
    if not os.path.exists(action_folder):
        os.makedirs(action_folder)
        print(f"Pasta de ação '{action_folder}' criada/verificada.")

    sequence_filepath = os.path.join(action_folder, "sequence.json")
    action_sequence = [] # Inicializa a sequência vazia

    # --- Carregar sequência existente se houver ---
    if os.path.exists(sequence_filepath):
        try:
            with open(sequence_filepath, 'r', encoding='utf-8') as f:
                loaded_sequence = json.load(f)
                if isinstance(loaded_sequence, list):
                     action_sequence = loaded_sequence
                     print(f"Sequência existente carregada de: {sequence_filepath}")
                     print(f"Passos atuais na sequência: {len(action_sequence)}")
                else:
                     print(f"Aviso: Conteúdo inválido no arquivo JSON de sequência '{sequence_filepath}'. Começando nova sequência.")
                     action_sequence = [] # Começa nova sequência se o JSON for inválido
        except json.JSONDecodeError:
            print(f"Erro ao decodificar o arquivo JSON '{sequence_filepath}'. Verifique a sintaxe. Começando nova sequência.")
            action_sequence = [] # Começa nova sequência em caso de erro de JSON
        except Exception as e:
            print(f"Erro ao carregar arquivo JSON de sequência '{sequence_filepath}': {e}. Começando nova sequência.")
            action_sequence = [] # Começa nova sequência em caso de outros erros
    else:
        print(f"Arquivo de sequência '{sequence_filepath}' não encontrado. Começando nova sequência.")


    print(f"\n--- Modo de Gravação da Sequência de Ações para: {action_name} ---")
    print("Você adicionará passos um por um.")
    print("Digite 'q' a qualquer momento para sair e salvar a sequência atual.")


    while True:
        current_step_number = len(action_sequence) + 1
        print(f"\n--- Passo {current_step_number} ---")
        print("Escolha o tipo de passo a gravar:")
        print("  t: Template de Imagem (Usar assistente de recorte manual)")
        print("  c: Coordenadas Diretas (Capturar toque na tela)")
        print("  w: Espera (gravar um tempo fixo)")
        print("  q: Sair e Salvar")

        step_type_choice = input("Digite a opção (t, c, w, q): ").lower()

        if step_type_choice == 'q':
            print("\nSaindo do modo de gravação.")
            break # Sai do loop principal

        elif step_type_choice == 't':
            print("\n--> Gravando Passo de Template de Imagem <--")
            # Chama o assistente para criar o arquivo de template manualmente
            template_file_path = create_action_template_manual_crop(action_name, current_step_number, device_id=device_id)

            if template_file_path:
                 # Se o template foi criado com sucesso, adiciona um modelo de passo ao JSON
                 template_filename = os.path.basename(template_file_path)
                 step_config = {
                     "name": f"Passo {current_step_number}: Template {template_filename}", # Nome padrão
                     "type": "template",
                     "template_file": template_filename,
                     "action_on_found": "click", # Ação padrão ao encontrar
                     "click_delay": 0.5, # Delay padrão
                     # Adicionando defaults para action_before_find e action_after_find
                     "action_before_find": {
                         "type": "scroll",
                         "direction": "up",
                         "duration_ms": 500,
                         "delay_after_scroll": 0.5
                     },
                     "action_after_find": {
                         "type": "scroll",
                         "direction": "down",
                         "duration_ms": 500,
                         "delay_after_scroll": 0.5
                     },
                     "max_attempts": 1 # Placeholder
                 }
                 action_sequence.append(step_config)
                 print(f"Passo de Template '{template_filename}' adicionado à sequência (modelo com defaults).")
                 print("Lembre-se de editar o arquivo sequence.json para ajustar este passo (remover scroll, mudar delay, etc.).")
            else:
                 print("Falha ao criar o template. Passo de template NÃO adicionado à sequência.")


        elif step_type_choice == 'c':
            print("\n--> Gravando Passo de Coordenadas Diretas <--")
            print("Aguardando toque na tela do dispositivo...")
            touch_coords_raw = get_touch_event_coordinates(device_id=device_id) # Usando a função de adb_utils

            if touch_coords_raw:
                center_x_raw, center_y_raw = touch_coords_raw
                print(f"Toque RAW capturado em: ({center_x_raw}, {center_y_raw})")

                # --- Coordinate Scaling/Adjustment ---
                # Usando as variáveis definidas localmente ou importadas
                try:
                     scale_x = DEVICE_SCREEN_WIDTH / GETEVENT_MAX_X if GETEVENT_MAX_X > 0 else 1
                     scale_y = DEVICE_SCREEN_HEIGHT / GETEVENT_MAX_Y if GETEVENT_MAX_Y > 0 else 1
                except NameError:
                     print("Erro: Variáveis de configuração do dispositivo (DEVICE_SCREEN_WIDTH, etc.) não encontradas. Defina-as.")
                     continue # Pula para o próximo loop

                # Aplicar o fator de escala
                adjusted_x = int(center_x_raw * scale_x)
                adjusted_y = int(center_y_raw * scale_y)

                # Adicionar o passo de coordenadas diretas à sequência
                step_config = {
                    "name": f"Passo {current_step_number}: Clique em Coords", # Nome padrão
                    "type": "coords",
                    "coordinates": [adjusted_x, adjusted_y],
                    "click_delay": 0.5 # Delay padrão
                }
                action_sequence.append(step_config)
                print(f"Passo de Coordenadas Diretas ({adjusted_x}, {adjusted_y}) adicionado à sequência.")

            else:
                 print("Não foi possível capturar coordenadas de toque válidas. Passo de coordenadas NÃO adicionado.")


        elif step_type_choice == 'w':
            print("\n--> Gravando Passo de Espera <--")
            # --- Lógica para gravar passo de espera ---
            step_config = {
                "name": f"Passo {current_step_number}: Espera", # Nome temporário
                "type": "wait"
            }

            try:
                wait_duration = float(input("Digite a duração da espera em segundos (ex: 2.5): "))
                if wait_duration > 0:
                    step_config["duration_seconds"] = wait_duration
                    # --- Adicionar o passo configurado à sequência ---
                    action_sequence.append(step_config)
                    print(f"\nPasso de Espera de {wait_duration} segundos adicionado à sequência.")
                else:
                    print("Duração da espera deve ser maior que zero. Passo não adicionado.")
            except ValueError:
                print("Entrada inválida para a duração da espera. Passo não adicionado.")
            except Exception as e:
                 print(f"Ocorreu um erro ao processar a espera: {e}")
                 print("Este passo de espera NÃO será adicionado à sequência.")


        else:
            print("Opção inválida. Digite 't', 'c', 'w' ou 'q'.")
            continue # Volta para o início do loop para pedir a opção novamente

        # --- Salvar a sequência após cada passo ---
        # Salvar após cada passo é mais seguro caso algo dê errado ou o script seja interrompido.
        try:
            with open(sequence_filepath, 'w', encoding='utf-8') as f:
                json.dump(action_sequence, f, indent=4) # Usar indent=4 para facilitar a leitura
            print(f"\nSequência atual salva em: {sequence_filepath}")
        except Exception as e:
            print(f"Erro ao salvar a sequência em {sequence_filepath}: {e}")


    # --- Fim do loop principal ---

    print(f"\nGravação da sequência de ações para '{action_name}' finalizada.")
    # A sequência final já foi salva na última iteração do loop.


# Exemplo de uso do script de gravação:
# Descomente as linhas abaixo para iniciar o modo de gravação.
action_name_to_record = "sair_conta" # Substitua pelo nome da ação que você quer gravar/editar
device_id_recording = 'RXCTB03EXVK'  # Substitua pelo seu device_id
record_action_sequence_assisted(action_name_to_record, device_id=device_id_recording)