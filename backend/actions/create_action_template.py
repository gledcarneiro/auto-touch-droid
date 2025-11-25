# Nome do Arquivo: 42427df3_create_action_template.py
# Descrição: Contém funções auxiliares para criar templates de imagem manualmente e gravar sequências assistidas.
# Versão: 01.00.14 -> Correção de erros de indentação e limpeza de código duplicado.
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
import numpy as np # Importar numpy para operações com imagens

# --- Funções auxiliares ---
# Importando funções dos módulos do backend
# --- Configuração de Importação ---
import sys
import os

# Adiciona o diretório raiz do projeto ao sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

# Importando funções dos módulos do backend
from backend.core.adb_utils import simulate_touch, get_touch_event_coordinates, capture_screen
# from ..core.action_executor import find_and_confirm_click # Removido temporariamente se a lógica for separada

# --- Configurações do Dispositivo ---
# Mantenho as configurações de getevent aqui por referência, embora não afetem diretamente a gravação de templates ou JSON
# As coordenadas de toque RAW do getevent (se usadas para gravar coords diretas) precisam ser ajustadas.
DEVICE_SCREEN_WIDTH = 2400 # Largura da tela em pixels (na orientação deitada, largura é a altura na retrato)
DEVICE_SCREEN_HEIGHT = 1080 # Altura da tela em pixels (na orientação deitada, altura é a largura na retrato)
GETEVENT_MAX_X = 4584 # Ajuste com base nos seus testes (maior X observado no teste central)
GETEVENT_MAX_Y = 4218 # Ajuste com base nos seus testes (maior Y observado no teste central)
# --- Fim das Configurações do Dispositivo ---


# --- Função para encontrar a marcação preta na imagem ---
def find_black_mark(original_image_path, marked_image_path):
    """
    Compara a imagem original com a imagem marcada e tenta encontrar a área da marcação preta.

    Args:
        original_image_path (str): Caminho para a imagem original (screenshot).
        marked_image_path (str): Caminho para a imagem com a marcação preta.

    Returns:
        tuple: Uma tupla (x, y, w, h) representando o bounding box da marcação encontrada,
               ou None se nenhuma marcação clara for detectada.
    """
    try:
        original = cv2.imread(original_image_path)
        marked = cv2.imread(marked_image_path)

        if original is None:
            print(f"Erro: Não foi possível carregar a imagem original de {original_image_path}")
            return None
        if marked is None:
            print(f"Erro: Não foi possível carregar a imagem marcada de {marked_image_path}")
            return None

        # Garante que as imagens têm as mesmas dimensões
        if original.shape != marked.shape:
            print("Erro: As imagens original e marcada têm dimensões diferentes.")
            return None

        # Converta as imagens para tons de cinza
        original_gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        marked_gray = cv2.cvtColor(marked, cv2.COLOR_BGR2GRAY)

        # Calcule a diferença absoluta entre as duas imagens em tons de cinza
        # A diferença será maior onde a marcação preta foi adicionada
        diff = cv2.absdiff(original_gray, marked_gray)

        # Use um limiar para binarizar a imagem de diferença.
        # Pixels com diferença acima do limiar são considerados parte da marcação.
        # O valor 30 é um limiar inicial, pode precisar de ajuste.
        _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

        # Encontre contornos na imagem binarizada.
        # cv2.findContours pode ter diferentes retornos dependendo da versão do OpenCV
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Itere sobre os contornos encontrados para encontrar o que provavelmente é a marcação
        # Podemos procurar pelo maior contorno (assumindo que a marcação é a maior diferença)
        # ou filtrar por área para evitar pequenos ruídos.
        if contours:
            # Encontre o contorno com a maior área
            largest_contour = max(contours, key=cv2.contourArea)

            # Obtenha o bounding box (caixa delimitadora) do maior contorno
            x, y, w, h = cv2.boundingRect(largest_contour)

            # Opcional: Filtrar por tamanho mínimo de área se necessário
            min_mark_area = 50 # Exemplo: Mínimo de 50 pixels quadrados para ser considerado marcação
            if cv2.contourArea(largest_contour) < min_mark_area:
                 print("Aviso: Nenhuma marcação com área significativa encontrada.")
                 return None

            print(f"Marcação detectada no bounding box: ({x}, {y}, {w}, {h})")
            return (x, y, w, h)
        else:
            print("Nenhum contorno detectado na imagem de diferença. Marcação não encontrada.")
            return None

    except Exception as e:
        print(f"Ocorreu um erro ao encontrar a marcação preta: {e}")
        return None


