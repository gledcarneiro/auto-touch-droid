import cv2
import subprocess
import os
import time
import re
import shutil # Importar shutil para copiar arquivos
import json # Importar json para lidar com arquivos de sequência

# --- Funções auxiliares ---
from adb_utils import simulate_touch, get_action_sequence, capture_screen
# Importando a função de confirmação (Assumindo que find_and_confirm_click está disponível para importação)
# Se find_and_confirm_click estiver em uma célula separada no notebook, você pode precisar executá-la primeiro.
# Idealmente, find_and_confirm_click estaria em um arquivo .py separado (ex: action_executor.py) para importar.
from action_executor import find_and_confirm_click # Assumindo que você salvou find_and_confirm_click em action_executor.py

# --- Configurações do Dispositivo ---
# As configurações de getevent não são usadas para o recorte neste método,
# mas podem ser úteis se a função find_image_on_screen as usar em algum momento.
# Mantenho-as aqui por consistência, mas a escala de toque não afeta mais a criação do template.
DEVICE_SCREEN_WIDTH = 2400 # Largura da tela em pixels (na orientação deitada, largura é a altura na retrato)
DEVICE_SCREEN_HEIGHT = 1080 # Altura da tela em pixels (na orientação deitada, altura é a largura na retrato)
GETEVENT_MAX_X = 4584 # Ajuste com base nos seus testes (maior X observado no teste central)
GETEVENT_MAX_Y = 4218 # Ajuste com base nos seus testes (maior Y observado no teste central)
# --- Fim das Configurações do Dispositivo ---

