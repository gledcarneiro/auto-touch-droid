"""
Nome do Arquivo: ciclo_rally_intercalado.py
Descrição: Executa rallys intercalando as 3 contas por fila (otimizado para timing).
           
Fluxo otimizado:
    Para cada fila (1 a 9):
        1. Login Conta1 → Entrar na fila N → Logout
        2. Login Conta2 → Entrar na fila N → Logout
        3. Login Conta3 → Entrar na fila N → Logout
        4. Próxima fila
    
    Vantagem: Todas as contas entram na mesma fila quase simultaneamente,
              aproveitando melhor o tempo de 5min dos rallys.

Versão: 01.00.00 - Criação com lógica intercalada
Analista: Gemini Advanced
Programador: Gled Carneiro
-----------------------------------------------------------------------------
"""

import sys
import os
import time
import json
from datetime import datetime

# Adiciona os diretórios necessários ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(backend_dir)
sys.path.insert(0, project_root)
sys.path.insert(0, backend_dir)

# Importa funções necessárias
sys.path.append(os.path.join(backend_dir, 'core'))
sys.path.append(os.path.join(backend_dir, 'config'))

from action_executor import execultar_acoes, execute_login_for_account, simulate_scroll
from adb_utils import simulate_touch, capture_screen
from image_detection import find_image_on_screen

# Importa a lista de contas
try:
    from accounts_config import accounts
    print("✅ Lista de contas importada com sucesso")
except ImportError:
    print("❌ ERRO: Não foi possível importar a lista de contas de accounts_config.py")
    print("Certifique-se de que o arquivo existe em backend/config/accounts_config.py")
    sys.exit(1)


# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

# Device ID - será lido do .env se disponível, senão usa padrão
try:
    from dotenv import load_dotenv
    load_dotenv()
    DEVICE_ID = os.getenv('DEFAULT_DEVICE_ID', 'RXCTB03EXVK')
    print(f"✅ Device ID carregado do .env: {DEVICE_ID}")
except ImportError:
    DEVICE_ID = 'RXCTB03EXVK'
    print(f"⚠️ python-dotenv não instalado, usando device ID padrão: {DEVICE_ID}")

# Nomes das ações
LOGIN_ACTION = "fazer_login"
LOGOUT_ACTION = "fazer_logout"
RALLY_ACTION = "entrar_rallys"

# Configurações de Rally
MAX_FILAS = 9
OFFSETS_FIXOS = {
    1: 140,
    2: 360,
    3: 590
}
OFFSET_CLICK_APOS_SCROLL = 650

# Configurações de Login com Template Fixo
TEMPLATE_PREPARA_TELA_LOGIN = os.path.join(backend_dir, "actions", "templates", "_global", "prepara_tela_login.png")
LOGIN_OFFSETS_FIXOS = {
    1: 140,
    2: 360,
    3: 590
}
LOGIN_OFFSET_CLICK_APOS_SCROLL = 650

# Delays otimizados (reduzidos ao mínimo seguro)
DELAY_APOS_LOGIN = 2  # Reduzido de 3 para 2
DELAY_ENTRE_ACOES = 1  # Reduzido de 2 para 1
DELAY_APOS_LOGOUT = 2  # Reduzido de 5 para 2
DELAY_APOS_FALHA = 3  # Reduzido de 5 para 3
DELAY_ENTRE_CONTAS = 1  # Reduzido de 3 para 1

# Pasta de ações
ACOES_FOLDER = os.path.join(backend_dir, "actions", "templates")

# Contas a processar (apenas as 3 primeiras)
CONTAS_ATIVAS = [0, 1, 2]  # Índices das contas (conta1, conta2, conta3)


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def print_separator(char="=", length=80):
    """Imprime uma linha separadora"""
    print(char * length)


def print_header(text):
    """Imprime um cabeçalho formatado"""
    print_separator()
    print(f"  {text}")
    print_separator()


