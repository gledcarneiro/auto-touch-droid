# Nome do Arquivo: eee823d0_action_executor.py
# Descrição: Contém a função principal para executar sequências de ações lidas de um arquivo sequence.json
#            e funções auxiliares relacionadas à execução, incluindo a execução unificada de login.
# Versão: 01.00.07 -> Adicionada a função execute_login_for_account para unificar a execução de login.
# Versão: 01.00.08 -> Adicionada lógica para verificar uma imagem de sucesso após cada passo e parar a ação se encontrada.
# Versão: 01.00.09 -> Ajustada a função execultar_acoes para carregar sequence.json em dois formatos (lista ou dicionário com 'sequence').
# Versão: 01.00.10 -> Corrigido UnboundLocalError para success_image_config quando usando sequence_override.
# Versão: 01.00.11 -> Corrigido o caminho do template ao usar sequence_override para garantir que a pasta da ação correta seja usada.
# Versão: 01.00.12 -> Corrigido processamento de action_before_find quando usando sequence_override.
# Versão: 01.00.13 -> Adicionada função wait_for_template() para otimização de velocidade (substitui time.sleep por detecção ativa).
# Analista: Antigravity
# Programador: Gled Carneiro
# -----------------------------------------------------------------------------
import time
import os
import json
import re
import subprocess # Importar subprocess explicitamente

# Importando funções dos módulos do backend
try:
    from .adb_utils import capture_screen, simulate_touch
    from .image_detection import find_image_on_screen
except ImportError:
    from adb_utils import capture_screen, simulate_touch
    from image_detection import find_image_on_screen


# ---------------------------------------------------------------------------
# Função de Espera Inteligente por Template (Otimização de Velocidade)
# ---------------------------------------------------------------------------
def wait_for_template(template_path, device_id=None, screenshot_path="temp_screenshot_wait.png", 
                      timeout=10, interval=0.2, post_detection_delay=0.5):
    """
    Espera até que um template apareça na tela (substitui time.sleep por detecção ativa).
    
    Esta função implementa "polling inteligente" ao invés de espera fixa, permitindo que
    o bot continue assim que o elemento estiver pronto, economizando tempo significativo.
    
    Args:
        template_path (str): Caminho do template a detectar
        device_id (str, optional): ID do dispositivo Android
        screenshot_path (str, optional): Caminho temporário para screenshots
        timeout (float): Tempo máximo de espera em segundos (default: 10)
        interval (float): Intervalo entre capturas em segundos (default: 0.2)
        post_detection_delay (float): Delay APÓS detectar o template para animações (default: 0.5)
    
    Returns:
        tuple: (x, y, w, h) se encontrado, None se timeout
    
    Example:
        # Ao invés de:
        time.sleep(2.0)
        
        # Use:
        wait_for_template("04_juntar.png", timeout=3, post_detection_delay=0.3)
    """
    start_time = time.time()
    attempts = 0
    
    # Ensure the directory for the temp screenshot exists
    temp_dir = os.path.dirname(screenshot_path)
    if temp_dir and not os.path.exists(temp_dir):
        try:
            os.makedirs(temp_dir)
        except OSError:
            screenshot_path = os.path.basename(screenshot_path)  # Fallback to current directory
    
    print(f"⏳ Aguardando template '{os.path.basename(template_path)}' (timeout: {timeout}s)...")
    
    while (time.time() - start_time) < timeout:
        attempts += 1
        
        # Captura e detecta
        if not capture_screen(device_id=device_id, output_path=screenshot_path):
            # Se falhar a captura, aguarda e tenta novamente
            time.sleep(interval)
            continue
        
        result = find_image_on_screen(screenshot_path, template_path)
        
        # Limpa screenshot temporário
        if os.path.exists(screenshot_path):
            try:
                os.remove(screenshot_path)
            except (PermissionError, Exception):
                pass  # Ignora erros de remoção
        
        if result:
            elapsed = time.time() - start_time
            # print(f"✅ Template encontrado em {attempts} tentativas ({elapsed:.2f}s)")
            
            # NÃO aplicar delay aqui - será aplicado DEPOIS de extrair coordenadas
            # para garantir que o clique aconteça na posição correta após animação
            
            return result
        
        # Intervalo entre tentativas
        time.sleep(interval)
    
    # Timeout atingido
    elapsed = time.time() - start_time
    print(f"⏱️ Timeout após {attempts} tentativas ({elapsed:.2f}s)")
    print(f"⚠️ Template '{os.path.basename(template_path)}' não encontrado")
    return None


def capturar_posicao_login_cav_dinamica(device_id=None):
    """
    Captura dinamicamente a posição do template '04_login_cav.png' na tela atual.
    
    Args:
        device_id (str, optional): ID do dispositivo Android
        
    Returns:
        tuple: (x, y) coordenadas do login_cav ou None se não encontrado
    """
    template_path = os.path.join("backend", "actions", "templates", "fazer_login", "04_login_cav.png")
    
    if not os.path.exists(template_path):
        print(f"⚠️  Template '04_login_cav.png' não encontrado em: {template_path}")
        return None
    
    try:
        # Capturar screenshot atual
        screenshot_path = "temp_screenshot_for_cav_detection.png"
        capture_screen(device_id, screenshot_path)
        
        # Buscar o template na tela
        result = find_image_on_screen(template_path, screenshot_path)
        
        if result:
            # Calcular coordenadas do centro do template (como faz o sistema normal)
            template_x, template_y, template_w, template_h = result
            center_x = template_x + template_w // 2
            center_y = template_y + template_h // 2
            
            # print(f"🎯 POSIÇÃO DINÂMICA DO LOGIN_CAV: Template encontrado em ({template_x}, {template_y})")
            # print(f"🎯 COORDENADAS DO CENTRO: ({center_x}, {center_y})")
            
            # Limpar screenshot temporário
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)
                
            return (center_x, center_y)
        else:
            print(f"❌ Template '04_login_cav.png' não encontrado na tela atual")
            
            # Limpar screenshot temporário
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)
                
            return None
            
    except Exception as e:
        print(f"❌ Erro ao capturar posição dinâmica do login_cav: {e}")
        return None

