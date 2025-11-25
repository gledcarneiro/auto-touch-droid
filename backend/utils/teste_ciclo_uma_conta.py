"""
Nome do Arquivo: teste_ciclo_uma_conta.py
Descrição: Script de teste para validar o ciclo completo em apenas UMA conta
           antes de executar em todas as 10 contas.
           
Útil para:
    - Testar se as ações estão funcionando
    - Verificar se os delays estão adequados
    - Validar templates
    - Debug de problemas

Versão: 01.00.00 - Criação inicial
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
    print("✅ Lista de contas importada")
except ImportError:
    print("❌ ERRO: Não foi possível importar accounts_config.py")
    sys.exit(1)


# ============================================================================
# CONFIGURAÇÕES DE TESTE
# ============================================================================

# Device ID
try:
    from dotenv import load_dotenv
    load_dotenv()
    DEVICE_ID = os.getenv('DEFAULT_DEVICE_ID', 'RXCTB03EXVK')
except ImportError:
    DEVICE_ID = 'RXCTB03EXVK'

# Qual conta testar? (índice 0-9)
# 0 = login_gled, 1 = login_inf, 2 = login_cav, etc.
CONTA_TESTE_INDEX = 9  # ← MUDE AQUI PARA TESTAR OUTRA CONTA

# Nomes das ações
LOGIN_ACTION = "fazer_login"
LOGOUT_ACTION = "fazer_logout"
PEGAR_BAU_ACTION = "pegar_bau"
PEGAR_RECURSOS_ACTION = "pegar_recursos"

# Delays
DELAY_APOS_LOGIN = 3
DELAY_ENTRE_ACOES = 2
DELAY_APOS_LOGOUT = 5

# Pasta de ações
ACOES_FOLDER = os.path.join(backend_dir, "actions", "templates")


# ============================================================================
# FUNÇÕES
# ============================================================================

def print_separator(char="=", length=60):
    print(char * length)


def print_header(text):
    print_separator()
    print(f"  {text}")
    print_separator()


def load_sequence(action_name):
    """Carrega sequência de uma ação"""
    sequence_path = os.path.join(ACOES_FOLDER, action_name, "sequence.json")
    
    try:
        with open(sequence_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "sequence" in data:
            return data["sequence"]
        else:
            return None
    except Exception as e:
        print(f"❌ Erro ao carregar {action_name}: {e}")
        return None


def main():
    """Função principal de teste"""
    
    print_header("🧪 TESTE DE CICLO COMPLETO - UMA CONTA")
    
    # Verificar se índice é válido
    if CONTA_TESTE_INDEX < 0 or CONTA_TESTE_INDEX >= len(accounts):
        print(f"❌ ERRO: Índice {CONTA_TESTE_INDEX} inválido")
        print(f"Valores válidos: 0 a {len(accounts)-1}")
        return
    
    # Pegar conta de teste
    account = accounts[CONTA_TESTE_INDEX]
    account_name = account.get('name')
    
    print(f"📱 Device ID: {DEVICE_ID}")
    print(f"👤 Conta de teste: {account_name} (índice {CONTA_TESTE_INDEX})")
    print(f"⏰ Início: {datetime.now().strftime('%H:%M:%S')}")
    
    # Carregar sequências
    print("\n📂 Carregando sequências...")
    
    login_sequence = load_sequence(LOGIN_ACTION)
    if not login_sequence:
        print(f"❌ Falha ao carregar sequência de login")
        return
    print(f"✅ Login: {len(login_sequence)} passos")
    
    logout_sequence = load_sequence(LOGOUT_ACTION)
    if not logout_sequence:
        print(f"❌ Falha ao carregar sequência de logout")
        return
    print(f"✅ Logout: {len(logout_sequence)} passos")
    
    start_time = time.time()
    
    # ========================================================================
    # PASSO 1: LOGIN
    # ========================================================================
    print_header(f"1/4 - LOGIN: {account_name}")
    
    try:
        login_success = execute_login_for_account(
            account, 
            login_sequence, 
            device_id=DEVICE_ID
        )
        
        if not login_success:
            print(f"❌ FALHA no login")
            print("🛑 Teste interrompido")
            return
            
        print(f"✅ Login bem-sucedido")
        print(f"⏳ Aguardando {DELAY_APOS_LOGIN}s...")
        time.sleep(DELAY_APOS_LOGIN)
        
    except Exception as e:
        print(f"❌ ERRO durante login: {e}")
        return
    
    # ========================================================================
    # PASSO 2: PEGAR BAÚS
    # ========================================================================
    print_header(f"2/4 - PEGAR BAÚS: {account_name}")
    
    try:
        bau_success = execultar_acoes(
            PEGAR_BAU_ACTION,
            device_id=DEVICE_ID,
            account_name=account_name
        )
        
        if bau_success:
            print(f"✅ Baús coletados")
        else:
            print(f"⚠️ Falha ao coletar baús (continuando...)")
            
        print(f"⏳ Aguardando {DELAY_ENTRE_ACOES}s...")
        time.sleep(DELAY_ENTRE_ACOES)
        
    except Exception as e:
        print(f"❌ ERRO ao pegar baús: {e}")
        print("⚠️ Continuando para próxima ação...")
    
    # ========================================================================
    # PASSO 3: PEGAR RECURSOS
    # ========================================================================
    print_header(f"3/4 - PEGAR RECURSOS: {account_name}")
    
    try:
        recursos_success = execultar_acoes(
            PEGAR_RECURSOS_ACTION,
            device_id=DEVICE_ID,
            account_name=account_name
        )
        
        if recursos_success:
            print(f"✅ Recursos coletados")
        else:
            print(f"⚠️ Falha ao coletar recursos (continuando...)")
            
        print(f"⏳ Aguardando {DELAY_ENTRE_ACOES}s...")
        time.sleep(DELAY_ENTRE_ACOES)
        
    except Exception as e:
        print(f"❌ ERRO ao pegar recursos: {e}")
        print("⚠️ Continuando para logout...")
    
    # ========================================================================
    # PASSO 4: LOGOUT
    # ========================================================================
    print_header(f"4/4 - LOGOUT: {account_name}")
    
    try:
        logout_success = execultar_acoes(
            action_name=LOGOUT_ACTION,
            device_id=DEVICE_ID,
            sequence_override=logout_sequence,
            account_name=account_name
        )
        
        if logout_success:
            print(f"✅ Logout bem-sucedido")
        else:
            print(f"⚠️ Falha no logout")
            
        time.sleep(DELAY_APOS_LOGOUT)
        
    except Exception as e:
        print(f"❌ ERRO durante logout: {e}")
    
    # ========================================================================
    # RESUMO
    # ========================================================================
    total_time = time.time() - start_time
    
    print_header("📊 RESUMO DO TESTE")
    print(f"👤 Conta testada: {account_name}")
    print(f"⏱️ Tempo total: {total_time:.1f}s")
    print(f"⏰ Término: {datetime.now().strftime('%H:%M:%S')}")
    print()
    print("✅ TESTE CONCLUÍDO!")
    print()
    print("💡 Próximos passos:")
    print("   1. Se tudo funcionou, execute: ciclo_completo_todas_contas.py")
    print("   2. Se houve problemas, ajuste os templates ou delays")
    print("   3. Para testar outra conta, mude CONTA_TESTE_INDEX no código")
    print_separator()


if __name__ == '__main__':
    try:
        # Confirmação antes de executar
        print("\n🧪 MODO DE TESTE - UMA CONTA")
        print(f"Conta que será testada: {accounts[CONTA_TESTE_INDEX].get('name')}")
        print()
        
        resposta = input("Deseja continuar? (s/n): ").lower()
        
        if resposta == 's':
            print()
            main()
        else:
            print("❌ Teste cancelado pelo usuário")
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n👋 Programa finalizado")