def load_sequence(action_name):
    """
    Carrega a sequência de uma ação do arquivo sequence.json
    
    Args:
        action_name: Nome da ação
        
    Returns:
        Sequência carregada ou None se houver erro
    """
    sequence_path = os.path.join(ACOES_FOLDER, action_name, "sequence.json")
    
    try:
        if not os.path.exists(sequence_path):
            print(f"⚠️ Arquivo não encontrado: {sequence_path}")
            return None
            
        with open(sequence_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Verificar estrutura (lista ou dicionário)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "sequence" in data:
            return data["sequence"]
        else:
            print(f"⚠️ Estrutura inválida em {sequence_path}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao carregar {sequence_path}: {e}")
        return None


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


def load_login_scroll_config():
    """Carrega configurações de scroll de login do JSON."""
    config_path = os.path.join(current_dir, "login_scroll_config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config.get("accounts", {})
    except Exception as e:
        print(f"⚠️ Erro ao carregar login_scroll_config.json: {e}")
        print("⚠️ Usando configurações padrão de login.")
        return {}


def get_template_path(filename):
    """Retorna o caminho completo para um template"""
    return os.path.join(project_root, "backend", "actions", "templates", RALLY_ACTION, filename)


def execute_back(times=1, delay=0.3):
    """Executa o comando BACK N vezes."""
    import subprocess
    for _ in range(times):
        try:
            subprocess.run(["adb", "-s", DEVICE_ID, "shell", "input", "keyevent", "4"], check=True)
            time.sleep(delay)
        except Exception as e:
            print(f"⚠️ Erro ao executar BACK: {e}")


def execute_login_with_fixed_template(account_index, account_name, login_sequence, login_scroll_config, device_id=DEVICE_ID):
    """
    Executa login usando template fixo e scroll cego (similar à estratégia de rally).
    
    Args:
        account_index: Índice da conta (0-based)
        account_name: Nome da conta para logging
        login_sequence: Sequência de login carregada
        login_scroll_config: Configuração de scroll de login
        device_id: ID do dispositivo
        
    Returns:
        bool: True se login bem-sucedido, False caso contrário
    """
    print(f"\n--- Fazendo login com template fixo: {account_name} (índice: {account_index}) ---")
    
    # 1. CLICAR NO ÍCONE DO GOOGLE (Passo 0)
    print("🔘 Clicando no ícone do Google...")
    if not execultar_acoes(LOGIN_ACTION, device_id=device_id, account_name="current", 
                          sequence_override=[login_sequence[0]], fila_atual="Login"):
        print("❌ Falha ao clicar no ícone do Google")
        return False
    
    time.sleep(2.0)  # Aguarda tela de login carregar
    
    # 2. SCROLL CEGO (se necessário para contas 4+)
    account_key = str(account_index + 1)  # Converte para 1-based
    
    if account_index >= 3:  # Contas 4+ (índice 3+)
        if account_key in login_scroll_config:
            config = login_scroll_config[account_key]
            num_scrolls = config.get("num_scrolls", 1)
            row_height = config.get("row_height", 230)
            scroll_duration = config.get("scroll_duration", 1000)
            start_y = config.get("start_y", 800)
            center_x = config.get("center_x", 1200)
        else:
            print(f"⚠️ Configuração não encontrada para Conta {account_index + 1}. Usando padrão.")
            num_scrolls = 1
            row_height = 230
            center_x = 1200
            start_y = 800
            scroll_duration = 1000
        
        end_y = start_y - row_height
        
        print(f"📜 Scroll Config para Conta {account_index + 1}:")
        print(f"   • Scrolls: {num_scrolls}x")
        print(f"   • Distância: {row_height}px (Y: {start_y} → {end_y})")
        print(f"   • Duração: {scroll_duration}ms")
        print(f"   • Posição X: {center_x}")
        
        try:
            for i in range(num_scrolls):
                simulate_scroll(device_id, start_coords=[center_x, start_y], 
                              end_coords=[center_x, end_y], duration_ms=scroll_duration)
                time.sleep(0.8)
            time.sleep(0.5)
        except Exception as e:
            print(f"❌ Erro no scroll: {e}")
            return False
    
    # 3. DETECTAR TEMPLATE FIXO E CLICAR
    offset_y = login_scroll_config.get(account_key, {}).get("offset_y", LOGIN_OFFSET_CLICK_APOS_SCROLL)
    screenshot_path = os.path.join(project_root, "temp_screenshots", "temp_screenshot_login.png")
    
    capture_screen(device_id, screenshot_path)
    result = find_image_on_screen(screenshot_path, TEMPLATE_PREPARA_TELA_LOGIN)
    
    if result is None:
        print(f"⚠️ Template fixo de login não encontrado.")
        return False
    
    x, y, w, h = result
    center_x = x + w // 2
    center_y = y + h // 2
    click_x = center_x
    click_y = center_y + offset_y
    
    print(f"📍 Template encontrado em ({x}, {y}) | Centro: ({center_x}, {center_y})")
    print(f"👆 Clicando na Conta {account_index + 1} → Centro Y ({center_y}) + Offset ({offset_y}) = {click_y}")
    
    # 4. GERAR IMAGEM DE DEBUG
    try:
        import cv2
        debug_img = cv2.imread(screenshot_path)
        if debug_img is not None:
            # Retângulo verde ao redor do template
            cv2.rectangle(debug_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Círculo vermelho no ponto de clique
            cv2.circle(debug_img, (click_x, click_y), 20, (0, 0, 255), -1)
            
            # Linha azul mostrando o offset
            cv2.line(debug_img, (click_x, center_y), (click_x, click_y), (255, 0, 0), 2)
            
            # Texto informativo
            cv2.putText(debug_img, f"Conta {account_index + 1} (+{offset_y})", 
                       (click_x + 30, click_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            # Salvar imagem
            debug_filename = os.path.join(project_root, "temp_screenshots", 
                                         f"debug_login_conta_{account_index + 1}.png")
            cv2.imwrite(debug_filename, debug_img)
            print(f"🖼️  Debug salvo: {debug_filename}")
    except Exception as e:
        print(f"⚠️ Erro ao salvar debug visual: {e}")
    
    # 5. CLICAR NA CONTA
    time.sleep(0.5)
    simulate_touch(click_x, click_y, device_id=device_id)
    time.sleep(2.0)  # Aguarda login completar
    
    print(f"✅ Login executado: {account_name}")
    return True


# ============================================================================
# FUNÇÕES DE NAVEGAÇÃO E PROCESSAMENTO DE RALLY
# ============================================================================

def navegar_para_lista_rallys(rally_sequence, fila_atual):
    """
    Garante que estamos na tela de lista de rallys.
    Fluxo: Aliança (01) -> Batalha (02).
    """
    if not execultar_acoes(RALLY_ACTION, device_id=DEVICE_ID, account_name="current", 
                       sequence_override=[rally_sequence[0]], fila_atual=fila_atual):
        return False
    time.sleep(0.6)  # Reduzido de 0.8
    
    if not execultar_acoes(RALLY_ACTION, device_id=DEVICE_ID, account_name="current", 
                      sequence_override=[rally_sequence[1]], fila_atual=fila_atual):
        return False
    time.sleep(1.2)  # Reduzido de 1.5
    return True


def processar_fila_unica(fila_num, rally_sequence, scroll_config, fila_atual):
    """
    Processa uma única fila para a conta atual.
    Retorna True se conseguiu entrar no rally, False caso contrário.
    """
    # 1. SCROLL (se necessário)
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
            num_scrolls = fila_num - 3
            row_height = 230
            center_x = 1200
            start_y = 800
            scroll_duration = 1000
        
        end_y = start_y - row_height
        
        try:
            for i in range(num_scrolls):
                simulate_scroll(DEVICE_ID, start_coords=[center_x, start_y], 
                              end_coords=[center_x, end_y], duration_ms=scroll_duration)
                time.sleep(0.6)  # Reduzido de 0.8
            time.sleep(0.4)  # Reduzido de 0.5
        except Exception as e:
            print(f"❌ Erro no scroll: {e}")
            return False

    # 2. DETECTAR E CLICAR NA FILA
    offset_y = OFFSETS_FIXOS.get(fila_num, OFFSET_CLICK_APOS_SCROLL)
    template_path = get_template_path("03_fila.png")
    screenshot_path = os.path.join(project_root, "temp_screenshots", "temp_screenshot_rally.png")
    
    capture_screen(DEVICE_ID, screenshot_path)
    result = find_image_on_screen(screenshot_path, template_path)
    
    if result is None:
        print(f"⚠️ Fila {fila_num} não encontrada.")
        return False
    
    x, y, w, h = result
    center_x = x + w // 2
    center_y = y + h // 2
    click_x = center_x
    click_y = center_y + offset_y
    
    time.sleep(0.4)  # Reduzido de 0.5
    simulate_touch(click_x, click_y, device_id=DEVICE_ID)
    time.sleep(1.2)  # Reduzido de 1.5
    
    # 3. CLICAR EM JUNTAR
    if not execultar_acoes(RALLY_ACTION, device_id=DEVICE_ID, account_name="current", 
                          sequence_override=[rally_sequence[3]], fila_atual=fila_atual):
        print("⚠️ Botão 'Juntar' não encontrado.")
        execute_back(times=1)
        return False
    
    # 4. CLICAR EM TROPAS
    if not execultar_acoes(RALLY_ACTION, device_id=DEVICE_ID, account_name="current", 
                          sequence_override=[rally_sequence[4]], fila_atual=fila_atual):
        print("⚠️ 'Tropas' não disponível.")
        execute_back(times=1)
        return False
    
    # 5. CLICAR EM MARCHAR
    if execultar_acoes(RALLY_ACTION, device_id=DEVICE_ID, account_name="current", 
                      sequence_override=[rally_sequence[5]], fila_atual=fila_atual):
        print("✅ Marcha enviada!")
        return True
    else:
        print("❌ Falha ao marchar.")
        return False


def processar_fila_para_conta(account, fila_num, login_sequence, logout_sequence, 
                               rally_sequence, scroll_config, login_scroll_config):
    """
    Processa uma fila específica para uma conta:
    Login → Entrar na fila → Logout
    
    Returns:
        True se conseguiu entrar no rally, False caso contrário
    """
    account_name = account.get('name')
    fila_atual = f"Fila {fila_num}"
    
    print(f"\n{'─'*60}")
    print(f"🎯 {account_name} → Fila {fila_num}")
    print(f"{'─'*60}")
    
    start_time = time.time()
    
    # 1. LOGIN COM TEMPLATE FIXO
    try:
        # Encontrar o índice da conta
        account_index = None
        for i, acc in enumerate(accounts):
            if acc.get('name') == account_name:
                account_index = i
                break
        
        if account_index is None:
            print(f"❌ Conta não encontrada: {account_name}")
            return False
        
        if not execute_login_with_fixed_template(account_index, account_name, login_sequence, 
                                                 login_scroll_config, device_id=DEVICE_ID):
            print(f"❌ Falha no login: {account_name}")
            return False
        print(f"✅ Login: {account_name}")
        time.sleep(DELAY_APOS_LOGIN)
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return False
    
    # 2. NAVEGAR E ENTRAR NA FILA
    success = False
    try:
        if navegar_para_lista_rallys(rally_sequence, fila_atual):
            success = processar_fila_unica(fila_num, rally_sequence, scroll_config, fila_atual)
        else:
            print("❌ Falha na navegação")
    except Exception as e:
        print(f"❌ Erro ao processar fila: {e}")
    
    # 3. LOGOUT
    try:
        execute_back(times=5, delay=0.2)  # Delay reduzido
        time.sleep(0.8)  # Reduzido de 1.0
        
        execultar_acoes(
            action_name=LOGOUT_ACTION,
            device_id=DEVICE_ID,
            sequence_override=logout_sequence,
            account_name=account_name
        )
        print(f"✅ Logout: {account_name}")
        time.sleep(DELAY_APOS_LOGOUT)
    except Exception as e:
        print(f"⚠️ Erro no logout: {e}")
    
    # Resumo
    duration = time.time() - start_time
    status = "✅ SUCESSO" if success else "❌ FALHOU"
    print(f"{status} | {account_name} | Fila {fila_num} | {duration:.1f}s")
    
    return success


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """Função principal com lógica intercalada"""
    
    print_header("🚀 CICLO DE RALLY INTERCALADO - 3 CONTAS")
    print(f"📱 Device ID: {DEVICE_ID}")
    print(f"👥 Contas: {len(CONTAS_ATIVAS)}")
    print(f"🔄 Filas: {MAX_FILAS}")
    print(f"⚡ Estratégia: Intercalar contas por fila (otimizado para timing)")
    print(f"⏰ Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar contas
    if not accounts or len(accounts) < 3:
        print("❌ ERRO: É necessário ter pelo menos 3 contas configuradas")
        return
    
    # ========================================================================
    # CARREGAR SEQUÊNCIAS
    # ========================================================================
    print("\n📂 Carregando sequências...")
    
    login_sequence = load_sequence(LOGIN_ACTION)
    if not login_sequence:
        print(f"❌ ERRO: Sequência de login não encontrada")
        return
    
    logout_sequence = load_sequence(LOGOUT_ACTION)
    if not logout_sequence:
        print(f"❌ ERRO: Sequência de logout não encontrada")
        return
    
    rally_sequence = load_sequence(RALLY_ACTION)
    if not rally_sequence:
        print(f"❌ ERRO: Sequência de rally não encontrada")
        return
    
    scroll_config = load_scroll_config()
    login_scroll_config = load_login_scroll_config()
    
    print("✅ Todas as sequências carregadas")
    if login_scroll_config:
        print("✅ Configurações de scroll de login carregadas")
    else:
        print("⚠️ Usando configurações padrão de scroll de login")
    
    # ========================================================================
    # LOOP INFINITO - INTERCALADO POR FILA
    # ========================================================================
    print_header("🔄 INICIANDO CICLO INTERCALADO")
    
    ciclo_numero = 0
    
    while True:
        ciclo_numero += 1
        print_header(f"🔁 CICLO #{ciclo_numero}")
        
        ciclo_start_time = time.time()
        stats = {
            'total_tentativas': 0,
            'total_sucessos': 0,
            'por_conta': {idx: {'tentativas': 0, 'sucessos': 0} for idx in CONTAS_ATIVAS}
        }
        
        # LOOP POR FILA (1 a 9)
        for fila_num in range(1, MAX_FILAS + 1):
            print(f"\n{'='*80}")
            print(f"📍 FILA {fila_num}/{MAX_FILAS} - Processando todas as contas")
            print(f"{'='*80}")
            
            fila_start_time = time.time()
            
            # Processar cada conta nesta fila
            for idx in CONTAS_ATIVAS:
                account = accounts[idx]
                
                try:
                    stats['total_tentativas'] += 1
                    stats['por_conta'][idx]['tentativas'] += 1
                    
                    success = processar_fila_para_conta(
                        account=account,
                        fila_num=fila_num,
                        login_sequence=login_sequence,
                        logout_sequence=logout_sequence,
                        rally_sequence=rally_sequence,
                        scroll_config=scroll_config,
                        login_scroll_config=login_scroll_config
                    )
                    
                    if success:
                        stats['total_sucessos'] += 1
                        stats['por_conta'][idx]['sucessos'] += 1
                    
                    # Delay mínimo entre contas
                    if idx != CONTAS_ATIVAS[-1]:
                        time.sleep(DELAY_ENTRE_CONTAS)
                        
                except KeyboardInterrupt:
                    print("\n\n⚠️ INTERROMPIDO PELO USUÁRIO")
                    return
                except Exception as e:
                    print(f"❌ ERRO CRÍTICO: {e}")
                    time.sleep(DELAY_APOS_FALHA)
            
            # Resumo da fila
            fila_duration = time.time() - fila_start_time
            print(f"\n⏱️ Fila {fila_num} concluída em {fila_duration:.1f}s ({fila_duration/60:.1f} min)")
        
        # ====================================================================
        # RESUMO DO CICLO
        # ====================================================================
        ciclo_duration = time.time() - ciclo_start_time
        
        print_header(f"📊 RESUMO DO CICLO #{ciclo_numero}")
        print(f"✅ Rallys bem-sucedidos: {stats['total_sucessos']}/{stats['total_tentativas']}")
        print(f"\nPor conta:")
        for idx in CONTAS_ATIVAS:
            account_name = accounts[idx].get('name')
            sucessos = stats['por_conta'][idx]['sucessos']
            tentativas = stats['por_conta'][idx]['tentativas']
            print(f"  • {account_name}: {sucessos}/{tentativas} rallys")
        
        print(f"\n⏱️ Tempo total do ciclo: {ciclo_duration:.1f}s ({ciclo_duration/60:.1f} min)")
        print(f"⏰ Término: {datetime.now().strftime('%H:%M:%S')}")
        print(f"\n🔄 Reiniciando ciclo...")
        print_separator()
        
        time.sleep(2)  # Pequena pausa antes de reiniciar


# ============================================================================
# EXECUÇÃO
# ============================================================================

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Programa interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n👋 Programa finalizado")
