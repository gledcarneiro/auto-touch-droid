# Nome do Arquivo: entrar_todos_rallys.py
# Descrição: Bot de Rally com Tarefas Secundárias (Baú, Recursos, Mobs) - Versão 4.2
# Versão: 04.02.00 (Scroll Configurável via JSON)
# Analista: Antigravity
# Programador: Gled Carneiro
# -----------------------------------------------------------------------------

import sys
import os
import time
import json
import subprocess
from datetime import datetime

# ---------------------------------------------------------------------------
# Configuração de caminho e importação de módulos do projeto
# ---------------------------------------------------------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)          # backend
project_root = os.path.dirname(backend_dir)        # raiz do projeto
if project_root not in sys.path:
    sys.path.append(project_root)

sys.path.append(os.path.join(backend_dir, "core"))
from action_executor import execultar_acoes, simulate_scroll
from adb_utils import simulate_touch, capture_screen
from image_detection import find_image_on_screen

# ---------------------------------------------------------------------------
# Configurações
# ---------------------------------------------------------------------------
try:
    from dotenv import load_dotenv
    load_dotenv()
    DEVICE_ID = os.getenv("DEFAULT_DEVICE_ID", "RXCTB03EXVK")
except Exception:
    DEVICE_ID = "RXCTB03EXVK"

RALLY_ACTION_NAME = "entrar_rallys"
MAX_FILAS = 9
OFFSETS_FIXOS = {
    1: 140,
    2: 360,
    3: 590
}
OFFSET_CLICK_APOS_SCROLL = 650

# FLAG GLOBAL: Controla se o bot está em modo Rally ou Tarefas Secundárias
FLAG_RALLY = True

# Template globais
GATILHO_TEMPLATE      = os.path.join(project_root, "backend", "actions", "templates", "_global", "prepara_voltar_rally.png")
TEMPLATE_MATAR_MOBS   = os.path.join(project_root, "backend", "actions", "templates", "_global", "prepara_matar_mobs.png")
TEMPLATE_BAU_RECURSOS = os.path.join(project_root, "backend", "actions", "templates", "_global", "prepara_pegar_bau_recursos.png")

