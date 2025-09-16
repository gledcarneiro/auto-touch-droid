# Nome do Arquivo: ef433a16_action_recorder.py
# Descrição: Contém funções para gravar sequências de ações (templates, coordenadas, esperas).
# Versão: 01.00.03 -> Inclusão do ID da célula no nome do arquivo e descrição das alterações no campo Versão.
# Analista: Gemini
# Programador: Gled Carneiro
# -----------------------------------------------------------------------------
import time
import subprocess
import os
import re
import json # Importar json para salvar a lista de forma estruturada

# Reutilizando a função de captura de toque e outras utilidades
from adb_utils import simulate_touch, get_touch_event_coordinates # simulate_touch pode ser útil para testes futuros

# --- Configurações do Dispositivo ---
# Ajuste estes valores de acordo com a resolução do seu dispositivo e o range de getevent
# Certifique-se de que estes valores estejam definidos localmente ou importados.
DEVICE_SCREEN_WIDTH = 2400 # Largura da tela em pixels (na orientação deitada, largura é a altura na retrato)
DEVICE_SCREEN_HEIGHT = 1080 # Altura da tela em pixels (na orientação deitada, altura é a largura na retrato)
GETEVENT_MAX_X = 4584 # Ajuste com base nos seus testes (maior X observado no teste central)
GETEVENT_MAX_Y = 4218 # Ajuste com base nos seus testes (maior Y observado no teste central)
# --- Fim das Configurações do Dispositivo ---


def create_action_sequence_by_touch_coords(device_id=None):
    """
    Captura uma sequência de coordenadas de toque na tela do dispositivo Android
    usando adb shell getevent e as armazena em uma lista, salvando em um arquivo JSON
    dentro da pasta de ação unificada ('acoes/<action_name>').

    Args:
        device_id (str, optional): O ID do dispositivo Android.

    Returns:
        list: Uma lista de tuplas (x, y) representando a sequência de coordenadas de toque.
              Retorna uma lista vazia se nenhum toque for capturado ou em caso de erro.
    """
    # --- Solicitar o nome da ação ao usuário ---
    action_name = input("Digite o nome da ação que você quer gravar (ex: abrir_menu, coletar_recursos): ")
    if not action_name:
        print("Nome da ação não fornecido. Cancelando gravação.")
        return [] # Retorna lista vazia se o nome não for fornecido

    # --- Usar a pasta de ações unificada ---
    action_folder = os.path.join("acoes", action_name) # Agora dentro da pasta 'acoes'
    if not os.path.exists(action_folder):
        os.makedirs(action_folder)
        print(f"Pasta de ação '{action_folder}' criada/verificada.")

    action_coords_sequence = []
    print(f"\n--- Modo de criação de sequência de ações por coordenadas de toque para a ação: {action_name} ---")
    print("Prepare a tela do seu dispositivo Android para a primeira ação.")
    print("Toque na tela no local da primeira ação.")
    print("Pressione 'q' e depois 'Enter' no terminal para sair.")

    step_counter = 1

    while True:
        print(f"\nAguardando toque para o Passo {step_counter}. Toque no dispositivo ou digite 'q' para sair.")

        # >>> Chamar a função para esperar por coordenadas de toque <<<
        # Certifique-se de que get_touch_event_coordinates está acessível (importada de adb_utils)
        touch_coords_raw = get_touch_event_coordinates(device_id=device_id) # Corrigido o nome da função

        if touch_coords_raw is None:
             user_input_check = input("Pressione 'Enter' para tentar capturar o toque novamente ou digite 'q' para sair: ")
             if user_input_check.lower() == 'q':
                  print("Saindo do modo de criação de sequência de ações por toque.")
                  break
             else:
                  continue # Try capturing touch again
        elif isinstance(touch_coords_raw, str) and touch_coords_raw.lower() == 'q':
             print("Saindo do modo de criação de sequência de ações por toque.")
             break

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
                 return [] # Sair em caso de erro de configuração


            # Aplicar o fator de escala
            adjusted_x = int(center_x_raw * scale_x)
            adjusted_y = int(center_y_raw * scale_y)

            # Adicionar as coordenadas ajustadas à sequência
            action_coords_sequence.append((adjusted_x, adjusted_y))
            print(f"Coordenadas ajustadas adicionadas à sequência: ({adjusted_x}, {adjusted_y})")

            step_counter += 1 # Incrementar o contador de passo

    print("\nSequência de ações por toque finalizada.")
    print(f"Sequência de coordenadas capturada: {action_coords_sequence}")

    # --- Salvar a sequência em um arquivo JSON na pasta de ação ---
    coords_filename = f"sequence.json" # Nome fixo ou baseado em step_counter se precisar de multiplos arquivos na pasta
    coords_filepath = os.path.join(action_folder, coords_filename)

    try:
        with open(coords_filepath, 'w') as f:
            json.dump(action_coords_sequence, f)
        print(f"Sequência de coordenadas salva em: {coords_filepath}")
    except Exception as e:
        print(f"Erro ao salvar a sequência de coordenadas em {coords_filepath}: {e}")

    return action_coords_sequence # Ensure the list is returned here

# Exemplo de uso do script auxiliar:
# device_id = 'RXCTB03EXVK'  # Substitua pelo seu device_id
# captured_sequence = create_action_sequence_by_touch_coords(device_id=device_id)
# print("\nSequência final capturada:")
# print(captured_sequence)