"""
Nome do Arquivo: ciclo_completo_todas_contas.py
Descrição: Executa o ciclo completo (Login → Pegar Baú → Pegar Recursos → Logout) 
           para todas as contas configuradas automaticamente.
           
Fluxo para cada conta:
    1. Login na conta
    2. Pegar baús
    3. Pegar recursos
    4. Logout
    5. Repetir para próxima conta

Versão: 01.00.00 - Criação inicial do utilitário automatizado
Analista: Claude (Gemini Advanced)
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

from action_executor import execultar_acoes, execute_login_for_account

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
PEGAR_BAU_ACTION = "pegar_bau"
PEGAR_RECURSOS_ACTION = "pegar_recursos"

# Delays entre ações (em segundos)
DELAY_APOS_LOGIN = 3
DELAY_ENTRE_ACOES = 2
DELAY_APOS_LOGOUT = 5
DELAY_APOS_FALHA = 5

# Pasta de ações
ACOES_FOLDER = os.path.join(backend_dir, "actions", "templates")


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


def execute_account_cycle(account, account_number, total_accounts, 
                          login_sequence, logout_sequence):
    """
    Executa o ciclo completo para uma conta
    
    Args:
        account: Dicionário com informações da conta
        account_number: Número da conta atual (1-indexed)
        total_accounts: Total de contas
        login_sequence: Sequência de login carregada
        logout_sequence: Sequência de logout carregada
        
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
    print_step(1, 4, f"LOGIN - {account_name}")
    
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
    # PASSO 2: PEGAR BAÚS
    # ========================================================================
    print_step(2, 4, f"PEGAR BAÚS - {account_name}")
    
    try:
        bau_success = execultar_acoes(
            PEGAR_BAU_ACTION,
            device_id=DEVICE_ID,
            account_name=account_name
        )
        
        if bau_success:
            print(f"✅ Baús coletados: {account_name}")
        else:
            print(f"⚠️ Falha ao coletar baús: {account_name}")
            
        time.sleep(DELAY_ENTRE_ACOES)
        
    except Exception as e:
        print(f"❌ ERRO ao pegar baús de {account_name}: {e}")
        # Continua mesmo com erro
    
    # ========================================================================
    # PASSO 3: PEGAR RECURSOS
    # ========================================================================
    print_step(3, 4, f"PEGAR RECURSOS - {account_name}")
    
    try:
        recursos_success = execultar_acoes(
            PEGAR_RECURSOS_ACTION,
            device_id=DEVICE_ID,
            account_name=account_name
        )
        
        if recursos_success:
            print(f"✅ Recursos coletados: {account_name}")
        else:
            print(f"⚠️ Falha ao coletar recursos: {account_name}")
            
        time.sleep(DELAY_ENTRE_ACOES)
        
    except Exception as e:
        print(f"❌ ERRO ao pegar recursos de {account_name}: {e}")
        # Continua mesmo com erro
    
    # ========================================================================
    # PASSO 4: LOGOUT
    # ========================================================================
    print_step(4, 4, f"LOGOUT - {account_name}")
    
    try:
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
    """Função principal que executa o ciclo completo para todas as contas"""
    
    print_header("🚀 CICLO COMPLETO - TODAS AS CONTAS")
    print(f"📱 Device ID: {DEVICE_ID}")
    print(f"👥 Total de contas: {len(accounts)}")
    print(f"⏰ Início da execução: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar se há contas
    if not accounts:
        print("❌ ERRO: Nenhuma conta configurada em accounts_config.py")
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
    
    # Verificar se ações de baú e recursos existem
    bau_path = os.path.join(ACOES_FOLDER, PEGAR_BAU_ACTION)
    recursos_path = os.path.join(ACOES_FOLDER, PEGAR_RECURSOS_ACTION)
    
    if not os.path.exists(bau_path):
        print(f"⚠️ AVISO: Ação '{PEGAR_BAU_ACTION}' não encontrada em {bau_path}")
    else:
        print(f"✅ Ação '{PEGAR_BAU_ACTION}' encontrada")
        
    if not os.path.exists(recursos_path):
        print(f"⚠️ AVISO: Ação '{PEGAR_RECURSOS_ACTION}' não encontrada em {recursos_path}")
    else:
        print(f"✅ Ação '{PEGAR_RECURSOS_ACTION}' encontrada")
    
    # ========================================================================
    # EXECUTAR CICLO PARA CADA CONTA
    # ========================================================================
    print_header("🔄 INICIANDO EXECUÇÃO DO CICLO")
    
    start_time = time.time()
    successful_accounts = 0
    failed_accounts = 0
    
    for index, account in enumerate(accounts, start=1):
        try:
            success = execute_account_cycle(
                account=account,
                account_number=index,
                total_accounts=len(accounts),
                login_sequence=login_sequence,
                logout_sequence=logout_sequence
            )
            
            if success:
                successful_accounts += 1
            else:
                failed_accounts += 1
                
        except KeyboardInterrupt:
            print("\n\n⚠️ EXECUÇÃO INTERROMPIDA PELO USUÁRIO")
            print(f"Contas processadas: {index - 1}/{len(accounts)}")
            break
            
        except Exception as e:
            print(f"\n❌ ERRO CRÍTICO ao processar conta {account.get('name')}: {e}")
            failed_accounts += 1
            time.sleep(DELAY_APOS_FALHA)
    
    # ========================================================================
    # RESUMO FINAL
    # ========================================================================
    total_duration = time.time() - start_time
    
    print_header("📊 RESUMO FINAL")
    print(f"✅ Contas processadas com sucesso: {successful_accounts}")
    print(f"❌ Contas com falha: {failed_accounts}")
    print(f"📊 Total de contas: {len(accounts)}")
    print(f"⏱️ Tempo total de execução: {total_duration:.1f}s ({total_duration/60:.1f} min)")
    print(f"⏰ Término: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if successful_accounts == len(accounts):
        print("\n🎉 TODAS AS CONTAS FORAM PROCESSADAS COM SUCESSO!")
    elif successful_accounts > 0:
        print(f"\n⚠️ EXECUÇÃO PARCIAL: {successful_accounts}/{len(accounts)} contas processadas")
    else:
        print("\n❌ NENHUMA CONTA FOI PROCESSADA COM SUCESSO")
    
    print_separator()


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