# ---------------------------------------------------------------------------
# Funções Auxiliares
# ---------------------------------------------------------------------------
def verificar_dispositivo_conectado():
    """Verifica se o dispositivo está conectado via ADB."""
    try:
        result = subprocess.run(
            ["adb", "devices"], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        # Verifica se o DEVICE_ID está na lista de dispositivos
        return DEVICE_ID in result.stdout and "device" in result.stdout
    except Exception:
        return False

def aguardar_reconexao():
    """Aguarda o dispositivo reconectar. Retorna quando conectado."""
    import os
    
    # Limpa a tela (Windows: cls, Linux/Mac: clear)
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("\n" + "="*80)
    print("⚠️ DISPOSITIVO DESCONECTADO!")
    print("="*80)
    print(f"🔌 Aguardando reconexão do dispositivo {DEVICE_ID}...")
    print("💡 Plugue o cabo USB novamente para continuar.")
    print("="*80)
    print()  # Linha em branco
    
    tentativas = 0
    while True:
        tentativas += 1
        
        if verificar_dispositivo_conectado():
            print("\n\n" + "="*80)
            print(f"✅ DISPOSITIVO RECONECTADO! (após {tentativas} tentativas)")
            print("="*80)
            print("🔄 Resetando estado e reiniciando bot...")
            time.sleep(2.0)  # Aguarda estabilização
            return True
        
        # Mostra contador em linha única (sobrescreve)
        print(f"\r⏳ Tentativa {tentativas}... ", end='', flush=True)
        
        time.sleep(3.0)  # Aguarda 3s entre verificações

def execute_back(times=1, delay=0.3):
    """Executa o comando BACK N vezes."""
    for _ in range(times):
        try:
            subprocess.run(["adb", "-s", DEVICE_ID, "shell", "input", "keyevent", "4"], check=True)
            time.sleep(delay)
        except Exception as e:
            print(f"⚠️ Erro ao executar BACK: {e}")

def load_scroll_config():
    """Carrega configurações de scroll do JSON."""
    config_path = os.path.join(current_dir, "scroll_config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config.get("filas", {})
    except Exception as e:
        print(f"⚠️ Erro ao carregar scroll_config.json: {e}")
        print("⚠️ Usando configurações padrão de scroll.")
        return {}

def load_sequence(action_name):
    sequence_path = os.path.join(project_root, "backend", "actions", "templates", action_name, "sequence.json")
    try:
        with open(sequence_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list): return data
        if isinstance(data, dict) and "sequence" in data: return data["sequence"]
    except Exception:
        pass
    return None

def get_template_path(filename):
    return os.path.join(project_root, "backend", "actions", "templates", RALLY_ACTION_NAME, filename)

def verificar_gatilho(screenshot_path=os.path.join(project_root, "temp_screenshots", "temp_screenshot_rally.png")):
    """
    Verifica se o aviso de novo rally apareceu na screenshot atual.
    Retorna True se detectado, False caso contrário.
    """
    global FLAG_RALLY
    
    if not os.path.exists(GATILHO_TEMPLATE):
        # Se o template não existir, não verifica (evita erro)
        return False
    
    result = find_image_on_screen(screenshot_path, GATILHO_TEMPLATE)
    
    if result is not None:
        print("🚨 GATILHO DETECTADO! Novo Rally disponível!")
        return True
    
    return False

def clicar_preparacao(template_path, descricao):
    """
    Busca e clica em um template de preparação global.
    """
    print(f"🔎 Procurando preparação: {descricao}...")
    screenshot_path = os.path.join(project_root, "temp_screenshots", "temp_prep.png")
    capture_screen(DEVICE_ID, screenshot_path)
    result = find_image_on_screen(screenshot_path, template_path)
    
    if result:
        x, y, w, h = result
        center_x = x + w // 2
        center_y = y + h // 2
        print(f"✅ {descricao} encontrado! Clicando em ({center_x}, {center_y})...")
        simulate_touch(center_x, center_y, DEVICE_ID)
        time.sleep(5.0) # Tempo para a UI reagir e abrir o menu/mapa
        return True
    else:
        print(f"⚠️ {descricao} não encontrado. Seguindo fluxo...")
        return False

# ---------------------------------------------------------------------------
# Lógica de Navegação e Processamento (Rally)
# ---------------------------------------------------------------------------

def navegar_para_lista_rallys(rally_sequence):
    """
    Garante que estamos na tela de lista de rallys (Tela1-Aba).
    Fluxo Padrão: Aliança (01) -> Batalha (02).
    """
    print("\n🧭 Navegando para a Lista de Rallys (Fluxo Inicial)...")
    
    # Sempre tentar o fluxo completo para garantir o estado correto
    print("1️⃣ Clicando em 'Aliança' (01_alianca.png)...")
    if execultar_acoes(RALLY_ACTION_NAME, device_id=DEVICE_ID, account_name="current", sequence_override=[rally_sequence[0]]):
        print("✅ 'Aliança' clicado.")
        time.sleep(0.8)
        
        print("2️⃣ Clicando em 'Batalha' (02_batalha.png)...")
        if execultar_acoes(RALLY_ACTION_NAME, device_id=DEVICE_ID, account_name="current", sequence_override=[rally_sequence[1]]):
            print("✅ 'Batalha' clicado. Estamos na lista.")
            time.sleep(1.5)
            return True
        else:
            print("❌ Falha ao clicar em 'Batalha'.")
    else:
        print("❌ Falha ao clicar em 'Aliança'.")
    
    return False

def processar_fila(fila_num, rally_sequence, scroll_config):
    """
    Processa uma única fila.
    """
    print(f"\n🎯 [Fila {fila_num}] Iniciando processamento...")
    
    # 1. SCROLL (se necessário) - USA CONFIGURAÇÕES DO JSON
    if fila_num >= 4:
        fila_key = str(fila_num)
        
        if fila_key in scroll_config:
            config = scroll_config[fila_key]
            num_scrolls = config.get("num_scrolls", fila_num - 3)
            row_height = config.get("row_height", 230)
            scroll_duration = config.get("scroll_duration", 1000)
            start_y = config.get("start_y", 800)
            center_x = config.get("center_x", 1200)
        else:
            # Fallback para valores padrão se não houver config
            print(f"⚠️ Configuração não encontrada para Fila {fila_num}. Usando padrão.")
            num_scrolls = fila_num - 3
            row_height = 230
            center_x = 1200
            start_y = 800
            scroll_duration = 1000
        
        end_y = start_y - row_height
        
        print(f"📜 Scroll Config para Fila {fila_num}:")
        print(f"   • Scrolls: {num_scrolls}x")
        print(f"   • Distância: {row_height}px (Y: {start_y} → {end_y})")
        print(f"   • Duração: {scroll_duration}ms")
        print(f"   • Posição X: {center_x}")
        
        try:
            for i in range(num_scrolls):
                simulate_scroll(DEVICE_ID, start_coords=[center_x, start_y], end_coords=[center_x, end_y], duration_ms=scroll_duration)
                time.sleep(0.8)
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ Erro no scroll: {e}")
            return 'ERROR'

    # 2. DETECTAR E CLICAR NA FILA
    offset_y = OFFSETS_FIXOS.get(fila_num, OFFSET_CLICK_APOS_SCROLL)
    template_path = get_template_path("03_fila.png")
    screenshot_path = os.path.join(project_root, "temp_screenshots", "temp_screenshot_rally.png")
    
    capture_screen(DEVICE_ID, screenshot_path)
    result = find_image_on_screen(screenshot_path, template_path)
    
    if result is None:
        print(f"⚠️ Fila {fila_num} (template 03_fila.png) não encontrada.")
        return 'REFRESH'
    
    x, y, w, h = result
    center_x = x + w // 2
    center_y = y + h // 2
    
    click_x = center_x
    click_y = center_y + offset_y
    
    print(f"📍 Template encontrado em ({x}, {y}) | Centro: ({center_x}, {center_y})")
    print(f"👆 Clicando na Fila {fila_num} -> Centro Y ({center_y}) + Offset ({offset_y}) = {click_y}")
    
    # Debug Visual
    try:
        import cv2
        debug_img = cv2.imread(screenshot_path)
        if debug_img is not None:
            cv2.rectangle(debug_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(debug_img, (click_x, click_y), 20, (0, 0, 255), -1)
            cv2.line(debug_img, (click_x, center_y), (click_x, click_y), (255, 0, 0), 2)
            cv2.putText(debug_img, f"Fila {fila_num} (+{offset_y})", (click_x + 30, click_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            debug_filename = os.path.join(project_root, "temp_screenshots", f"debug_click_fila_{fila_num}.png")
            cv2.imwrite(debug_filename, debug_img)
            print(f"🖼️ Debug salvo: {debug_filename}")
    except Exception as e:
        print(f"⚠️ Erro ao salvar debug visual: {e}")

    time.sleep(0.5)
    simulate_touch(click_x, click_y, device_id=DEVICE_ID)
    time.sleep(1.5)
    
    # 3. CLICAR EM JUNTAR
    print("🔘 Clicando em 'Juntar'...")
    if not execultar_acoes(RALLY_ACTION_NAME, device_id=DEVICE_ID, account_name="current", sequence_override=[rally_sequence[3]]):
        print("⚠️ Botão 'Juntar' não encontrado = NÃO HÁ RALLY DISPONÍVEL nesta posição.")
        print("🔙 Voltando para lista (1x BACK)...")
        execute_back(times=1)
        return 'NO_RALLY'
    
    # 4. CLICAR EM TROPAS
    print("💥 Clicando em 'Tropas'...")
    if not execultar_acoes(RALLY_ACTION_NAME, device_id=DEVICE_ID, account_name="current", sequence_override=[rally_sequence[4]]):
        print("⚠️ 'Tropas' não disponível = JÁ PARTICIPOU deste rally.")
        print("🔙 Voltando para lista (1x BACK)...")
        execute_back(times=1)
        return 'NEXT'
    
    # 5. CLICAR EM MARCHAR
    print("⚔️ Clicando em 'Marchar'...")
    if execultar_acoes(RALLY_ACTION_NAME, device_id=DEVICE_ID, account_name="current", sequence_override=[rally_sequence[5]]):
        print("✅ SUCESSO! Marcha enviada.")
        return 'MARCHED'
    else:
        print("❌ Falha ao clicar em Marchar (Erro Inesperado).")
        return 'ERROR'

# ---------------------------------------------------------------------------
# Tarefas Secundárias (com verificação de gatilho integrada)
# ---------------------------------------------------------------------------

def executar_com_gatilho(action_name, step_index, sequence):
    """
    Executa um passo de uma ação, mas ANTES verifica o gatilho.
    Retorna True se o gatilho foi detectado (interrompe), False caso contrário.
    """
    global FLAG_RALLY
    
    # Captura a tela para o passo atual
    screenshot_path = os.path.join(project_root, "temp_screenshots", "temp_screenshot_rally.png")
    capture_screen(DEVICE_ID, screenshot_path)
    
    # VERIFICA O GATILHO ANTES DE EXECUTAR O PASSO
    if verificar_gatilho(screenshot_path):
        FLAG_RALLY = True
        return True  # Gatilho detectado, interrompe
    
    # Se não detectou, executa o passo normalmente
    execultar_acoes(action_name, device_id=DEVICE_ID, account_name="current", sequence_override=[sequence[step_index]])
    return False  # Continua normalmente

def executar_tarefas_secundarias():
    """
    Executa tarefas na ordem: Baú → Recursos → Mobs (infinito).
    Interrompe imediatamente se o gatilho for detectado.
    """
    global FLAG_RALLY
    
    print("\n" + "="*80)
    print("🔄 MODO IDLE: Executando Tarefas Secundárias")
    print("="*80)
    
    # Hard Reset para garantir que estamos na tela principal
    print("🔙 Hard Reset (5x BACK) para Tela Principal...")
    execute_back(times=5)
    time.sleep(1.5)
    
    # 1. PREPARAÇÃO E PEGAR BAÚ
    # Clica no ícone global que leva para a área de baú/recursos (geralmente mapa ou base)
    clicar_preparacao(TEMPLATE_BAU_RECURSOS, "Ícone Prepara Baú/Recursos")
    
    print("\n📦 [TAREFA 1/3] Executando: pegar_bau...")
    print("\n📦 [TAREFA 1/3] Executando: pegar_bau...")
    bau_sequence = load_sequence("pegar_bau")
    if bau_sequence:
        for i in range(len(bau_sequence)):
            if executar_com_gatilho("pegar_bau", i, bau_sequence):
                print("🚨 Gatilho detectado durante pegar_bau! Abortando tarefas secundárias.")
                return
            time.sleep(0.5)
        print("✅ pegar_bau concluído.")
    else:
        print("⚠️ Sequência pegar_bau não encontrada. Pulando...")
    
    # Volta para tela principal após baú
    execute_back(times=3)
    time.sleep(1.0)
    
    # 2. PEGAR RECURSOS
    print("\n🌾 [TAREFA 2/3] Executando: pegar_recursos...")
    recursos_sequence = load_sequence("pegar_recursos")
    if recursos_sequence:
        for i in range(len(recursos_sequence)):
            if executar_com_gatilho("pegar_recursos", i, recursos_sequence):
                print("🚨 Gatilho detectado durante pegar_recursos! Abortando tarefas secundárias.")
                return
        print("✅ pegar_recursos concluído.")
    else:
        print("⚠️ Sequência pegar_recursos não encontrada. Pulando...")
    
    # Volta para tela principal após recursos
    execute_back(times=3)
    time.sleep(1.0)
    
    # 3. PREPARAÇÃO E MATAR MOBS (Loop Infinito)
    # Clica no ícone global que leva para o mapa/busca de mobs
    clicar_preparacao(TEMPLATE_MATAR_MOBS, "Ícone Prepara Mobs")

    print("\n⚔️ [TAREFA 3/3] Executando: matar_mobs (loop infinito)...")
    mobs_sequence = load_sequence("matar_mobs")
    if mobs_sequence:
        ciclo_mob = 0
        while not FLAG_RALLY:
            ciclo_mob += 1
            print(f"\n🗡️ Ciclo de Mob #{ciclo_mob}")
            
            for i in range(len(mobs_sequence)):
                if executar_com_gatilho("matar_mobs", i, mobs_sequence):
                    print("🚨 Gatilho detectado durante matar_mobs! Voltando para Rallies.")
                    return
                
                # Lógica injetada: Clique no centro após '01_buscar.png'
                # Isso garante que o menu feche ou o foco mude antes de tentar clicar em tropas
                step = mobs_sequence[i]
                
                # Tenta extrair o nome da imagem de diferentes formatos possíveis
                if isinstance(step, dict):
                    # Tenta vários campos possíveis
                    image_name = step.get("image", step.get("template_file", step.get("name", "")))
                else:
                    image_name = str(step)
                
                if "01_buscar" in image_name:  # Removido .png para ser mais flexível
                    click_x = 1200
                    click_y = 550
                    
                    # Debug Visual ANTES do clique (captura a tela atual)
                    print(f"ℹ️ [Injeção] Preparando clique no centro da tela ({click_x}, {click_y})...")
                    try:
                        import cv2
                        screenshot_path = os.path.join(project_root, "temp_screenshots", "temp_screenshot_rally.png")
                        capture_screen(DEVICE_ID, screenshot_path)  # Captura ANTES do clique
                        debug_img = cv2.imread(screenshot_path)
                        if debug_img is not None:
                            # Desenha um círculo vermelho grande no ponto de clique
                            cv2.circle(debug_img, (click_x, click_y), 30, (0, 0, 255), -1)
                            # Desenha uma cruz amarela para marcar o centro exato
                            cv2.line(debug_img, (click_x - 50, click_y), (click_x + 50, click_y), (0, 255, 255), 3)
                            cv2.line(debug_img, (click_x, click_y - 50), (click_x, click_y + 50), (0, 255, 255), 3)
                            # Adiciona texto descritivo
                            cv2.putText(debug_img, f"CLIQUE CENTRO ({click_x}, {click_y})", (click_x + 40, click_y - 10), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                            
                            debug_filename = os.path.join(project_root, "temp_screenshots", "debug_click_centro.png")
                            cv2.imwrite(debug_filename, debug_img)
                            print(f"🖼️ Debug do clique no centro salvo: {debug_filename}")
                    except Exception as e:
                        print(f"⚠️ Erro ao salvar debug visual do centro: {e}")
                    
                    # Aguarda animação e executa o clique
                    print("ℹ️ Aguardando a animação do mob terminar...")
                    time.sleep(5.0)
                    
                    print(f"👆 Clicando no centro da tela em: ({click_x}, {click_y})...")
                    simulate_touch(click_x, click_y, DEVICE_ID) 
                    time.sleep(0.5)

                time.sleep(0.5)
            
            # Pequeno delay entre ciclos de mob
            time.sleep(1.0)
    else:
        print("⚠️ Sequência matar_mobs não encontrada.")
        time.sleep(3)
        FLAG_RALLY = True  # Força retorno ao modo rally

# ---------------------------------------------------------------------------
# Loop Principal - SCROLL CEGO PROGRESSIVO
# ---------------------------------------------------------------------------
def main():
    global FLAG_RALLY
    
    print("🚀 Iniciando Bot de Rally Híbrido (24/7) - Scroll Cego Progressivo")
    print("📋 Modo: Rally (Prioridade) + Tarefas Secundárias (Idle)")
    
    rally_sequence = load_sequence(RALLY_ACTION_NAME)
    if not rally_sequence:
        print("❌ Erro: Sequência de rally não carregada.")
        return

    # Carrega configurações de scroll do JSON
    scroll_config = load_scroll_config()
    if scroll_config:
        print("✅ Configurações de scroll carregadas do scroll_config.json")
    else:
        print("⚠️ Usando configurações padrão de scroll")

    # RESET COMPLETO: Garante estado limpo (importante após reconexão USB)
    global FLAG_RALLY
    FLAG_RALLY = True  # Sempre inicia em modo rally
    primeiro_ciclo = True  # Sempre trata como primeiro ciclo
    
    while True:
        if FLAG_RALLY:
            # ========== MODO RALLY ATIVO ==========
            print("\n" + "="*80)
            print("🎯 MODO RALLY ATIVO - Scroll Cego Progressivo")
            print("="*80)
            
            rallies_joined = 0  # Contador de rallies que conseguimos entrar
            jah_na_lista = False  # Flag para indicar se já estamos na lista de rallys
            
            # Loop de Filas (1-9) - NUNCA PARA NO MEIO
            for fila in range(1, MAX_FILAS + 1):
                print(f"\n{'='*60}")
                print(f"🎯 Processando Fila {fila}/{MAX_FILAS}")
                print(f"{'='*60}")
                
                # NAVEGAÇÃO ANTES DE CADA FILA (Aliança → Batalha)
                # OTIMIZAÇÃO: Pula navegação se já estamos na lista (após falha no Passo 5)
                if not jah_na_lista:
                    if not navegar_para_lista_rallys(rally_sequence):
                        print("🔙 Falha na navegação. Resetando (5x BACK)...")
                        execute_back(times=5)
                        time.sleep(1.0)
                        jah_na_lista = False  # Reset flag
                        continue  # Pula para próxima fila
                else:
                    print("⚡ OTIMIZAÇÃO: Já estamos na lista, pulando navegação!")
                    jah_na_lista = False  # Reset flag para próxima iteração
                
                # PROCESSAR FILA
                status = processar_fila(fila, rally_sequence, scroll_config)
                
                # Tratamento de status
                if status == 'REFRESH':
                    if fila == 1 and primeiro_ciclo:
                        # Primeira fila do primeiro ciclo não encontrada = lista vazia
                        print("⚠️ Lista de rallies vazia (primeiro ciclo). Entrando em modo IDLE...")
                        FLAG_RALLY = False
                        break
                    else:
                        # Fila não encontrada, mas continua para próxima
                        print(f"⚠️ Fila {fila} não encontrada. Continuando para próxima...")
                        execute_back(times=2)  # Volta para garantir estado limpo
                        time.sleep(0.5)
                        jah_na_lista = False  # Reset flag
                        continue
                        
                elif status == 'MARCHED':
                    rallies_joined += 1
                    print(f"✅ Rally {rallies_joined} concluído! Continuando para próxima fila...")
                    # NÃO FAZ BREAK - Continua para próxima fila
                    time.sleep(1.0)
                    jah_na_lista = False  # Reset flag
                    continue
                    
                elif status == 'NO_RALLY':
                    # Filas sem rally = Fim da lista (não entra em IDLE!)
                    # Botão "Juntar" sempre aparece (mesmo desabilitado)
                    # IDLE só acontece quando template 03_fila.png não é encontrado (REFRESH)
                    print(f"🔄 Fim da lista de rallies (fila {fila} vazia). Encerrando ciclo...")
                    break
                        
                elif status == 'NEXT':
                    print(f"➡️ Fila {fila} já participada. Próxima fila...")
                    jah_na_lista = True  # MARCA que já estamos na lista!
                    continue
                    
                elif status == 'ERROR':
                    print(f"❌ Erro na fila {fila}. Resetando e continuando...")
                    execute_back(times=5)
                    time.sleep(1.0)
                    jah_na_lista = False  # Reset flag
                    continue
            
            # Fim do ciclo de 9 filas
            primeiro_ciclo = False  # Marca que primeiro ciclo foi concluído
            
            if not FLAG_RALLY:
                # Se FLAG_RALLY foi desativada (lista vazia no primeiro ciclo), sai do modo rally
                continue
            
            # Relatório do ciclo
            print("\n" + "="*80)
            print(f"📊 CICLO COMPLETO: {rallies_joined} rallies participados")
            print("🔄 Iniciando Loop de Segurança (varredura infinita)...")
            print("="*80)
            
            time.sleep(2.0)  # Pequena pausa entre ciclos
        
        else:
            # ========== MODO TAREFAS SECUNDÁRIAS ==========
            executar_tarefas_secundarias()
            # Quando retornar, FLAG_RALLY já estará True (gatilho ativou)
            
            # RESET: Marca como primeiro ciclo novamente após retornar do IDLE
            # Isso permite que o bot entre em IDLE novamente se a lista estiver vazia
            primeiro_ciclo = True
            print("🔄 Retornando ao modo rally. Resetando flag de primeiro ciclo...")

if __name__ == "__main__":
    while True:  # Loop infinito para recuperação de desconexão
        try:
            main()
        except KeyboardInterrupt:
            print("\n🛑 Interrompido pelo usuário.")
            break  # Sai do loop infinito
        except Exception as e:
            error_msg = str(e)
            
            # Detecta desconexão do dispositivo
            if "device" in error_msg.lower() and "not found" in error_msg.lower():
                print(f"\n⚠️ Erro de conexão detectado: {e}")
                
                # Aguarda reconexão
                aguardar_reconexao()
                
                # Reseta e reinicia
                print("🔄 Reiniciando bot do zero...")
                time.sleep(1.0)
                continue  # Volta ao início do loop (chama main() novamente)
            
            # Outros erros: mostra e para
            else:
                print(f"❌ Erro fatal: {e}")
                import traceback
                traceback.print_exc()
                break  # Sai do loop