def calcular_posicao_conta_relativa(account_name, account_index, device_id=None):
    """
    Calcula a posição e scroll necessários para uma conta baseado na NOVA estratégia simplificada.
    
    NOVA ESTRATÉGIA SIMPLIFICADA (sugestão do usuário):
    - login_gled (índice 0): Posição fixa, sem scroll
    - login_inf (índice 1): Posição fixa, sem scroll  
    - login_cav (índice 2): Posição fixa, sem scroll - POSIÇÃO DE REFERÊNCIA
    - login_c52+ (índice 3+): Usar posição da login_cav + scroll incremental simples
    
    Args:
        account_name (str): Nome da conta (ex: 'login_gled')
        account_index (int): Índice da conta na lista (0-based)
        device_id (str, optional): ID do dispositivo Android
    
    Returns:
        dict: {
            'scroll_needed': bool,
            'scroll_count': int,  # Número de scrolls incrementais
            'click_position': tuple (x, y),
            'description': str
        }
    """
    
    # Posições fixas das 3 primeiras contas (sem scroll) - mantém detecção normal
    # Para contas c52+ (índice 3+): usar posição DINÂMICA da login_cav + scroll incremental
    SCROLL_UNIT = 1  # Número de scrolls por conta (incremental simples)
    
    # AJUSTE FINO: Controle mais preciso do scroll
    # Cada conta c52+ precisa de scroll incremental para ficar na posição da login_cav
    SCROLL_PRECISION_FACTOR = 1.2  # Fator de ajuste para scroll mais preciso
    
    if account_index <= 2:
        # Primeiras 3 contas: usam detecção normal (clicam onde encontram o template)
        resultado = {
            'scroll_needed': False,
            'scroll_count': 0,
            'click_position': None,  # Será definido pela detecção do template
            'description': f"{account_name} (índice {account_index}): detecção normal"
        }
    else:
        # Contas c52+ (índice 3+): capturar posição dinâmica da login_cav + scroll incremental
        print(f"🔍 Capturando posição dinâmica do login_cav para {account_name}...")
        cav_position = capturar_posicao_login_cav_dinamica(device_id)
        
        if cav_position is None:
            # Fallback para posição fixa se não conseguir capturar dinamicamente
            print(f"⚠️  Usando posição de fallback para {account_name}")
            cav_position = (753, 966)  # Posição de fallback baseada no último teste
        
        scroll_count = int((account_index - 2) * SCROLL_PRECISION_FACTOR)  # Aplicar fator de precisão
        resultado = {
            'scroll_needed': True,
            'scroll_count': scroll_count,
            'click_position': cav_position,  # Clique "cego" na posição DINÂMICA
            'description': f"{account_name} (índice {account_index}): {scroll_count} scroll(s) OTIMIZADO → clique cego em {cav_position}"
        }
    
    print(f"🎯 POSICIONAMENTO OTIMIZADO: {resultado['description']}")
    if resultado['scroll_needed']:
        print(f"   Scrolls: {resultado['scroll_count']} | Clique: {resultado['click_position']}")
    else:
        print(f"   Sem scroll | Clique: {resultado['click_position']}")
    
    return resultado


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
        # print(f"Simulando scroll de coordenadas específicas: ({final_start_x}, {final_start_y}) para ({final_end_x}, {final_end_y})")
    else:
        # Usar coordenadas genéricas baseadas na direção (Landscape 2400x1080)
        landscape_width = 2400  # Largura em modo paisagem
        landscape_height = 1080 # Altura em modo paisagem
        center_x_landscape = landscape_width // 2

        if direction == "up":
            # Scroll para cima (conteúdo sobe): Gesto de baixo para cima na tela landscape.
            final_start_x, final_start_y = center_x_landscape, int(landscape_height * 0.75)  # Ajustado de 0.8 para 0.75
            final_end_x, final_end_y = center_x_landscape, int(landscape_height * 0.25)      # Ajustado de 0.2 para 0.25
            # print(f"Simulando scroll genérico OTIMIZADO na direção 'up'.")
        elif direction == "down":
            # Scroll para baixo (conteúdo desce): Gesto de cima para baixo na tela landscape.
            final_start_x, final_start_y = center_x_landscape, int(landscape_height * 0.25)  # Ajustado de 0.2 para 0.25
            final_end_x, final_end_y = center_x_landscape, int(landscape_height * 0.75)      # Ajustado de 0.8 para 0.75
            # print(f"Simulando scroll genérico OTIMIZADO na direção 'down'.")
        else:
            print(f"Aviso: Direção de scroll '{direction}' desconhecida e coordenadas não fornecidas. Pulando scroll.")
            return # Não executa o scroll se a configuração for inválida

    command = ["adb"]
    if device_id:
        command.extend(["-s", device_id])
    # input swipe <x1> <y1> <x2> <y2> [duration_ms]
    command.extend(["shell", "input", "swipe", str(final_start_x), str(final_start_y), str(final_end_x), str(final_end_y), str(duration_ms)])

    print(f"⚠️  Scroll simulado no dispositivo {device_id} iniciando em {final_start_x}, {final_start_y} para {final_end_x}, {final_end_y} em {duration_ms}ms")

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=(duration_ms / 1000.0) + 5) # Timeout um pouco maior que a duração do swipe
        # print("Scroll simulado com sucesso.")
        # print(f"DEBUG simulate_scroll stdout: {result.stdout.strip()}") # Comentado para evitar muita verbosidade
        # print(f"DEBUG simulate_scroll stderr: {result.stderr.strip()}") # Comentado para evitar muita verbosidade

        # Delay removido - já controlado por delay_after_scroll no sequence.json
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
    # print(f"Procurando template: {os.path.basename(template_path)}") # Printa só o nome do arquivo

    # Adicionar um atraso antes da primeira tentativa
    if initial_delay > 0:
        # print(f"Aguardando {initial_delay} segundos antes da primeira tentativa...")
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
    mostra_tentativas = False
    for attempt in range(1, max_attempts + 1):
        if mostra_tentativas:
            print(f"Tentativa {attempt}/{max_attempts} para encontrar o template '{os.path.basename(template_path)}'.")
            mostra_tentativas = False

        # 1. Capturar a tela
        if not capture_screen(device_id=device_id, output_path=screenshot_path):
            mostra_tentativas = True
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
            # print(f"Template '{os.path.basename(template_path)}' encontrado na tentativa {attempt} em ({x}, {y}).")
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


