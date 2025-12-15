"""
Nome do Arquivo: ciclo_rally_tres_contas.py
Descrição: Executa ciclo contínuo de rally para 3 contas específicas.
           
Fluxo para cada conta:
    1. Login na conta
    2. Executar 9 iterações de entrar_rallys (com scroll cego)
    3. Logout
    4. Repetir para próxima conta
    5. Após conta3, retornar para conta1 (ciclo infinito)

Versão: 01.00.00 - Criação inicial do utilitário automatizado
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
MAX_ITERACOES_RALLY = 9
MAX_FILAS = 9
OFFSETS_FIXOS = {
    1: 140,
    2: 360,
    3: 590
}
OFFSET_CLICK_APOS_SCROLL = 650

# Delays entre ações (em segundos)
DELAY_APOS_LOGIN = 3
DELAY_ENTRE_ACOES = 2
DELAY_APOS_LOGOUT = 5
DELAY_APOS_FALHA = 5
DELAY_ENTRE_CONTAS = 3

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


def print_step(step_number, total_steps, description):
    """Imprime informação de um passo"""
    print(f"\n[{step_number}/{total_steps}] {description}")


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


# ============================================================================
# FUNÇÕES DE NAVEGAÇÃO E PROCESSAMENTO DE RALLY
# ============================================================================

def navegar_para_lista_rallys(rally_sequence, fila_atual):
    """
    Garante que estamos na tela de lista de rallys.
    Fluxo: Aliança (01) -> Batalha (02).
    """
    print("\n🧭 Navegando para a Lista de Rallys...")
    
    print("1️⃣  Clicando em 'Aliança' (01_alianca.png)...")
    if execultar_acoes(RALLY_ACTION, device_id=DEVICE_ID, account_name="current", 
                       sequence_override=[rally_sequence[0]], fila_atual=fila_atual):
        print("✅ 'Aliança' clicado.")
        time.sleep(0.8)
        
        if execultar_acoes(RALLY_ACTION, device_id=DEVICE_ID, account_name="current", 
                          sequence_override=[rally_sequence[1]], fila_atual=fila_atual):
            time.sleep(1.5)
            return True
        else:
            print("❌ Falha ao clicar em 'Batalha'.")
    else:
        print("❌ Falha ao clicar em 'Aliança'.")
    
    return False


def processar_fila(fila_num, rally_sequence, scroll_config, fila_atual):
    """
    Processa uma única fila com scroll cego progressivo.
    Implementa a mesma lógica de entrar_todos_rallys.py
    """
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
            # Fallback para valores padrão
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
    
    time.sleep(0.5)
    simulate_touch(click_x, click_y, device_id=DEVICE_ID)
    time.sleep(1.5)
    
    # 3. CLICAR EM JUNTAR
    print("🔘 Clicando em 'Juntar'...")
    if not execultar_acoes(RALLY_ACTION, device_id=DEVICE_ID, account_name="current", 
                          sequence_override=[rally_sequence[3]], fila_atual=fila_atual):
        print("⚠️ Botão 'Juntar' não encontrado.")
        print("🔙 Voltando para lista (1x BACK)...")
        execute_back(times=1)
        return 'NO_RALLY'
    
    # 4. CLICAR EM TROPAS
    print("💥 Clicando em 'Tropas'...")
    if not execultar_acoes(RALLY_ACTION, device_id=DEVICE_ID, account_name="current", 
                          sequence_override=[rally_sequence[4]], fila_atual=fila_atual):
        print("⚠️ 'Tropas' não disponível = JÁ PARTICIPOU deste rally.")
        print("🔙 Voltando para lista (1x BACK)...")
        execute_back(times=1)
        return 'NEXT'
    
    # 5. CLICAR EM MARCHAR
    print("⚔️ Clicando em 'Marchar'...")
    if execultar_acoes(RALLY_ACTION, device_id=DEVICE_ID, account_name="current", 
                      sequence_override=[rally_sequence[5]], fila_atual=fila_atual):
        print("✅ SUCESSO! Marcha enviada.")
        return 'MARCHED'
    else:
        print("❌ Falha ao clicar em Marchar.")
        return 'ERROR'


def executar_rally_completo(rally_sequence, scroll_config, account_name):
    """
    Executa o ciclo completo de rally (9 iterações) para uma conta.
    Implementa a mesma lógica de scroll cego de entrar_todos_rallys.py
    """
    print_header(f"🎯 EXECUTANDO RALLYS - {account_name}")
    
    rallies_joined = 0
    jah_na_lista = False
    
    # Loop de Filas (1-9)
    for fila in range(1, MAX_FILAS + 1):
        fila_atual = f"⚔️  Fila {fila}/{MAX_FILAS}"
        print(f"\n{'='*60}")
        print(f"🎯 Processando {fila_atual}")
        print(f"{'='*60}")
        
        # NAVEGAÇÃO ANTES DE CADA FILA
        if not jah_na_lista:
            if not navegar_para_lista_rallys(rally_sequence, fila_atual=fila_atual):
                print("🔙 Falha na navegação. Resetando (5x BACK)...")
                execute_back(times=5)
                time.sleep(1.0)
                jah_na_lista = False
                continue
        else:
            print("⚡ OTIMIZAÇÃO: Já estamos na lista, pulando navegação!")
            jah_na_lista = False
        
        # PROCESSAR FILA
        status = processar_fila(fila, rally_sequence, scroll_config, fila_atual)
        
        # Tratamento de status
        if status == 'REFRESH':
            print(f"⚠️ Fila {fila} não encontrada. Continuando para próxima...")
            execute_back(times=2)
            time.sleep(0.5)
            jah_na_lista = False
            continue
                
        elif status == 'MARCHED':
            rallies_joined += 1
            print(f"✅ Rally {rallies_joined} concluído! Continuando para próxima fila...")
            time.sleep(1.0)
            jah_na_lista = False
            continue
            
        elif status == 'NO_RALLY':
            print(f"🔄 Fim da lista de rallies (fila {fila} vazia).")
            execute_back(times=5)
            break
                
        elif status == 'NEXT':
            print(f"➡️ Fila {fila} já participada. Próxima fila...")
            jah_na_lista = True
            continue
            
        elif status == 'ERROR':
            print(f"❌ Erro na fila {fila}. Resetando e continuando...")
            execute_back(times=5)
            time.sleep(1.0)
            jah_na_lista = False
            continue
    
    print(f"\n📊 Total de rallies participados: {rallies_joined}")
    return rallies_joined


# ============================================================================
# FUNÇÃO DE CICLO POR CONTA
# ============================================================================

def execute_account_cycle(account, account_number, total_accounts, 
                          login_sequence, logout_sequence, rally_sequence, scroll_config):
    """
    Executa o ciclo completo para uma conta:
    Login -> 9x Rally -> Logout
    
    Args:
        account: Dicionário com informações da conta
        account_number: Número da conta atual (1-indexed)
        total_accounts: Total de contas
        login_sequence: Sequência de login carregada
        logout_sequence: Sequência de logout carregada
        rally_sequence: Sequência de rally carregada
        scroll_config: Configurações de scroll
        
    Returns:
        True se o ciclo foi completado com sucesso, False caso contrário
    """
    account_name = account.get('name')
    
    print_header(f"CONTA {account_number}/{total_accounts}: {account_name}")
    print(f"⏰ Início: {datetime.now().strftime('%H:%M:%S')}")
    
    cycle_start_time = time.time()
    
    # ========================================================================
    # PASSO 1: LOGIN
    # ========================================================================
    print_step(1, 3, f"LOGIN - {account_name}")
    
    try:
        login_success = execute_login_for_account(
            account, 
            login_sequence, 
            device_id=DEVICE_ID
        )
        
        if not login_success:
            print(f"❌ FALHA no login para {account_name}")
            print(f"⏭️ Pulando para próxima conta...")
            time.sleep(DELAY_APOS_FALHA)
            return False
            
        print(f"✅ Login bem-sucedido: {account_name}")
        time.sleep(DELAY_APOS_LOGIN)
        
    except Exception as e:
        print(f"❌ ERRO durante login de {account_name}: {e}")
        time.sleep(DELAY_APOS_FALHA)
        return False
    
    # ========================================================================
    # PASSO 2: EXECUTAR RALLYS (9 ITERAÇÕES)
    # ========================================================================
    print_step(2, 3, f"EXECUTAR RALLYS - {account_name}")
    
    try:
        rallies_count = executar_rally_completo(rally_sequence, scroll_config, account_name)
        print(f"✅ Rallys executados: {rallies_count}")
        time.sleep(DELAY_ENTRE_ACOES)
        
    except Exception as e:
        print(f"❌ ERRO ao executar rallys de {account_name}: {e}")
        # Continua mesmo com erro para fazer logout
    
    # ========================================================================
    # PASSO 3: LOGOUT
    # ========================================================================
    print_step(3, 3, f"LOGOUT - {account_name}")
    
    try:
        # Reset para tela principal antes do logout
        execute_back(times=5)
        time.sleep(1.0)
        
        logout_success = execultar_acoes(
            action_name=LOGOUT_ACTION,
            device_id=DEVICE_ID,
            sequence_override=logout_sequence,
            account_name=account_name
        )
        
        if logout_success:
            print(f"✅ Logout bem-sucedido: {account_name}")
        else:
            print(f"⚠️ Falha no logout: {account_name}")
            
        time.sleep(DELAY_APOS_LOGOUT)
        
    except Exception as e:
        print(f"❌ ERRO durante logout de {account_name}: {e}")
        time.sleep(DELAY_APOS_LOGOUT)
    
    # ========================================================================
    # RESUMO DO CICLO
    # ========================================================================
    cycle_duration = time.time() - cycle_start_time
    print(f"\n⏱️ Tempo total para {account_name}: {cycle_duration:.1f}s")
    print(f"⏰ Término: {datetime.now().strftime('%H:%M:%S')}")
    
    return True


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """Função principal que executa o ciclo infinito para as 3 contas"""
    
    print_header("🚀 CICLO DE RALLY - 3 CONTAS (LOOP INFINITO)")
    print(f"📱 Device ID: {DEVICE_ID}")
    print(f"👥 Contas ativas: {len(CONTAS_ATIVAS)}")
    print(f"🔄 Iterações de rally por conta: {MAX_ITERACOES_RALLY}")
    print(f"⏰ Início da execução: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar se há contas
    if not accounts or len(accounts) < 3:
        print("❌ ERRO: É necessário ter pelo menos 3 contas configuradas em accounts_config.py")
        return
    
    # ========================================================================
    # CARREGAR SEQUÊNCIAS
    # ========================================================================
    print("\n📂 Carregando sequências de ações...")
    
    login_sequence = load_sequence(LOGIN_ACTION)
    if login_sequence is None:
        print(f"❌ ERRO: Não foi possível carregar sequência de {LOGIN_ACTION}")
        return
    print(f"✅ Sequência de login carregada ({len(login_sequence)} passos)")
    
    logout_sequence = load_sequence(LOGOUT_ACTION)
    if logout_sequence is None:
        print(f"❌ ERRO: Não foi possível carregar sequência de {LOGOUT_ACTION}")
        return
    print(f"✅ Sequência de logout carregada ({len(logout_sequence)} passos)")
    
    rally_sequence = load_sequence(RALLY_ACTION)
    if rally_sequence is None:
        print(f"❌ ERRO: Não foi possível carregar sequência de {RALLY_ACTION}")
        return
    print(f"✅ Sequência de rally carregada ({len(rally_sequence)} passos)")
    
    # Carregar configurações de scroll
    scroll_config = load_scroll_config()
    if scroll_config:
        print("✅ Configurações de scroll carregadas do scroll_config.json")
    else:
        print("⚠️ Usando configurações padrão de scroll")
    
    # ========================================================================
    # LOOP INFINITO - CICLO ENTRE AS 3 CONTAS
    # ========================================================================
    print_header("🔄 INICIANDO CICLO INFINITO")
    
    ciclo_numero = 0
    
    while True:
        ciclo_numero += 1
        print_header(f"🔁 CICLO #{ciclo_numero}")
        
        ciclo_start_time = time.time()
        successful_accounts = 0
        failed_accounts = 0
        
        # Processar apenas as 3 primeiras contas
        for idx in CONTAS_ATIVAS:
            account = accounts[idx]
            account_number = idx + 1
            
            try:
                success = execute_account_cycle(
                    account=account,
                    account_number=account_number,
                    total_accounts=len(CONTAS_ATIVAS),
                    login_sequence=login_sequence,
                    logout_sequence=logout_sequence,
                    rally_sequence=rally_sequence,
                    scroll_config=scroll_config
                )
                
                if success:
                    successful_accounts += 1
                else:
                    failed_accounts += 1
                    
                # Delay entre contas
                if idx != CONTAS_ATIVAS[-1]:  # Não espera após última conta
                    print(f"\n⏳ Aguardando {DELAY_ENTRE_CONTAS}s antes da próxima conta...")
                    time.sleep(DELAY_ENTRE_CONTAS)
                    
            except KeyboardInterrupt:
                print("\n\n⚠️ EXECUÇÃO INTERROMPIDA PELO USUÁRIO")
                print(f"Ciclos completados: {ciclo_numero - 1}")
                return
                
            except Exception as e:
                print(f"\n❌ ERRO CRÍTICO ao processar conta {account.get('name')}: {e}")
                failed_accounts += 1
                time.sleep(DELAY_APOS_FALHA)
        
        # ====================================================================
        # RESUMO DO CICLO
        # ====================================================================
        ciclo_duration = time.time() - ciclo_start_time
        
        print_header(f"📊 RESUMO DO CICLO #{ciclo_numero}")
        print(f"✅ Contas processadas com sucesso: {successful_accounts}")
        print(f"❌ Contas com falha: {failed_accounts}")
        print(f"⏱️ Tempo do ciclo: {ciclo_duration:.1f}s ({ciclo_duration/60:.1f} min)")
        print(f"⏰ Término do ciclo: {datetime.now().strftime('%H:%M:%S')}")
        
        if successful_accounts == len(CONTAS_ATIVAS):
            print(f"\n🎉 CICLO #{ciclo_numero} COMPLETO! Reiniciando para conta1...")
        else:
            print(f"\n⚠️ CICLO #{ciclo_numero} PARCIAL: {successful_accounts}/{len(CONTAS_ATIVAS)} contas processadas")
        
        print_separator()
        
        # Pequeno delay antes de reiniciar o ciclo
        print(f"\n⏳ Aguardando {DELAY_ENTRE_CONTAS}s antes de reiniciar ciclo...")
        time.sleep(DELAY_ENTRE_CONTAS)


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
