# Nome do Arquivo: ef433a16_action_recorder.py (Originalmente action_recorder, renomeado para evitar confusão com gravação assistida)
# Descrição: Contém uma função (agora não principal) para gravar sequências APENAS por coordenadas de toque.
# Versão: 01.00.04 -> Incluído ID, Descrição atualizada, e ajustado para ser uma função auxiliar menos central.
# Analista: Gemini
# Programador: Gled Carneiro
# -----------------------------------------------------------------------------
import time
import subprocess
import os
import re
import json # Importar json para salvar a lista de forma estruturada

# Reutilizando a função de captura de toque e outras utilidades
from ..core.adb_utils import simulate_touch, get_touch_event_coordinates

# --- Configurações do Dispositivo (devem ser consistentes em todos os scripts que usam getevent) ---
# Ajuste estes valores de acordo com a resolução do seu dispositivo e o range de getevent
# Certifique-se de que estes valores estejam definidos localmente ou importados de um arquivo de config central.
# Por enquanto, mantidos aqui para esta função específica.
DEVICE_SCREEN_WIDTH = 2400 # Largura da tela em pixels (na orientação deitada, largura é a altura na retrato)
DEVICE_SCREEN_HEIGHT = 1080 # Altura da tela em pixels (na orientação deitada, altura é a largura na retrato)
GETEVENT_MAX_X = 4584 # Ajuste com base nos seus testes (maior X observado no teste central)
GETEVENT_MAX_Y = 4218 # Ajuste com base nos seus testes (maior Y observado no teste central)
# --- Fim das Configurações do Dispositivo ---


