import time
import subprocess
import os
import re
import json # Importar json para salvar a lista de forma estruturada

# Reutilizando a função de captura de toque e outras utilidades
from adb_utils import simulate_touch, get_touch_event_coordinates # simulate_touch pode ser útil para testes futuros

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
# --- Fim das Configurações do Dispositivo ---

#--- Script Principal para Captura e Criação de Templates via Toque ---
def create_action_sequence_by_touch_coords(action_name, device_id=None):
    """
    Captura uma sequência de coordenadas de toque na tela do dispositivo Android
    usando adb shell getevent e as armazena em uma lista.

    Args:
        action_name (str): O nome da ação (será usado para criar a pasta e o nome do arquivo).
        device_id (str, optional): O ID do dispositivo Android.

    Returns:
        list: Uma lista de tuplas (x, y) representando a sequência de coordenadas de toque.
              Retorna uma lista vazia se nenhum toque for capturado ou em caso de erro.
    """
    action_folder = os.path.join("acoes_coords", action_name) # Criar uma pasta específica para coordenadas
    if not os.path.exists(action_folder):
        os.makedirs(action_folder)
        print(f"Pasta de ação para coordenadas '{action_folder}' criada.")

    action_coords_sequence = []
    print(f"\n--- Modo de criação de sequência de ações por coordenadas de toque para a ação: {action_name} ---")
    print("Prepare a tela do seu dispositivo Android para a primeira ação.")
    print("Toque na tela no local da primeira ação.")
    print("Pressione 'q' e depois 'Enter' no terminal para sair.")

    step_counter = 1

    while True:
        print(f"\nAguardando toque para o Passo {step_counter}. Toque no dispositivo ou digite 'q' para sair.")

        # >>> Chamar a função para esperar por coordenadas de toque <<<
        # Reutilizando a lógica de get_touch_event_coordinates
        # Certifique-se de que esta função está disponível (definida na célula anterior ou importada)
        touch_coords_raw = get_touch_event_coordinates(device_id=device_id)


        if touch_coords_raw is None:
            # Check for user input if touch_coords_raw is None (e.g., timeout or user typed 'q' in get_touch_event_coordinates if that logic is added there)
            # For now, assuming get_touch_event_coordinates returns None on timeout or error.
            # We should also allow explicit 'q' input here.
             user_input_check = input("Pressione 'Enter' para tentar capturar o toque novamente ou digite 'q' para sair: ")
             if user_input_check.lower() == 'q':
                  print("Saindo do modo de criação de sequência de ações por toque.")
                  break
             else:
                  continue # Try capturing touch again
        elif isinstance(touch_coords_raw, str) and touch_coords_raw.lower() == 'q':
             print("Saindo do modo de criação de sequência de ações por toque.")
             break # Exit if get_touch_event_coordinates was modified to return 'q' on user input

        elif touch_coords_raw:
            center_x_raw, center_y_raw = touch_coords_raw
            print(f"Toque RAW capturado em: ({center_x_raw}, {center_y_raw})")

            # --- Coordinate Scaling/Adjustment (Reutilizando a lógica da célula 42427df3) ---
            # É crucial que DEVICE_SCREEN_WIDTH, DEVICE_SCREEN_HEIGHT, GETEVENT_MAX_X, GETEVENT_MAX_Y
            # estejam definidos e corretos.
            # Para este código funcionar, assumimos que essas variáveis estão no escopo global
            # ou você as define aqui com os valores corretos para o seu dispositivo.
            # DEFINA ESTAS VARIÁVEIS AQUI SE NÃO ESTIVEREM NO ESCOPO GLOBAL:
            try:
                 # Try to use global variables if they exist
                 scale_x = globals().get('DEVICE_SCREEN_WIDTH', 1) / globals().get('GETEVENT_MAX_X', 1)
                 scale_y = globals().get('DEVICE_SCREEN_HEIGHT', 1) / globals().get('GETEVENT_MAX_Y', 1)
                 # Add a check for division by zero
                 if globals().get('GETEVENT_MAX_X', 0) == 0: scale_x = globals().get('DEVICE_SCREEN_WIDTH', 1)
                 if globals().get('GETEVENT_MAX_Y', 0) == 0: scale_y = globals().get('DEVICE_SCREEN_HEIGHT', 1)

            except NameError:
                 print("Erro: Variáveis de configuração do dispositivo (DEVICE_SCREEN_WIDTH, etc.) não encontradas. Defina-as.")
                 # Fallback or exit if essential variables are not defined
                 print("Saindo devido à falta de variáveis de configuração.")
                 return []


            # Aplicar o fator de escala
            adjusted_x = int(center_x_raw * scale_x)
            adjusted_y = int(center_y_raw * scale_y)

            # Adicionar as coordenadas ajustadas à sequência
            action_coords_sequence.append((adjusted_x, adjusted_y))
            print(f"Coordenadas ajustadas adicionadas à sequência: ({adjusted_x}, {adjusted_y})")

            step_counter += 1 # Incrementar o contador de passo

        # else: # touch_coords_raw was None due to timeout/error in get_touch_event_coordinates
        #    print("Não foi possível capturar as coordenadas do toque.")
           # The handling for None is now at the top of the loop


    print("\nSequência de ações por toque finalizada.")
    print(f"Sequência de coordenadas capturada: {action_coords_sequence}")

    # --- Salvar a sequência em um arquivo ---
    coords_filename = f"{action_name}_sequence.json" # Usar .json para facilitar leitura e escrita
    coords_filepath = os.path.join(action_folder, coords_filename)

    try:
        with open(coords_filepath, 'w') as f:
            json.dump(action_coords_sequence, f)
        print(f"Sequência de coordenadas salva em: {coords_filepath}")
    except Exception as e:
        print(f"Erro ao salvar a sequência de coordenadas em {coords_filepath}: {e}")

    return action_coords_sequence # Ensure the list is returned here

# Exemplo de uso do script auxiliar:
device_id = 'RXCTB03EXVK'  # Substitua pelo seu device_id
action_name_to_record = "minha_primeira_acao" # Nome da ação que você está gravando
captured_sequence = create_action_sequence_by_touch_coords(action_name_to_record, device_id=device_id)
print("\nSequência final capturada:")
print(captured_sequence)