# --- Script Principal para Captura de Screenshot e Espera por Template Manual ---
def create_action_template_manual_crop(action_name, device_id=None):
    """
    Script auxiliar para capturar a tela do Android, salvar como arquivo temporário,
    e aguardar que o usuário crie manualmente um template 'template.png' na pasta da ação.
    O script testa o template, copia se for bem-sucedido e renomeia a cópia.
    Se o teste for bem-sucedido, também salva as coordenadas do centro da imagem encontrada
    em um arquivo sequence.json na pasta da ação.

    Args:
        action_name (str): O nome da ação (será usado para criar a pasta e prefixo do arquivo).
        device_id (str, optional): O ID do dispositivo Android.
    """
    # --- Usar a pasta de ações unificada ---
    action_folder = os.path.join("acoes", action_name) # Agora dentro da pasta 'acoes'
    if not os.path.exists(action_folder):
        os.makedirs(action_folder)
        print(f"Pasta de ação '{action_folder}' criada/verificada.")

    # Caminho para o arquivo de sequência JSON
    sequence_filepath = os.path.join(action_folder, "sequence.json")

    print(f"\n--- Modo de criação de templates por recorte manual e gravação de coordenadas para a ação: {action_name} ---")
    print("Prepare a tela do seu dispositivo Android para o próximo passo da ação.")
    print("Pressione 'Enter' no terminal para capturar a tela.")
    print("Pressione 'q' e depois 'Enter' para sair a qualquer momento.")

    step_counter = 1
    # Determine the next sequential filename based on existing files
    # Agora procurando por arquivos .png que seguem o padrão XX_template.png na pasta de ação unificada
    existing_files = get_action_sequence(action_folder)
    if existing_files:
        # Filtra apenas os arquivos .png que seguem o padrão XX_template.png
        template_files = sorted([f for f in existing_files if os.path.basename(f).endswith('.png') and re.match(r'\d+_template\.png', os.path.basename(f))])

        if template_files:
            last_file = os.path.basename(template_files[-1])
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
        else:
             print("Nenhum arquivo de template sequencial encontrado na pasta. Iniciando a sequência do 1.")
             step_counter = 1 # Start from 1 if no template files found


    screenshot_temp_path = "screenshot_temp_for_template_manual.png" # Nome fixo para a screenshot temporária
    template_manual_path = os.path.join(action_folder, "template.png") # Caminho fixo para o template manual

    while True:
        user_input = input(f"Pronto para o template (Passo {step_counter})? Pressione Enter para capturar tela ou 'q' para sair: ")

        if user_input.lower() == 'q':
            print("Saindo do modo de criação de templates manuais.")
            # Clean up temp screenshot if it exists on exit
            if os.path.exists(screenshot_temp_path):
                os.remove(screenshot_temp_path)
                print(f"Arquivo temporário {screenshot_temp_path} removido na saída.")
            # Also clean up the template.png if it exists and the user quits
            if os.path.exists(template_manual_path):
                 print(f"Removendo arquivo temporário de template '{template_manual_path}'.")
                 os.remove(template_manual_path)

            break
        elif user_input == '':
            print("\nCapturando tela...")
            # Use the capture_screen function from adb_utils
            if capture_screen(device_id=device_id, output_path=screenshot_temp_path):
                print(f"Screenshot capturada e salva como {screenshot_temp_path}.")

                # --- Instruir o usuário e esperar pelo template manual ---
                print(f"\n--> INSTRUÇÕES <--")
                print(f"1. Abra o arquivo '{screenshot_temp_path}' em um editor de imagem.")
                print(f"2. Recorte a área exata que você quer usar como template.")
                print(f"3. Salve o recorte como '{os.path.basename(template_manual_path)}' DENTRO da pasta da ação: '{action_folder}'")
                print(f"4. Volte aqui e aguarde. O script detectará o arquivo.")
                print(f"------------------")


                print(f"\nAguardando arquivo '{template_manual_path}' ser criado/atualizado...")

                # Esperar pelo arquivo template.png ser criado/atualizado
                wait_time = 0
                # Use a mechanism to check for file modification or creation
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

                     # Add an option to cancel waiting? Ctrl+C still works.


                # --- Arquivo template.png detectado/modificado, agora testar ---
                print(f"\nTestando o template: {template_manual_path}")
                # capture_screen, find_image_on_screen, simulate_touch are used inside find_and_confirm_click
                # We pass the path to the manually created template.png
                # Modified find_and_confirm_click to return success and coordinates
                success, coords = find_and_confirm_click(template_manual_path, device_id=device_id)

                # Remover a screenshot temporária APÓS o teste (sucesso ou falha)
                if os.path.exists(screenshot_temp_path):
                    os.remove(screenshot_temp_path)
                    print(f"Arquivo temporário {screenshot_temp_path} removido após teste.")


                if success:
                    print("Teste de template BEM-SUCEDIDO: A imagem foi encontrada e clicada.")
                    center_x, center_y = coords # Desempacota as coordenadas retornadas

                    # --- Se o teste passar, COPIAR template e SALVAR coordenadas ---
                    template_filename_sequential = f"{step_counter:02d}_template.png"
                    template_save_path = os.path.join(action_folder, template_filename_sequential)

                    try:
                        # Use shutil.copy2 to copy metadata as well
                        shutil.copy2(template_manual_path, template_save_path)
                        print(f"Cópia do template salva como: {template_save_path}")

                        # --- Salvar as coordenadas do centro da imagem encontrada no JSON ---
                        # Carregar a sequência existente, adicionar a nova coordenada e salvar
                        action_coords_sequence = []
                        if os.path.exists(sequence_filepath):
                            try:
                                with open(sequence_filepath, 'r') as f:
                                    action_coords_sequence = json.load(f)
                            except json.JSONDecodeError:
                                print(f"Aviso: Arquivo JSON de sequência '{sequence_filepath}' inválido/vazio. Criando nova sequência.")
                                action_coords_sequence = [] # Reinicia se o JSON for inválido/vazio
                            except Exception as e:
                                print(f"Erro ao carregar arquivo JSON de sequência '{sequence_filepath}': {e}. Criando nova sequência.")
                                action_coords_sequence = [] # Reinicia em caso de outros erros

                        # Adicionar as coordenadas encontradas como uma tupla (X, Y)
                        action_coords_sequence.append((center_x, center_y))
                        print(f"Coordenadas encontradas ({center_x}, {center_y}) adicionadas à sequência.")

                        # Salvar a sequência atualizada no arquivo JSON
                        try:
                            with open(sequence_filepath, 'w') as f:
                                json.dump(action_coords_sequence, f, indent=4) # Usar indent=4 para facilitar a leitura
                            print(f"Sequência de coordenadas atualizada salva em: {sequence_filepath}")
                        except Exception as e:
                            print(f"Erro ao salvar a sequência de coordenadas em {sequence_filepath}: {e}")


                        step_counter += 1 # Incrementar APENAS se o teste passar e a cópia for bem-sucedida (e salvamento JSON tentado)


                    except OSError as e:
                        print(f"Erro ao copiar o arquivo {template_manual_path} para {template_save_path}: {e}")
                        print("A cópia do template não foi salva corretamente. O passo não será incrementado.")
                        # step_counter is not incremented on copy error.

                    except Exception as e:
                         print(f"Ocorreu um erro inesperado após teste bem-sucedido ao tentar copiar o template ou salvar JSON: {e}")
                         # step_counter is not incremented on unexpected error.


                else:
                    print("Teste de template FALHOU: A imagem NÃO foi encontrada ou clicada.")
                    print(f"O arquivo '{template_manual_path}' permaneceu na pasta. Recorte e salve-o novamente para o Passo {step_counter}.")
                    # Não incrementa step_counter
                    # O loop continuará e esperará por uma nova modificação em template.png


                # The loop continues, either for the next step (if successful) or the same step (if failed)


            else:
                print("Falha ao capturar a tela. Não foi possível iniciar o processo de criação de template manual.")
                # Não há arquivo temporário para remover neste caso

        else:
            print("Entrada inválida. Pressione Enter ou 'q'.")

# Exemplo de uso do script auxiliar de template manual:
action_name_manual = "coleta_item" # Nome da ação para salvar os templates e a sequência
device_id_manual = 'RXCTB03EXVK'  # Substitua pelo seu device_id
create_action_template_manual_crop(action_name_manual, device_id=device_id_manual)