# --- Função para criar template usando detecção de marcação ---
def create_action_template_by_marking(action_name, step_number, device_id=None):
    """
    Captura a tela do dispositivo, pré-cria o arquivo para marcação,
    instrui o usuário a marcar a área do template com uma marcação preta
    na imagem salva, e então detecta a marcação para recortar automaticamente
    o template da imagem original. Permite nomear o passo.

    Args:
        action_name (str): O nome da ação (será usado para criar/acessar a pasta).
        step_number (int): O número do passo atual na sequência (usado para nomes de arquivo).
        device_id (str, optional): O ID do dispositivo Android.

    Returns:
        str: O nome do arquivo de template criado (apenas o nome, não o caminho completo),
             ou None em caso de falha.
    """
    action_folder = os.path.join("acoes", action_name)
    if not os.path.exists(action_folder):
        os.makedirs(action_folder)
        print(f"Pasta de ação '{action_folder}' criada/verificada.")

    # Nomes de arquivo temporários/intermediários
    screenshot_original_path = os.path.join(action_folder, f"screenshot_original_{step_number:02d}.png")
    screenshot_marked_path = os.path.join(action_folder, f"screenshot_marked_{step_number:02d}.png")

    print(f"\n--- Criando Template (por marcação) para o Passo {step_number} da ação '{action_name}' ---")
    print("Prepare a tela do seu dispositivo para o estado deste passo.")
    input("Pressione 'Enter' para capturar a tela para criar o template...")

    # Captura a screenshot original
    if not capture_screen(device_id=device_id, output_path=screenshot_original_path):
        print("Falha ao capturar a tela para criar o template.")
        return None

    print(f"\nScreenshot original capturada e salva como '{screenshot_original_path}'.")

    # --- Pré-criar o arquivo marcado (copiando a original) ---
    try:
        shutil.copy(screenshot_original_path, screenshot_marked_path)
        print(f"Arquivo para marcação pré-criado em '{screenshot_marked_path}'.")
    except Exception as e:
        print(f"Erro ao pré-criar arquivo para marcação em '{screenshot_marked_path}': {e}")
        # Se falhar ao pré-criar, podemos tentar seguir o fluxo antigo (aguardar a criação)
        print("Tentando aguardar pela criação manual do arquivo marcado...")

    # --- Solicitar o nome do passo ---
    step_name_input = input("Digite um nome descritivo para este passo (ex: entrar, item, pegar, confirma): ")
    # Limpar o nome para usar em nome de arquivo (remover espaços, caracteres especiais, etc.)
    # Substitui espaços e caracteres não alfanuméricos por underscore, e converte para minúsculas.
    safe_step_name = re.sub(r'\W+', '_', step_name_input).lower().strip('_')
    if not safe_step_name:
        safe_step_name = f"step_{step_number:02d}" # Fallback name if input is empty/invalid

    # Define o nome do arquivo de template gerado usando o número do passo e o nome descritivo
    template_generated_filename = f"{step_number:02d}_{safe_step_name}.png"
    template_generated_path = os.path.join(action_folder, template_generated_filename)


    print(f"\n--> INSTRUÇÕES <--")
    print(f"1. Abra o arquivo '{screenshot_marked_path}' em um editor de imagem no seu PC.")
    print(f"2. Adicione uma **marcação preta sólida** (bola, quadrado, etc.) em algum lugar DENTRO da área que você quer usar como template.")
    print(f"3. **Salve** as mudanças no arquivo '{os.path.basename(screenshot_marked_path)}' DENTRO da pasta da ação: '{action_folder}'")
    print(f"4. Volte aqui e aguarde. O script detectará a modificação no arquivo marcado e tentará encontrar a marcação.")
    print(f"------------------")

    print(f"\nAguardando arquivo '{screenshot_marked_path}' ser criado/atualizado com a marcação...")

    # Esperar pelo arquivo marcado ser criado/atualizado
    # A lógica de espera agora verifica a modificação do arquivo pré-criado
    wait_time = 0
    last_modified_time_marked = None
    if os.path.exists(screenshot_marked_path):
         # Pega o tempo de modificação inicial do arquivo pré-criado
         last_modified_time_marked = os.path.getmtime(screenshot_marked_path)
         print(f"Aguardando modificação do arquivo '{screenshot_marked_path}'...")
    else:
         # Se o pré-criação falhou, volta a aguardar a criação manual (comentado)
         # print(f"Aguardando criação do arquivo '{screenshot_marked_path}'...")
         # Neste caso, a lógica de espera abaixo ainda funcionaria, mas o aviso acima é útil.
         pass


    while True:
         time.sleep(1) # Espera 1 segundo
         wait_time += 1

         if os.path.exists(screenshot_marked_path):
              current_modified_time_marked = os.path.getmtime(screenshot_marked_path)
              # Check if file has been modified since we started waiting (plus buffer)
              # Use last_modified_time_marked != current_modified_time_marked or current_modified_time_marked > initial_wait_time + 1
              # or simply check if current_modified_time_marked > last_modified_time_marked (if it exists)
              # Let's use a check against the initial modification time plus a buffer
              if last_modified_time_marked is not None and current_modified_time_marked > last_modified_time_marked + 1: # +1 second buffer
                   print(f"\nArquivo '{screenshot_marked_path}' detectado/modificado após {wait_time}s de espera!")
                   # No need to update last_modified_time_marked here, we break
                   break # Exit the waiting loop
              elif last_modified_time_marked is None: # Case where pre-creation failed and we are waiting for manual creation
                   print(f"\nArquivo '{screenshot_marked_path}' criado após {wait_time}s de espera! Procedendo...")
                   break # Exit if the file is newly created


         if wait_time > 600: # Timeout de 10 minutos (600 segundos)
              print("\nTempo limite de espera excedido. Nenhuma marcação foi salva.")
              # Limpar arquivos temporários
              try:
                  if os.path.exists(screenshot_original_path): os.remove(screenshot_original_path)
              except PermissionError:
                  print(f"Aviso: Não foi possível remover o arquivo original '{screenshot_original_path}'. Ele pode estar em uso por outro programa. Por favor, feche-o.")
              try:
                  if os.path.exists(screenshot_marked_path): os.remove(screenshot_marked_path)
              except PermissionError:
                   print(f"Aviso: Não foi possível remover o arquivo marcado '{screenshot_marked_path}'. Ele pode estar em uso por outro programa. Por favor, feche-o.")
              return None


         if wait_time % 15 == 0: # Imprime uma mensagem a cada 15 segundos
             print(f"Ainda aguardando por '{screenshot_marked_path}' ser modificado/criado... ({wait_time}s)")


    # --- Tentar encontrar a marcação preta na imagem marcada ---
    print(f"\nProcurando a marcação preta em '{screenshot_marked_path}'...")
    mark_position = find_black_mark(screenshot_original_path, screenshot_marked_path)

    # --- Recortar a área do template da imagem original (sem a marcação) usando o bounding box da marcação ---

    # Carregar a imagem original para o recorte
    original_for_crop = cv2.imread(screenshot_original_path)
    if original_for_crop is None:
         print(f"Erro: Não foi possível recarregar a imagem original para recorte em {screenshot_original_path}")
         # Limpar o arquivo marcado temporário
         try:
             if os.path.exists(screenshot_marked_path): os.remove(screenshot_marked_path)
         except PermissionError:
              print(f"Aviso: Não foi possível remover o arquivo marcado '{screenshot_marked_path}'. Ele pode estar em uso por outro programa. Por favor, feche-o.")
         # Não remover a original aqui, pois o erro já indica que não foi carregada, a remoção será feita após o if
         return None


    if mark_position:
        mark_x, mark_y, mark_w, mark_h = mark_position

        # As coordenadas do bounding box (x, y, w, h) são exatamente a área de recorte
        crop_x1 = mark_x
        crop_y1 = mark_y
        crop_x2 = mark_x + mark_w
        crop_y2 = mark_y + mark_h

        # Realizar o recorte da imagem original (sem a marcação) usando as coordenadas do bounding box
        template_image = original_for_crop[crop_y1:crop_y2, crop_x1:crop_x2]

        # Salvar o template recortado
        cv2.imwrite(template_generated_path, template_image)
        print(f"Template gerado e salvo como '{template_generated_filename}'.") # Printando apenas o nome do arquivo gerado

        # --- Limpar arquivos temporários APÓS o template ser salvo ---
        try:
            if os.path.exists(screenshot_original_path):
                os.remove(screenshot_original_path)
                print(f"Arquivo temporário '{screenshot_original_path}' removido.")
        except PermissionError:
            print(f"Aviso: Não foi possível remover o arquivo original '{screenshot_original_path}'. Ele pode estar em uso por outro programa. Por favor, feche-o.")

        try:
            if os.path.exists(screenshot_marked_path):
                os.remove(screenshot_marked_path)
                print(f"Arquivo temporário '{screenshot_marked_path}' removido.")
        except PermissionError:
            print(f"Aviso: Não foi possível remover o arquivo marcado '{screenshot_marked_path}'. Ele pode estar em uso por outro programa. Por favor, feche-o.")


        # Retorna o NOME do arquivo de template criado (não o caminho completo)
        return template_generated_filename

    else:
        print("Não foi possível detectar a marcação preta. Falha na criação do template.")
        # Limpar arquivos temporários em caso de falha na detecção da marcação
        try:
            if os.path.exists(screenshot_original_path): os.remove(screenshot_original_path) # Remover agora
        except PermissionError:
             print(f"Aviso: Não foi possível remover o arquivo original '{screenshot_original_path}'. Ele pode estar em uso por outro programa. Por favor, feche-o.")
        try:
            if os.path.exists(screenshot_marked_path): os.remove(screenshot_marked_path)
        except PermissionError:
             print(f"Aviso: Não foi possível remover o arquivo marcado '{screenshot_marked_path}'. Ele pode estar em uso por outro programa. Por favor, feche-o.")
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
        # Removido o menu de escolha do tipo de passo
        # print("Escolha o tipo de passo a gravar:")
        # print("  t: Template de Imagem (Usar assistente de marcação na screenshot)")
        # print("  c: Coordenadas Diretas (Capturar toque na tela)")
        # print("  w: Espera (gravar um tempo fixo)")
        # print("  q: Sair e Salvar")

        # step_type_choice = input("Digite a opção (t, c, w, q): ").lower() # Removido a entrada do usuário para escolha do tipo

        # Forçar o tipo de passo para 't' (Template)
        step_type_choice = 't' # Define o tipo de passo diretamente como 't'

        if step_type_choice == 'q': # Ainda permite sair digitando 'q' no input subsequente se implementado
            print("\nSaindo do modo de gravação.")
            break # Sai do loop principal

        elif step_type_choice == 't':
            print("\n--> Gravando Passo de Template de Imagem (por marcação) <--")
            # Chama o assistente para criar o arquivo de template usando detecção de marcação
            # Agora create_action_template_by_marking retorna apenas o nome do arquivo
            template_filename = create_action_template_by_marking(action_name, current_step_number, device_id=device_id)

            if template_filename: # Verifica se o nome do arquivo foi retornado (sucesso)
                 # Se o template foi criado com sucesso, adiciona um modelo de passo ao JSON
                 step_config = {
                     "name": f"Passo {current_step_number}: Template {template_filename}", # Nome padrão
                     "type": "template",
                     "template_file": template_filename,
                     "action_on_found": "click", # Ação padrão ao encontrar
                     "click_delay": 0.5, # Delay padrão após o clique
                     "click_offset": [0, 0], # Novo campo: Deslocamento [x, y] em pixels a partir do centro do template
                     # Adicionando defaults para action_before_find e action_after_find como comentários
                     # "#action_before_find": { # Exemplo de scroll antes de encontrar o template
                     # # "type": "scroll",
                     # # "direction": "up",
                     # # "duration_ms": 500,
                     # # "delay_after_scroll": 0.5
                     # },
                     # "#action_after_find": { # Exemplo de scroll após encontrar o template
                     # # "type": "scroll",
                     # # "direction": "down",
                     # # "duration_ms": 500,
                     # # "delay_after_scroll": 0.5
                     # },
                     "max_attempts": 5, # Aumentado o default para 5 tentativas
                     "attempt_delay": 1.0, # Mantido o delay entre tentativas
                     "initial_delay": 2.0 # Adicionado um atraso inicial padrão de 2 segundos
                 }
                 action_sequence.append(step_config)
                 print(f"Passo de Template '{template_filename}' adicionado à sequência (modelo com defaults).")
                 print("Lembre-se de editar o arquivo sequence.json para ajustar este passo (mudar delays, adicionar scroll, offset, etc.).")
            else:
                 print("Falha ao criar o template. Passo de template NOT added to the sequence.")


        # Os tipos 'c' e 'w' foram removidos do fluxo principal de gravação assistida
        # elif step_type_choice == 'c':
        #     print("\n--> Gravando Passo de Coordenadas Diretas <--")
        #     # Lógica para capturar coordenadas...
        #     print("Funcionalidade desativada neste modo.")


        # elif step_type_choice == 'w':
        #     print("\n--> Gravando Passo de Espera <--")
        #     # Lógica para gravar espera...
        #     print("Funcionalidade desativada neste modo.")


        else:
             # Esta parte se torna inalcançável com a escolha forçada para 't'
             print("Opção inválida. Digite 't', 'c', 'w' ou 'q'.")
             continue # Volta para o início do loop para pedir a opção novamente

        # --- Salvar a sequência após cada passo ---
        # Salvar após cada passo é mais seguro caso algo dê errado ou o script seja interrompido.
        try:
            # JSON não suporta comentários nativamente no formato.
            # Uma alternativa é usar chaves que começam com um prefixo de comentário, como '#'.
            # Ao carregar o JSON para execução, a função execultar_acoes precisará ignorar ou tratar essas chaves.
            with open(sequence_filepath, 'w', encoding='utf-8') as f:
                json.dump(action_sequence, f, indent=4) # Usar indent=4 para facilitar a leitura
            print(f"\nSequência atual salva em: {sequence_filepath}")
        except Exception as e:
            print(f"Erro ao salvar a sequência em {sequence_filepath}: {e}")


    # --- Fim do loop principal ---

    print(f"\nGravação da sequência de ações para '{action_name}' finalizada.")


if __name__ == "__main__":
    print("=== Assistente de Criação de Templates ===")
    action_name_to_record = input("Digite o nome da ação para gravar (ex: entrar_rallys): ").strip()
    
    if action_name_to_record:
        # Tenta pegar o device ID do .env se possível, senão usa padrão ou None
        device_id_recording = None
        try:
            from dotenv import load_dotenv
            load_dotenv()
            device_id_recording = os.getenv("DEFAULT_DEVICE_ID")
        except ImportError:
            pass
            
        if not device_id_recording:
            device_id_recording = 'RXCTB03EXVK' # Fallback
            
        print(f"Iniciando gravação para ação: '{action_name_to_record}' no device: {device_id_recording}")
        record_action_sequence_assisted(action_name_to_record, device_id=device_id_recording)
    else:
        print("Nome da ação não fornecido. Encerrando.")