def execultar_acoes(action_name, device_id=None, sequence_override=None, account_name=None, fila_atual=None):
    """
    Executa uma sequência de ações lidas de um arquivo sequence.json
    na pasta da ação, onde cada item no JSON define um passo
    (template matching, clique, scroll, etc.).

    Args:
        action_name (str): O nome da ação a ser executada (corresponde ao nome da pasta).
        device_id (str, optional): O ID do dispositivo Android.
        sequence_override (list, optional): Uma lista de dicionários de passos para executar
                                           em vez de carregar do arquivo sequence.json.
                                           Útil para sequências dinâmicas (como login por conta).
        account_name (str, optional): O nome da conta sendo executada (para logs melhorados).

    Returns:
        bool: True se a execução da ação foi considerada bem-sucedida (terminou sem erros críticos
              ou encontrou a imagem de sucesso), False caso contrário.
    """
    # Initialize success_image_config before the conditional logic
    success_image_config = None

    # --- Define action_folder based on action_name regardless of override ---
    # Caminho para a pasta de ações na nova estrutura
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    acoes_folder = os.path.join(backend_dir, "actions", "templates")
    action_folder = os.path.join(acoes_folder, action_name)
    if not os.path.isdir(action_folder):
         print(f"Erro: Pasta de ação '{action_folder}' não encontrada.")
         # Return False here as the folder is essential for templates even with override
         return False


    if sequence_override is not None:
        # Usar a sequência fornecida diretamente
        action_sequence = sequence_override
        # print(f"Executando sequência de ações fornecida por override ({len(action_sequence)} passos).")
        # When using override, success_image_config is not loaded from the overridden sequence JSON.
        # If success image check is needed, it must be handled by the caller (e.g., execute_login_for_account)
        # or the success config must be passed separately.
        # For now, success_image check in this function is only active for file-loaded sequences (see below).
        pass # sequence_override is not None, action_sequence is already set


    else:
        # Carregar a sequência de ações do arquivo JSON
        sequence_filepath = os.path.join(action_folder, "sequence.json")

        if not os.path.exists(sequence_filepath):
            print(f"Erro: Arquivo de sequência '{sequence_filepath}' não encontrado.")
            print("Certifique-se de que você criou e configurou o arquivo sequence.json para esta ação.")
            return False # Retorna False em caso de erro

        try:
            with open(sequence_filepath, 'r', encoding='utf-8') as f:
                action_data = json.load(f) # Carrega o conteúdo do JSON

            # --- Lógica para lidar com os dois formatos de JSON ---
            action_sequence = []
            # success_image_config is already initialized to None at the start

            if isinstance(action_data, list):
                # Formato antigo: a lista de passos está no nível raiz
                action_sequence = action_data
                print(f"Sequência de ações para '{action_name}' carregada (formato lista).")
                # No formato antigo, não há configuração de success_image
                success_image_config = None
            elif isinstance(action_data, dict) and "sequence" in action_data and isinstance(action_data["sequence"], list):
                 # Novo formato: dicionário com chave 'sequence' e opcionalmente 'success_image'
                 action_sequence = action_data["sequence"]
                 success_image_config = action_data.get("success_image") # Carrega a configuração da imagem de sucesso
                 print(f"Sequência de ações para '{action_name}' carregada (formato dicionário com 'sequence').")
                 if success_image_config:
                      print(f"Imagem de sucesso configurada para '{action_name}'.")
            else:
                 print(f"Erro: O conteúdo do arquivo '{sequence_filepath}' não tem a estrutura esperada (lista ou dicionário com chave 'sequence').")
                 return False # Retorna False em caso de estrutura inválida


            if not action_sequence:
                 print(f"Aviso: A lista de ações na chave 'sequence' do arquivo '{sequence_filepath}' está vazia. Nenhuma ação para executar.")
                 # Se carregou um dicionário mas a lista 'sequence' está vazia, ainda pode haver uma imagem de sucesso para verificar?
                 # Para uma sequência vazia, consideramos sucesso se não houver passos, a menos que haja uma imagem de sucesso que não foi encontrada.
                 # Vamos retornar True aqui se a lista de passos for vazia, independentemente da imagem de sucesso.
                 return True # Considera sucesso se não houver passos para executar


        except json.JSONDecodeError:
            print(f"Erro ao decodificar o arquivo JSON '{sequence_filepath}'. Verifique a sintaxe.")
            return False # Retorna False em caso de erro de JSON
        except Exception as e:
            print(f"Ocorreu um erro ao carregar o arquivo de sequência '{sequence_filepath}': {e}")
            return False # Retorna False em caso de outros erros


    # print(f"\nExecutando a ação: {action_name}")

    # Se houver uma imagem de sucesso configurada para esta ação, preparamos para verificá-la.
    # Esta parte agora é carregada DENTRO do bloco try/except de carregamento do JSON.
    success_image_path = None # Initialize before the check
    success_check_attempts = 1 # Default
    success_check_delay = 0.5 # Default

    # A configuração de success_image_config é carregada no bloco else acima, se carregando de arquivo.
    # Se a configuração veio do arquivo (sequence_override is None), a lógica de success_image_config já foi preenchida.
    # Se a sequência veio por override, success_image_config é None por padrão no início da função.
    # A verificação de imagem de sucesso ABAIXO só faz sentido na execução NORMAL (sem override).
    # Se precisarmos disso para a sequência de login temporária, a lógica deve estar na execute_login_for_account
    # ou a configuração de success_image deve ser passada para execultar_acoes.

    # A lógica de verificação de imagem de sucesso só deve ser ativada se success_image_config NÃO FOR NONE
    # E se NÃO estivermos usando sequence_override (ou se sequence_override incluir a configuração de sucesso).
    # Por enquanto, a verificação abaixo está ligada a sequence_override is None, o que está incorreto para a função execute_login_for_account.

    # Vamos simplificar temporariamente a lógica de verificação de sucesso AQUI (dentro de execultar_acoes)
    # para que ela funcione SOMENTE quando success_image_config for carregada do arquivo (ou seja, sequence_override is None)

    # --- Lógica de execução dos passos ---
    # print(f"\n🚀 INICIANDO EXECUÇÃO DA AÇÃO: '{action_name}' ({len(action_sequence)} passos)")
    # print("=" * 60)
    
    for i, step_config in enumerate(action_sequence):
        step_number = i + 1
        step_name = step_config.get("name", f"Passo {step_number}") # Usar nome do JSON ou default

        # print(f"\n🎯 PASSO {step_number}/{len(action_sequence)}: {step_name}")
        
        # Criar log melhorado com informações de ação e conta
        account_info = f" - Conta: {account_name}" if account_name else ""
        template_info = ""
        if step_config.get("type") == "template":
            template_filename = step_config.get("template_file", "N/A")
            template_info = f" - Template: {template_filename}"
        
        print(f"\n{fila_atual} - Acao: {action_name} {step_name}")
        # print("-" * 40)

        step_type = step_config.get("type")

        # --- VERIFICAR IMAGEM DE SUCESSO ANTES DE EXECUTAR O PASSO? ---
        # (Mantido o comentário, a verificação principal é após o passo)

        step_success = True # Flag para indicar se o passo individual foi bem-sucedido

        if step_type == "template":
            template_filename = step_config.get("template_file")
            action_on_found = step_config.get("action_on_found", "click") # Default action is click
            click_delay = step_config.get("click_delay", 0.5) # Default delay
            click_offset = step_config.get("click_offset", [0, 0]) # Obter o offset do JSON, default [0, 0]
            max_attempts = step_config.get("max_attempts", 1) # Default 1 attempt
            attempt_delay = step_config.get("attempt_delay", 1.0) # Default 1 second delay between attempts
            initial_delay = step_config.get("initial_delay", 0) # Novo campo para atraso inicial
            
            # NOVOS PARÂMETROS PARA MODO OTIMIZADO
            wait_enabled = step_config.get("wait_for_template", False)  # Ativa modo otimizado
            wait_timeout = step_config.get("wait_timeout", 10)  # Timeout de espera
            wait_interval = step_config.get("wait_interval", 0.2)  # Intervalo entre capturas
            post_delay = step_config.get("post_detection_delay", 0.5)  # Delay após detectar

            if not template_filename:
                print(f"Erro: Passo {step_number} ('{step_name}') do tipo 'template' não especifica 'template_file'. Pulando passo.")
                step_success = False
                continue # Pula para o próximo passo se faltar o template_file.

            # Construir o caminho COMPLETO para o template file, relativo à pasta da ação
            # Se estivermos usando override (chamado por execute_login_for_account), a action_name é "fazer_login"
            # e os templates como "01_google.png", "02_login_gled.png" estão dentro de acoes/fazer_login
            # template_path = os.path.join("acoes", action_name, template_filename) # OLD: This was the source of the bug.
            # NEW: action_folder is already defined at the beginning based on action_name
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
                      if before_type and not before_type.startswith("#"):
                           print(f"Aviso: Tipo de action_before_find '{before_type}' no {step_name} desconhecido/não implementado.")


            # --- Tentar encontrar o template ---
            # MODO OTIMIZADO (wait_for_template) ou MODO TRADICIONAL (find_and_optionally_click)
            found = False
            coords = None
            
            if wait_enabled:
                # ========== MODO OTIMIZADO: wait_for_template ==========
                print(f"🔍 PROCURANDO TEMPLATE {template_filename} MODO OTIMIZADO (wait_for_template)")
                print(f"⏱️  Timeout: {wait_timeout}s | Intervalo: {wait_interval}s | Delay pós-detecção: {post_delay}s")
                
                result = wait_for_template(
                    template_path,
                    device_id=device_id,
                    timeout=wait_timeout,
                    interval=wait_interval,
                    post_detection_delay=post_delay
                )
                
                if result:
                    found = True
                    x, y, w, h = result
                    center_x = x + w // 2
                    center_y = y + h // 2
                    coords = (center_x, center_y)
                else:
                    found = False
                    coords = None
                    
            else:
                # ========== MODO TRADICIONAL: find_and_optionally_click ==========
                print(f"🔍 PROCURANDO TEMPLATE  {template_filename} MODO TRADICIONAL (find_and_optionally_click)")
                print(f"🎯 Ação ao encontrar: {action_on_found}")
                print(f"🔄 Máximo de tentativas: {max_attempts}")
                print(f"⏱️  Delay entre tentativas: {attempt_delay}s")
                
                if initial_delay > 0:
                    print(f"⏳ Delay inicial: {initial_delay}s")
                
                # print("🔎 Iniciando busca na tela...")
                
                # Usando a função find_and_optionally_click que inclui tentativas e atraso inicial
                found, coords = find_and_optionally_click(
                    template_path,
                    device_id=device_id,
                    max_attempts=max_attempts,
                    attempt_delay=attempt_delay,
                    initial_delay=initial_delay # Passando o novo parâmetro
                )

            if found:
                # print(f"✅ TEMPLATE ENCONTRADO! Coordenadas: {coords}")
                
                if action_on_found == "click":
                    # Verificar se temos coordenadas forçadas (posicionamento relativo)
                    force_coords = step_config.get('force_click_coords')
                    if force_coords:
                        center_x, center_y = force_coords
                        # print(f"🎯 USANDO COORDENADAS FORÇADAS (posicionamento relativo): ({center_x}, {center_y})")
                    else:
                        # Se o template foi encontrado, simulamos o clique usando as coordenadas retornadas
                        center_x, center_y = coords

                    # APLICAR POST_DETECTION_DELAY AQUI (no modo otimizado)
                    # Aguarda DEPOIS de detectar mas ANTES de clicar
                    # Isso garante que animações (como slide) terminem antes do clique
                    if wait_enabled and post_delay > 0:
                        print(f"⏳ Aguardando {post_delay}s pós-detecção (animação)...")
                        time.sleep(post_delay)

                    # Aplicar o click_offset, se for uma lista válida de 2 elementos
                    if isinstance(click_offset, list) and len(click_offset) == 2:
                         final_click_x = center_x + click_offset[0]
                         final_click_y = center_y + click_offset[1]
                        #  print(f"🎯 Aplicando offset [{click_offset[0]}, {click_offset[1]}]")
                        #  print(f"👆 CLICANDO EM: ({final_click_x}, {final_click_y})")
                         simulate_touch(final_click_x, final_click_y, device_id=device_id)
                    else:
                         # Validar se click_offset foi especificado mas não é uma lista de 2 ints
                         if "click_offset" in step_config:
                              print(f"⚠️  Aviso: Configuração de click_offset inválida ({click_offset}) em {step_name}. Esperado [x, y].")
                         print(f"👆 CLICANDO EM: ({center_x}, {center_y})")
                         simulate_touch(center_x, center_y, device_id=device_id) # Clica no centro se o offset for inválido ou não especificado

                    # OTIMIZAÇÃO: No modo otimizado, post_detection_delay JÁ cumpre o papel de click_delay
                    if not wait_enabled and click_delay > 0:
                        #  print(f"⏳ Aguardando {click_delay}s após o clique...")
                         time.sleep(click_delay)
                    elif wait_enabled:
                         print(f"⚡ Modo otimizado: click_delay ignorado (post_detection_delay já aplicado)")
                    
                    # Log de sucesso melhorado
                    account_info = f" - Conta: {account_name}" if account_name else ""
                    print(f"🎉 SUCESSO [Passo {step_number}] - Template: {os.path.basename(template_path)} - Acao: {action_name}{account_info}")
                    step_success = True # Passo de template/click bem-sucedido
                
                elif action_on_found == "scroll_then_click":
                    # PRIMEIRO executa o scroll, DEPOIS clica
                    # print(f"🔄 EXECUTANDO: Scroll primeiro, depois clique")
                    
                    # Executar action_after_find ANTES do clique
                    action_after = step_config.get("action_after_find")
                    if action_after and isinstance(action_after, dict):
                        after_type = action_after.get("type")
                        if after_type == "scroll":
                            scroll_direction = action_after.get("direction", "down")
                            scroll_duration = action_after.get("duration_ms", 500)
                            delay_after_scroll_after = action_after.get("delay_after_scroll", 0.5)
                            scroll_start_coords = action_after.get("start_coords")
                            scroll_end_coords = action_after.get("end_coords")

                            # print(f"📜 PRIMEIRO: Executando scroll {scroll_direction} por {scroll_duration}ms")
                            simulate_scroll(
                                device_id=device_id,
                                direction=scroll_direction,
                                duration_ms=scroll_duration,
                                start_coords=scroll_start_coords,
                                end_coords=scroll_end_coords
                            )
                            # print(f"⏳ Aguardando {delay_after_scroll_after}s após o scroll...")
                            time.sleep(delay_after_scroll_after)
                    
                    # AGORA executa o clique
                    center_x, center_y = coords
                    
                    # APLICAR POST_DETECTION_DELAY AQUI (no modo otimizado)
                    # Aguarda DEPOIS de detectar mas ANTES de clicar
                    if wait_enabled and post_delay > 0:
                        print(f"⏳ Aguardando {post_delay}s pós-detecção (animação)...")
                        time.sleep(post_delay)
                    
                    if isinstance(click_offset, list) and len(click_offset) == 2:
                         final_click_x = center_x + click_offset[0]
                         final_click_y = center_y + click_offset[1]
                         print(f"🎯 Aplicando offset [{click_offset[0]}, {click_offset[1]}]")
                         print(f"👆 SEGUNDO: CLICANDO EM: ({final_click_x}, {final_click_y})")
                         simulate_touch(final_click_x, final_click_y, device_id=device_id)
                    else:
                         if "click_offset" in step_config:
                              print(f"⚠️  Aviso: Configuração de click_offset inválida ({click_offset}) em {step_name}. Esperado [x, y].")
                         print(f"👆 SEGUNDO: CLICANDO NO CENTRO: ({center_x}, {center_y})")
                         simulate_touch(center_x, center_y, device_id=device_id)

                    # OTIMIZAÇÃO: No modo otimizado, post_detection_delay JÁ cumpre o papel de click_delay
                    if not wait_enabled and click_delay > 0:
                        #  print(f"⏳ Aguardando {click_delay}s após o clique...")
                         time.sleep(click_delay)
                    elif wait_enabled:
                         print(f"⚡ Modo otimizado: click_delay ignorado (post_detection_delay já aplicado)")
                    
                    # Log de sucesso melhorado para scroll_then_click
                    account_info = f" - Conta: {account_name}" if account_name else ""
                    print(f"🎉 SUCESSO [Passo {step_number}] - Template: {os.path.basename(template_path)} - Acao: {action_name}{account_info}")
                    step_success = True
                    # Não executar action_after_find novamente, pois já foi executado
                # TODO: Adicionar outros tipos de action_on_found aqui (ex: swipe a partir do template)
                else:
                    # Ignora chaves que começam com '#'
                    if action_on_found and not action_on_found.startswith("#"):
                        print(f"Aviso: Tipo de action_on_found '{action_on_found}' no {step_name} desconhecido/não implementado. Template encontrado, mas ação não executada.")
                        step_success = False # Considera falha se a ação no template não puder ser executada/reconhecida

            else:
                # print(f"❌ FALHA: Template NÃO encontrado!")
                # print(f"🔍 Arquivo procurado: {os.path.basename(template_path)}")
                # print(f"🔄 Tentativas realizadas: {max_attempts}")
                # print(f"⚠️  PASSO FALHOU: {step_name}")
                # print(f"🛑 PARANDO EXECUÇÃO PARA ANÁLISE DO PROBLEMA...")
                step_success = False # Passo de template falhou
                return False  # Para a execução imediatamente


            # --- Processar action_after_find ---
            # Não executar se já foi processado no scroll_then_click
            if action_on_found != "scroll_then_click":
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


                 # Adicionar aqui a lógica para verificar a imagem de sucesso APÓS este passo se configurado
                 # Esta é uma alternativa a verificar após CADA passo de template.
                 # Se a configuração `success_image` estiver no JSON principal da ação,
                 # podemos verificar aqui após cada passo de template.

                 # else:
                 #      # Ignora chaves que começam com '#'
                 #      if after_type and not after_type.startswith("#"):
                 #           print(f"Aviso: Tipo de action_after_find '{after_type}' no {step_name} desconhecido/não implementado.")


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
                  step_success = True
             else:
                  print(f"Erro: Passo {step_number} ('{step_name}') do tipo 'coords' não especifica 'coordinates' válidas ([x, y]). Pulando passo.")
                  step_success = False


        elif step_type == "scroll":
             # Implementar lógica para scroll direto
             scroll_direction = step_config.get("direction", "up")
             scroll_duration = step_config.get("duration_ms", 500)
             delay_after_scroll = step_config.get("delay_after_scroll", 0.5)
             scroll_start_coords = step_config.get("start_coords")
             scroll_end_coords = step_config.get("end_coords")
             
             print(f"🔄 Executando {step_name}: Scroll {scroll_direction} por {scroll_duration}ms")
             simulate_scroll(
                 device_id=device_id,
                 direction=scroll_direction,
                 duration_ms=scroll_duration,
                 start_coords=scroll_start_coords,
                 end_coords=scroll_end_coords
             )
             
             if delay_after_scroll > 0:
                 print(f"⏳ Aguardando {delay_after_scroll}s após o scroll...")
                 time.sleep(delay_after_scroll)
             
             print(f"✅ {step_name} concluído com sucesso.")
             step_success = True

        elif step_type == "wait":
             # Implementar lógica para esperar um tempo fixo
             wait_time = step_config.get("duration_seconds")
             if isinstance(wait_time, (int, float)) and wait_time > 0:
                  print(f"Executando {step_name}: Esperando por {wait_time} segundos.")
                  time.sleep(wait_time)
                  print(f"{step_name} (espera) concluído com sucesso.")
                  step_success = True
             else:
                  print(f"Erro: Passo {step_number} ('{step_name}') do tipo 'wait' não especifica 'duration_seconds' válida. Pulando passo.")
                  step_success = False


        # Ignorar chaves de comentário
        elif step_type is not None and step_type.startswith("#"):
             pass

        else:
             # Ignora chaves que começam com '#'
             if step_type and not step_type.startswith("#"):
                  print(f"Erro: Passo {step_number} ('{step_name}') tem tipo '{step_type}' desconhecido ou faltando. Pulando passo.")
             step_success = False # Considera falha se o tipo for inválido/não implementado

        # --- VERIFICAR IMAGEM DE SUCESSO APÓS EXECUTAR O PASSO ---
        # Esta verificação SÓ faz sentido se success_image_config foi carregada (ou seja, sequence_override is None)
        # OU se a configuração de success_image foi explicitamente passada via sequence_override (o que não fazemos atualmente).
        # Para a lógica atual do menu, a verificação só é necessária quando executando a ação "fazer_login"
        # com a sequência TEMPORÁRIA gerada em execute_login_for_account.
        # A forma como a lógica de success_image_config está estruturada atualmente na execultar_acoes
        # a torna difícil de usar com sequence_override.

        # VAMOS MOVER A LÓGICA DE VERIFICAÇÃO DE IMAGEM DE SUCESSO PARA FORA DO execultar_acoes
        # e colocá-la na execute_login_for_account, que lida com o fluxo de login por conta.

        # RESUMO DO PASSO
        # print(f"\n📊 RESUMO DO PASSO {step_number}:")
        # if step_success:
        #     print(f"✅ Status: SUCESSO")
        #     print(f"🎯 Passo: {step_name}")
        #     print(f"🔧 Tipo: {step_type}")
        # else:
        #     print(f"❌ Status: FALHA")
        #     print(f"⚠️  Passo: {step_name}")
        #     print(f"🔧 Tipo: {step_type}")
        #     print(f"💡 Verifique se o template existe e está visível na tela!")
        
        # print("=" * 50)
        
        # OTIMIZAÇÃO: Delay entre passos reduzido no modo otimizado
        # No modo otimizado, wait_for_template já gerencia a espera necessária
        if step_type == "template" and wait_enabled:
            # Modo otimizado: delay mínimo apenas para estabilidade
            # print("⚡ Modo otimizado: delay entre passos reduzido (0.1s)")
            time.sleep(0.1)
        elif action_name == "pegar_recursos":
            # print("⏳ Aguardando 0.5 segundos antes do próximo passo...")
            time.sleep(0.5)  # Delay reduzido para recursos já visíveis
        else:
            # print("⏳ Aguardando 0.5 segundos antes do próximo passo...")
            time.sleep(0.5)  # Pausa padrão entre passos para observação
        
        # REMOVENDO VERIFICAÇÃO DE SUCESSO DAQUI TEMPORARIAMENTE para simplificar
        # if sequence_override is None and success_image_config and isinstance(success_image_config, dict) and step_success: # Verifica após um passo bem-sucedido
        #      print(f"Verificando imagem de sucesso após {step_name}...")
        #      # ... lógica de find_and_optionally_click para imagem de sucesso ...
        #      if success_found:
        #          print(f"\n!!! Imagem de sucesso encontrada após {step_name}. Interrompendo execução da ação '{action_name}'. !!!")
        #          return True # Retorna True para indicar sucesso e parar a execução da ação atual

        # Se o passo falhou e não estamos em uma sequência de override (execução normal de uma ação)
        # e não há uma imagem de sucesso configurada para parar a ação em caso de falha no passo,
        # podemos querer parar a execução da ação inteira.
        # A lógica anterior já para a execução da ação se um template ESSENCIAL não for encontrado,
        # pois find_and_optionally_click retorna False e a lógica de "if found:" falha.
        # Isso está OK para a maioria dos casos.


    # print(f"\nExecução da ação '{action_name}' finalizada (chegou ao fim da sequência).")
    # Se chegou ao fim da sequência, consideramos a execução bem-sucedida, a menos que um erro tenha ocorrido em um passo.
    # A lógica de retorno True/False agora deve refletir se a sequência terminou SEM um erro crítico em um passo.
    # Se um template NÃO for encontrado, a função já retorna False.
    # Se o loop terminar sem um retorno False anterior, significa que todos os passos foram processados (ou pulados).
    return True # Retorna True se a função chegou ao fim da sequência sem interrupção por erro de template.