def create_action_sequence_by_touch_coords_only(action_name, device_id=None):
    """
    **Esta função é para gravar APENAS sequências de cliques por coordenadas diretas.**
    Captura uma sequência de coordenadas de toque na tela do dispositivo Android
    usando adb shell getevent e as armazena em uma lista, salvando em um arquivo JSON
    dentro da pasta de ação unificada ('acoes/<action_name>').

    A gravação assistida principal (create_action_template.py) é recomendada para a maioria dos casos.

    Args:
        action_name (str): O nome da ação que você quer gravar (será a pasta).
        device_id (str, optional): O ID do dispositivo Android.

    Returns:
        list: Uma lista de dicionários representando os passos de coordenadas.
              Retorna uma lista vazia se nenhum toque for capturado ou em caso de erro.
    """
    if not action_name:
        print("Nome da ação não fornecido. Cancelando gravação.")
        return []

    # --- Usar a pasta de ações unificada ---
    action_folder = os.path.join("acoes", action_name) # Agora dentro da pasta 'acoes'
    if not os.path.exists(action_folder):
        os.makedirs(action_folder)
        print(f"Pasta de ação '{action_folder}' criada/verificada.")

    sequence_filepath = os.path.join(action_folder, "sequence.json")
    action_sequence = [] # Lista para armazenar os dicionários de passos

    # Carregar sequência existente se houver (para adicionar no final)
    if os.path.exists(sequence_filepath):
        try:
            with open(sequence_filepath, 'r', encoding='utf-8') as f:
                loaded_sequence = json.load(f)
                if isinstance(loaded_sequence, list):
                     action_sequence = loaded_sequence
                     print(f"Sequência existente carregada de: {sequence_filepath}")
                     print(f"Adicionando novos passos ao final dos {len(action_sequence)} passos existentes.")
                else:
                     print(f"Aviso: Conteúdo inválido no arquivo JSON de sequência '{sequence_filepath}'. Começando nova sequência.")
                     action_sequence = [] # Começa nova sequência se o JSON for inválido
        except json.JSONDecodeError:
            print(f"Erro ao decodificar o arquivo JSON '{sequence_filepath}'. Verifique a sintaxe. Começando nova sequência.")
            action_sequence = [] # Começa nova sequência em caso de erro de JSON
        except Exception as e:
            print(f"Erro ao carregar arquivo JSON de sequência '{sequence_filepath}': {e}. Começando nova sequência.")
            action_sequence = [] # Começa nova sequência em caso de outros erros


    print(f"\n--- Modo de criação de sequência de ações por coordenadas de toque para a ação: {action_name} ---")
    print("Prepare a tela do seu dispositivo Android para a primeira ação.")
    print("Toque na tela no local da primeira ação.")
    print("Pressione 'q' e depois 'Enter' no terminal para sair.")

    step_counter = len(action_sequence) + 1 # Começa a numerar a partir do próximo passo

    while True:
        print(f"\nAguardando toque para o Passo {step_counter}. Toque no dispositivo ou digite 'q' para sair.")

        # >>> Chamar a função para esperar por coordenadas de toque <<<
        touch_coords_raw = get_touch_event_coordinates(device_id=device_id)

        # Verifica se o usuário digitou 'q' na entrada de get_touch_event_coordinates
        # (get_touch_event_coordinates retorna None se o timeout ocorrer)
        # Se retornou None, pedimos confirmação para sair
        if touch_coords_raw is None:
             user_input_check = input("Pressione 'Enter' para tentar capturar o toque novamente ou digite 'q' para sair: ")
             if user_input_check.lower() == 'q':
                  print("Saindo do modo de criação de sequência de ações por toque.")
                  break
             else:
                  continue # Tenta capturar toque novamente


        elif touch_coords_raw:
            center_x_raw, center_y_raw = touch_coords_raw
            print(f"Toque RAW capturado em: ({center_x_raw}, {center_y_raw})")

            # --- Coordinate Scaling/Adjustment ---
            # Usando as variáveis definidas localmente no script
            try:
                 scale_x = DEVICE_SCREEN_WIDTH / GETEVENT_MAX_X if GETEVENT_MAX_X > 0 else 1
                 scale_y = DEVICE_SCREEN_HEIGHT / GETEVENT_MAX_Y if GETEVENT_MAX_Y > 0 else 1
            except NameError:
                 print("Erro: Variáveis de configuração do dispositivo (DEVICE_SCREEN_WIDTH, etc.) não encontradas. Defina-as.")
                 # Salva a sequência parcial antes de sair em caso de erro de configuração
                 try:
                      with open(sequence_filepath, 'w', encoding='utf-8') as f:
                          json.dump(action_sequence, f, indent=4)
                      print(f"Sequência parcial salva em: {sequence_filepath}")
                 except Exception as save_e:
                      print(f"Erro ao salvar sequência parcial em {sequence_filepath}: {save_e}")
                 return action_sequence # Retorna a sequência parcial


            # Aplicar o fator de escala
            adjusted_x = int(center_x_raw * scale_x)
            adjusted_y = int(center_y_raw * scale_y)

            # Criar um dicionário para este passo (tipo "coords")
            step_config = {
                "name": f"Passo {step_counter}: Clique em Coords ({adjusted_x}, {adjusted_y})", # Nome padrão mais descritivo
                "type": "coords",
                "coordinates": [adjusted_x, adjusted_y],
                "click_delay": 0.5 # Delay padrão
            }

            # Adicionar o passo configurado à sequência
            action_sequence.append(step_config)
            print(f"Passo de Coordenadas Diretas ({adjusted_x}, {adjusted_y}) adicionado à sequência.")

            step_counter += 1 # Incrementar o contador de passo

            # --- Salvar a sequência após cada passo ---
            try:
                with open(sequence_filepath, 'w', encoding='utf-8') as f:
                    json.dump(action_sequence, f, indent=4) # Usar indent=4 para facilitar a leitura
                print(f"\nSequência atual salva em: {sequence_filepath}")
            except Exception as e:
                print(f"Erro ao salvar a sequência em {sequence_filepath}: {e}")


    print("\nSequência de ações por toque finalizada.")
    # A sequência final já foi salva na última iteração do loop.

    return action_sequence # Ensure the list is returned here

# Removido o exemplo de uso direto. Esta função não é mais o ponto de entrada principal para gravação.
# # Exemplo de uso do script auxiliar:
# # device_id = 'RXCTB03EXVK'  # Substitua pelo seu device_id
# # action_name_for_coords_only = "minha_acao_coords" # Nome da ação para esta gravação específica
# # captured_sequence = create_action_sequence_by_touch_coords_only(action_name=action_name_for_coords_only, device_id=device_id)
# # print("\nSequência final capturada (coords only):")
# # print(captured_sequence)