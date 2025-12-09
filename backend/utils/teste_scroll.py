# Nome do Arquivo: teste_scroll.py
# Descrição: Script de Calibração Manual de Scroll para Rally Bot
# Versão: 01.00.00
# Analista: Antigravity
# Programador: Gled Carneiro
# -----------------------------------------------------------------------------

import sys
import os
import time
import json
import subprocess

# ---------------------------------------------------------------------------
# Configuração de caminho e importação de módulos do projeto
# ---------------------------------------------------------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(backend_dir)
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
CONFIG_PATH = os.path.join(current_dir, "scroll_config.json")
OFFSETS_FIXOS = {
    1: 140,
    2: 360,
    3: 590
}
OFFSET_CLICK_APOS_SCROLL = 650

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

def load_scroll_config():
    """Carrega configurações de scroll do JSON."""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config.get("filas", {})
    except Exception as e:
        print(f"❌ Erro ao carregar scroll_config.json: {e}")
        return {}

def save_scroll_config(filas_config):
    """Salva configurações de scroll no JSON."""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        config["filas"] = filas_config
        
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print("✅ Configurações salvas com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar scroll_config.json: {e}")
        return False

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

def navegar_para_lista_rallys(rally_sequence):
    """Navega para a lista de rallys (Aliança -> Batalha)."""
    print("\n🧭 Navegando para a Lista de Rallys...")
    
    # print("1️⃣ Clicando em 'Aliança' (01_alianca.png)...")
    if execultar_acoes(RALLY_ACTION_NAME, device_id=DEVICE_ID, account_name="current", sequence_override=[rally_sequence[0]]):
        # print("✅ 'Aliança' clicado.")
        time.sleep(0.8)
        
        # print("2️⃣ Clicando em 'Batalha' (02_batalha.png)...")
        if execultar_acoes(RALLY_ACTION_NAME, device_id=DEVICE_ID, account_name="current", sequence_override=[rally_sequence[1]]):
            # print("✅ 'Batalha' clicado. Estamos na lista.")
            time.sleep(1.5)
            return True
        else:
            print("❌ Falha ao clicar em 'Batalha'.")
    else:
        print("❌ Falha ao clicar em 'Aliança'.")
    
    return False

def executar_scroll_fila(fila_num, scroll_config):
    """Executa o scroll para uma fila específica usando configurações do JSON."""
    fila_key = str(fila_num)
    
    if fila_key not in scroll_config:
        print(f"⚠️ Fila {fila_num} não encontrada no scroll_config.json")
        return False
    
    config = scroll_config[fila_key]
    num_scrolls = config.get("num_scrolls", 0)
    
    if num_scrolls == 0:
        print(f"ℹ️ Fila {fila_num} não requer scroll.")
        return True
    
    # Extrai parâmetros
    row_height = config.get("row_height", 230)
    scroll_duration = config.get("scroll_duration", 1000)
    start_y = config.get("start_y", 800)
    center_x = config.get("center_x", 1200)
    end_y = start_y - row_height
    
    print(f"\n📜 Executando Scroll para Fila {fila_num}:")
    print(f"   • Scrolls: {num_scrolls}x")
    print(f"   • Distância: {row_height}px (Y: {start_y} → {end_y})")
    print(f"   • Duração: {scroll_duration}ms")
    print(f"   • Posição X: {center_x}")
    
    try:
        for i in range(num_scrolls):
            print(f"   🔄 Scroll {i+1}/{num_scrolls}...")
            simulate_scroll(DEVICE_ID, start_coords=[center_x, start_y], end_coords=[center_x, end_y], duration_ms=scroll_duration)
            time.sleep(0.8)
        
        time.sleep(0.5)
        print(f"✅ Scroll concluído para Fila {fila_num}")
        return True
        
    except Exception as e:
        print(f"❌ Erro no scroll: {e}")
        return False