# --- Nova função para executar a ação de login para uma conta específica ---
# Esta função irá adaptar a sequência original para cada conta
def execute_login_for_account(account_info, original_sequence, device_id=None):
    """
    Executa a sequência de login, adaptando o passo do template de email
    para a conta fornecida usando posicionamento relativo matemático.

    Args:
        account_info (dict): Dicionário contendo informações da conta (ex: {"name": "login_gled"}).
        original_sequence (list): A lista de passos da sequência de ação lida do sequence.json.
        device_id (str, optional): O ID do dispositivo Android.

    Returns:
        bool: True se a execução da sequência de login para esta conta foi considerada bem-sucedida
              (encontrou a imagem de sucesso durante a execução), False caso contrário.
    """
    if not original_sequence:
        print("Erro: Sequência de ação original não fornecida ou vazia.")
        return False

    account_name = account_info.get("name")
    if not account_name:
        print("Aviso: Nome da conta não especificado. Pulando esta conta.")
        return False

    # Importar lista de contas para obter o índice
    try:
        import sys
        import os
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.append(os.path.join(backend_dir, 'config'))
        from accounts_config import accounts
        
        # Encontrar o índice da conta atual
        account_index = None
        for i, account in enumerate(accounts):
            if account.get('name') == account_name:
                account_index = i
                break
        
        if account_index is None:
            print(f"Erro: Conta '{account_name}' não encontrada na lista de contas.")
            return False
            
    except ImportError:
        print("Erro: Não foi possível importar accounts_config. Usando posicionamento padrão.")
        account_index = 0

    print(f"\n--- Tentando fazer login com a conta: {account_name} (índice: {account_index}) ---")
    
    # Calcular posicionamento relativo para esta conta
    posicionamento = calcular_posicao_conta_relativa(account_name, account_index, device_id)
    print(f"📍 {posicionamento['description']}")

    # Criar uma sequência TEMPORÁRIA para esta conta, incluindo o passo do Google (se existir)
    # e APENAS o passo do template de email correspondente à conta atual.
    modified_sequence_for_execution = []
    email_template_step_found = False # Renomeado para maior clareza

    for step in original_sequence:
        step_type = step.get("type")
        # Criar uma cópia profunda do passo para inclusão na sequência temporária
        modified_step = json.loads(json.dumps(step))

        if step_type == "template":
            template_filename = modified_step.get("template_file")

            # Adicionar o passo do template do Google (ou outros passos comuns antes do email)
            if template_filename and template_filename == "01_google.png":
                 modified_sequence_for_execution.append(modified_step)
                 print(f"  Incluindo passo universal: '{modified_step.get('name')}'")

            # Na função execute_login_for_account, simplesmente adicionar o passo:
            elif template_filename and template_filename.endswith('.png') and account_name in template_filename:
                print(f"  Incluindo passo de template específico da conta '{account_name}'")
                print(f"  📜 O scroll será executado via action_before_find do JSON")
                modified_sequence_for_execution.append(modified_step)
                email_template_step_found = True

            else:
                 # Ignora outros passos de template que não são o Google nem o email da conta atual
                 print(f"  Ignorando passo de template '{template_filename}' para a conta '{account_name}'.")
                 pass # Não adiciona este passo à sequência temporária para esta conta


        elif step_type in ["coords", "wait"]:
             # Adiciona passos de coordenadas ou espera que vêm DEPOIS do passo do Google e ANTES do passo de email,
             # ou que vêm DEPOIS do passo de email.
             # Com a estrutura atual do JSON, onde cada conta tem seu email step logo após o Google step,
             # pode não haver passos "coords" ou "wait" ENTRE o Google e o email.
             # Mas se houver, eles serão incluídos aqui.
             modified_sequence_for_execution.append(modified_step)
             print(f"  Incluindo passo de tipo '{step_type}': '{modified_step.get('name')}'")


        # Ignorar chaves de comentário
        elif step_type is not None and step_type.startswith("#"):
             pass
        else:
             print(f"  Aviso: Tipo de passo desconhecido ou faltando em '{step.get('name', 'Passo desconhecido')}' para a conta '{account_name}'. Ignorando.")


    if not email_template_step_found:
        print(f"Erro: Não foi encontrado um passo de template que corresponda ao nome da conta '{account_name}' na sequência original. Certifique-se de que o nome da conta está no nome do arquivo do template de email no sequence.json.")
        return False # Não executa se não encontrar o template de email para a conta


    # --- Executar a sequência TEMPORÁRIA criada para esta conta ---
    # print(f"\nExecutando sequência temporária para a conta '{account_name}' ({len(modified_sequence_for_execution)} passos):")

    # Chamamos a função execultar_acoes, passando a sequência modificada como override
    # O nome da ação ("fazer_login") ainda é necessário para que execultar_acoes saiba onde encontrar os templates
    # (na pasta acoes/fazer_login) e também a imagem de sucesso configurada no JSON principal dessa ação.
    login_execution_success = execultar_acoes(action_name="fazer_login", device_id=device_id, sequence_override=modified_sequence_for_execution)

    # A função execultar_acoes agora retorna True se a imagem de sucesso for encontrada
    # (ou a sequência terminar sem erros em execução normal sem override), e False em caso de erro.
    # Para a execução de login por conta (com override), ela retornará True se a imagem de sucesso
    # for encontrada durante a execução da sequência TEMPORÁRIA.

    return login_execution_success # Retorna o resultado da execução da sequência temporária

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