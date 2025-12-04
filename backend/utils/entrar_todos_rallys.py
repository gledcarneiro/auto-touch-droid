# Nome do Arquivo: entrar_todos_rallys.py
# Descrição: Bot de Rally com Tarefas Secundárias (Baú, Recursos, Mobs) - Versão 4.0
# Versão: 04.00.00 (Arquitetura Híbrida com Gatilho)
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
    3: 590,
}
OFFSET_CLICK_APOS_SCROLL = 590

# FLAG GLOBAL: Controla se o bot está em modo Rally ou Tarefas Secundárias
FLAG_RALLY = True

# Template globais
GATILHO_TEMPLATE      = os.path.join(project_root, "backend", "actions", "templates", "_global", "prepara_voltar_rally.png")
TEMPLATE_MATAR_MOBS   = os.path.join(project_root, "backend", "actions", "templates", "_global", "prepara_matar_mobs_novo_rally.png")
TEMPLATE_BAU_RECURSOS = os.path.join(project_root, "backend", "actions", "templates", "_global", "prepara_pegar_bau_recursos.png")

# ---------------------------------------------------------------------------
# Funções Auxiliares
# ---------------------------------------------------------------------------
def execute_back(times=1, delay=0.3):
    """Executa o comando BACK N vezes."""
    for _ in range(times):
        try:
            subprocess.run(["adb", "-s", DEVICE_ID, "shell", "input", "keyevent", "4"], check=True)
            time.sleep(delay)
        except Exception as e:
            print(f"⚠️ Erro ao executar BACK: {e}")

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

def processar_fila(fila_num, rally_sequence):
    """
    Processa uma única fila.
    """
    print(f"\n🎯 [Fila {fila_num}] Iniciando processamento...")
    
    # 1. SCROLL (se necessário)
    if fila_num >= 4:
        num_scrolls = fila_num - 3
        row_height = 230
        center_x = 1200
        start_y = 800
        end_y = start_y - row_height
        scroll_duration = 1000
        
        print(f"📜 Scroll: {num_scrolls}x ({row_height}px) para revelar Fila {fila_num}")
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
        print("⚠️ 'Juntar' não disponível (Falha Esperada - Já participou ou cheio).")
        print("🔙 Voltando para lista (1x BACK)...")
        execute_back(times=1)
        return 'NEXT'
    
    # 4. CLICAR EM TROPAS
    print("💥 Clicando em 'Tropas'...")
    if not execultar_acoes(RALLY_ACTION_NAME, device_id=DEVICE_ID, account_name="current", sequence_override=[rally_sequence[4]]):
        print("⚠️ 'Tropas' não disponível (Falha Esperada).")
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
    
    # 1. PEGAR BAÚ
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
            time.sleep(0.5)
        print("✅ pegar_recursos concluído.")
    else:
        print("⚠️ Sequência pegar_recursos não encontrada. Pulando...")
    
    # Volta para tela principal após recursos
    execute_back(times=3)
    time.sleep(1.0)
    
    # 3. MATAR MOBS (Loop Infinito)
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
                time.sleep(0.5)
            
            # Pequeno delay entre ciclos de mob
            time.sleep(1.0)
    else:
        print("⚠️ Sequência matar_mobs não encontrada.")
        print("⏳ Aguardando 30 segundos antes de verificar rallies novamente...")
        time.sleep(30)
        FLAG_RALLY = True  # Força retorno ao modo rally

# ---------------------------------------------------------------------------
# Loop Principal
# ---------------------------------------------------------------------------
def main():
    global FLAG_RALLY
    
    print("🚀 Iniciando Bot de Rally Híbrido (24/7)")
    print("📋 Modo: Rally (Prioridade) + Tarefas Secundárias (Idle)")
    
    rally_sequence = load_sequence(RALLY_ACTION_NAME)
    if not rally_sequence:
        print("❌ Erro: Sequência de rally não carregada.")
        return

    while True:
        if FLAG_RALLY:
            # ========== MODO RALLY ATIVO ==========
            print("\n" + "="*80)
            print("🎯 MODO RALLY ATIVO")
            print("="*80)
            
            if not navegar_para_lista_rallys(rally_sequence):
                print("🔙 Falha na navegação. Resetando (5x BACK)...")
                execute_back(times=5)
                continue
            
            # Loop de Filas
            reset_needed = False
            rallies_joined = 0  # Contador de rallies que conseguimos entrar
            for fila in range(1, MAX_FILAS + 1):
                status = processar_fila(fila, rally_sequence)
                
                if status == 'REFRESH':
                    if fila == 1:
                        # Não achou nem a primeira fila = lista vazia
                        print("⚠️ Lista de rallies vazia. Entrando em modo IDLE...")
                        FLAG_RALLY = False
                        break
                    else:
                        # Acabaram as filas, mas processou algumas
                        print("🔄 Fim da lista de rallies. Atualizando...")
                        break
                        
                elif status == 'MARCHED':
                    rallies_joined += 1  # Incrementa o contador
                    print("🎉 Rally concluído! Reiniciando ciclo...")
                    reset_needed = True 
                    break
                    
                elif status == 'NEXT':
                    print("➡️ Indo para próxima fila...")
                    continue
                    
                elif status == 'ERROR':
                    print("❌ Erro crítico. Resetando...")
                    execute_back(times=5)
                    reset_needed = True
                    break
            
            # Se processou todas as filas mas não conseguiu entrar em nenhuma, ativa modo IDLE
            if rallies_joined == 0 and not reset_needed and FLAG_RALLY:
                print("⚠️ Nenhum rally disponível para entrar (todos já participados). Entrando em modo IDLE...")
                FLAG_RALLY = False
                
            if reset_needed:
                time.sleep(1)
                continue
                
            # Soft Reset (atualizar lista)
            if FLAG_RALLY:  # Só faz soft reset se ainda estiver em modo rally
                print("🔄 Reiniciando ciclo de navegação (Soft Reset)...")
                execute_back(times=1) 
                time.sleep(1.0)
        
        else:
            # ========== MODO TAREFAS SECUNDÁRIAS ==========
            executar_tarefas_secundarias()
            # Quando retornar, FLAG_RALLY já estará True (gatilho ativou)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Interrompido pelo usuário.")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()