def marcar_posicao_fila(fila_num):
    """Captura screenshot e marca visualmente onde a fila deveria estar."""
    offset_y = OFFSETS_FIXOS.get(fila_num, OFFSET_CLICK_APOS_SCROLL)
    template_path = get_template_path("03_fila.png")
    screenshot_path = os.path.join(project_root, "temp_screenshots", f"calibracao_fila_{fila_num}.png")
    
    capture_screen(DEVICE_ID, screenshot_path)
    result = find_image_on_screen(screenshot_path, template_path)
    
    if result is None:
        print(f"⚠️ Template 03_fila.png não encontrado na tela.")
        return False
    
    x, y, w, h = result
    center_x = x + w // 2
    center_y = y + h // 2
    click_y = center_y + offset_y
    
    # Debug Visual
    try:
        import cv2
        debug_img = cv2.imread(screenshot_path)
        if debug_img is not None:
            # Retângulo verde no template detectado
            cv2.rectangle(debug_img, (x, y), (x + w, y + h), (0, 255, 0), 3)
            
            # Círculo vermelho no ponto de clique
            cv2.circle(debug_img, (center_x, click_y), 25, (0, 0, 255), -1)
            
            # Linha azul mostrando o offset
            cv2.line(debug_img, (center_x, center_y), (center_x, click_y), (255, 0, 0), 3)
            
            # Linha horizontal amarela na posição ideal (offset)
            cv2.line(debug_img, (0, click_y), (debug_img.shape[1], click_y), (0, 255, 255), 2)
            
            # Textos informativos
            cv2.putText(debug_img, f"FILA {fila_num}", (center_x + 40, click_y - 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
            cv2.putText(debug_img, f"Offset: +{offset_y}px", (center_x + 40, click_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
            cv2.putText(debug_img, f"Click Y: {click_y}", (center_x + 40, click_y + 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
            
            cv2.imwrite(screenshot_path, debug_img)
            print(f"🖼️ Screenshot de calibração salva: {screenshot_path}")
            print(f"📍 Template em: ({x}, {y}) | Centro: ({center_x}, {center_y})")
            print(f"👆 Ponto de clique: ({center_x}, {click_y}) [Offset: +{offset_y}px]")
            return True
    except Exception as e:
        print(f"⚠️ Erro ao salvar debug visual: {e}")
        return False

# ---------------------------------------------------------------------------
# Menu Interativo
# ---------------------------------------------------------------------------
def menu_principal():
    """Menu principal do script de teste."""
    print("\n" + "="*80)
    print("🎯 TESTE DE SCROLL - CALIBRAÇÃO MANUAL")
    print("="*80)
    print("\nOpções:")
    print("  [1-9] - Testar scroll para fila específica")
    print("  [A]   - Testar todas as filas (4-9) em sequência")
    print("  [E]   - Editar configuração de uma fila")
    print("  [V]   - Visualizar configurações atuais")
    print("  [R]   - Reset (voltar para tela inicial)")
    print("  [S]   - Sair")
    print("="*80)
    
    escolha = input("\n👉 Escolha uma opção: ").strip().upper()
    return escolha

def testar_fila_individual(fila_num, rally_sequence, scroll_config):
    """Testa o scroll de uma fila específica."""
    print(f"\n{'='*80}")
    print(f"🧪 TESTANDO FILA {fila_num}")
    print(f"{'='*80}")
    
    # Navega para lista
    if not navegar_para_lista_rallys(rally_sequence):
        print("❌ Falha na navegação. Tente novamente.")
        return
    
    # Executa scroll
    if executar_scroll_fila(fila_num, scroll_config):
        time.sleep(1.0)
        
        # Marca posição
        print(f"\n📸 Capturando posição da Fila {fila_num}...")
        marcar_posicao_fila(fila_num)
        
        print(f"\n✅ Teste da Fila {fila_num} concluído!")
        print("💡 Verifique o screenshot em temp_screenshots/ para validar o posicionamento.")
        print("   • Se a fila estiver ACIMA da linha amarela → DIMINUA row_height")
        print("   • Se a fila estiver ABAIXO da linha amarela → AUMENTE row_height")
    
    # Volta para tela inicial
    print("\n🔙 Voltando para tela inicial...")
    execute_back(times=5)
    time.sleep(1.0)

def testar_todas_filas(rally_sequence, scroll_config):
    """Testa todas as filas de 4 a 9 em sequência."""
    print(f"\n{'='*80}")
    print("🧪 TESTANDO TODAS AS FILAS (4-9)")
    print(f"{'='*80}")
    
    for fila in range(4, 10):
        input(f"\n⏸️ Pressione ENTER para testar Fila {fila}...")
        testar_fila_individual(fila, rally_sequence, scroll_config)
        time.sleep(2.0)
    
    print("\n✅ Teste de todas as filas concluído!")

def editar_configuracao_fila(scroll_config):
    """Menu para editar configuração de uma fila."""
    fila_num = input("\n👉 Qual fila deseja editar (4-9)? ").strip()
    
    if fila_num not in scroll_config:
        print(f"❌ Fila {fila_num} não encontrada.")
        return scroll_config
    
    config = scroll_config[fila_num]
    
    print(f"\n📋 Configuração atual da Fila {fila_num}:")
    print(f"   • num_scrolls: {config.get('num_scrolls', 0)}")
    print(f"   • row_height: {config.get('row_height', 230)}")
    print(f"   • scroll_duration: {config.get('scroll_duration', 1000)}")
    print(f"   • start_y: {config.get('start_y', 800)}")
    print(f"   • center_x: {config.get('center_x', 1200)}")
    
    print("\n🔧 O que deseja editar?")
    print("  [1] num_scrolls")
    print("  [2] row_height (distância do scroll)")
    print("  [3] scroll_duration (velocidade)")
    print("  [4] start_y")
    print("  [5] center_x")
    print("  [C] Cancelar")
    
    opcao = input("\n👉 Escolha: ").strip().upper()
    
    if opcao == "C":
        return scroll_config
    
    campo_map = {
        "1": "num_scrolls",
        "2": "row_height",
        "3": "scroll_duration",
        "4": "start_y",
        "5": "center_x"
    }
    
    if opcao not in campo_map:
        print("❌ Opção inválida.")
        return scroll_config
    
    campo = campo_map[opcao]
    valor_atual = config.get(campo, 0)
    
    try:
        novo_valor = int(input(f"\n👉 Novo valor para {campo} (atual: {valor_atual}): ").strip())
        config[campo] = novo_valor
        
        if save_scroll_config(scroll_config):
            print(f"✅ {campo} da Fila {fila_num} atualizado para {novo_valor}")
        
    except ValueError:
        print("❌ Valor inválido. Deve ser um número inteiro.")
    
    return scroll_config

def visualizar_configuracoes(scroll_config):
    """Exibe todas as configurações de scroll."""
    print(f"\n{'='*80}")
    print("📋 CONFIGURAÇÕES DE SCROLL ATUAIS")
    print(f"{'='*80}")
    
    for fila in range(4, 10):
        fila_key = str(fila)
        if fila_key in scroll_config:
            config = scroll_config[fila_key]
            print(f"\n🎯 Fila {fila}:")
            print(f"   • Scrolls: {config.get('num_scrolls', 0)}x")
            print(f"   • Distância: {config.get('row_height', 230)}px")
            print(f"   • Duração: {config.get('scroll_duration', 1000)}ms")
            print(f"   • Start Y: {config.get('start_y', 800)}")
            print(f"   • Center X: {config.get('center_x', 1200)}")
    
    print(f"\n{'='*80}")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("🚀 Iniciando Script de Calibração de Scroll")
    
    # Carrega sequência de rally
    rally_sequence = load_sequence(RALLY_ACTION_NAME)
    if not rally_sequence:
        print("❌ Erro: Sequência de rally não carregada.")
        return
    
    # Carrega configurações de scroll
    scroll_config = load_scroll_config()
    if not scroll_config:
        print("❌ Erro: Configurações de scroll não carregadas.")
        return
    
    while True:
        escolha = menu_principal()
        
        if escolha == "S":
            print("\n👋 Encerrando script de calibração. Até logo!")
            break
        
        elif escolha in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            fila_num = int(escolha)
            if fila_num < 4:
                print(f"⚠️ Fila {fila_num} não requer scroll (visível sem scroll).")
            else:
                testar_fila_individual(fila_num, rally_sequence, scroll_config)
        
        elif escolha == "A":
            testar_todas_filas(rally_sequence, scroll_config)
        
        elif escolha == "E":
            scroll_config = editar_configuracao_fila(scroll_config)
        
        elif escolha == "V":
            visualizar_configuracoes(scroll_config)
        
        elif escolha == "R":
            print("\n🔙 Executando reset (5x BACK)...")
            execute_back(times=5)
            time.sleep(1.0)
            print("✅ Reset concluído!")
        
        else:
            print("❌ Opção inválida. Tente novamente.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Interrompido pelo usuário.")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
