# Nome do Arquivo: entrar_todos_rallys.py
# Descrição: Automatiza a entrada em todos os Monster Rallys usando os templates criados em backend/actions/templates/entrar_rallys.
# Versão: 01.00.00
# Analista: Antigravity
# Programador: Gled Carneiro
# -----------------------------------------------------------------------------

"""
Este script percorre todas as contas configuradas em `backend/config/accounts_config.py`
 e executa a sequência de ação `entrar_rallys` que foi criada com o assistente de
 templates. Cada sequência já deve conter um passo de scroll (action_before_find)
 antes de clicar no template `03_fila.png` que representa a fila do rally.

Requisitos:
- A pasta `backend/actions/templates/entrar_rallys` deve conter `sequence.json`.
- O dispositivo Android deve estar conectado via ADB.
- O ID do dispositivo pode ser definido em `.env` (variável `DEFAULT_DEVICE_ID`).
"""

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
# Garantir que o caminho raiz esteja no sys.path para importações absolutas
if project_root not in sys.path:
    sys.path.append(project_root)

# Importar utilidades do core
sys.path.append(os.path.join(backend_dir, "core"))
from action_executor import execultar_acoes

# Account handling removed – script will run for the currently logged‑in account only
# No import of accounts_config is needed

# ---------------------------------------------------------------------------
# Configurações gerais
# ---------------------------------------------------------------------------
# Device ID – tenta ler do .env, senão usa fallback
try:
    from dotenv import load_dotenv
    load_dotenv()
    DEVICE_ID = os.getenv("DEFAULT_DEVICE_ID", "RXCTB03EXVK")
    print(f"✅ Device ID carregado do .env: {DEVICE_ID}")
except Exception:
    DEVICE_ID = "RXCTB03EXVK"
    print(f"⚠️ .env não encontrado ou dotenv não instalado – usando fallback: {DEVICE_ID}")

# Nome da ação de rally (pasta dentro de backend/actions/templates)
RALLY_ACTION_NAME = "entrar_rallys"

# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------
def print_separator(char="=", length=80):
    print(char * length)

def print_header(text):
    print_separator()
    print(f"  {text}")
    print_separator()

def print_step(step_number, total_steps, description):
    print(f"\n[{step_number}/{total_steps}] {description}")

def load_sequence(action_name):
    """Carrega a sequência JSON para a ação especificada."""
    sequence_path = os.path.join(project_root, "backend", "actions", "templates", action_name, "sequence.json")
    if not os.path.exists(sequence_path):
        print(f"⚠️ Arquivo sequence.json não encontrado: {sequence_path}")
        return None
    try:
        with open(sequence_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # O formato pode ser lista ou dict com chave "sequence"
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "sequence" in data:
            return data["sequence"]
        print(f"⚠️ Estrutura inesperada em {sequence_path}")
        return None
    except Exception as e:
        print(f"❌ Erro ao ler {sequence_path}: {e}")
        return None

# ---------------------------------------------------------------------------
# Função principal que executa o rally para cada conta
# ---------------------------------------------------------------------------
def main():
    """Loop infinito entrando nos rallys, fechando a tela e usando scroll inteligente."""
    print_header("🚀 Entrar no Monster Rally (loop infinito)")
    print(f"📱 Device ID: {DEVICE_ID}")
    # Carregar a sequência de rally
    rally_sequence = load_sequence(RALLY_ACTION_NAME)
    if rally_sequence is None:
        print("❌ Não foi possível carregar a sequência de rally. Abortando.")
        return
    print(f"✅ Sequência de rally carregada ({len(rally_sequence)} passos)\\n")

    row_counter = 0  # controla quantas filas já foram processadas
    successful = 0
    failed = 0
    start_time_total = time.time()

    try:
        while True:
            # Se já processamos 3 filas visíveis, precisamos fazer scroll antes da próxima
            if row_counter % 3 == 0 and row_counter != 0:
                print("🔄 Realizando scroll para revelar novas filas...")
                try:
                    from action_executor import simulate_scroll
                    simulate_scroll(device_id=DEVICE_ID, direction="up", duration_ms=800)
                except Exception as e:
                    print(f"❌ Erro ao executar scroll: {e}")
                time.sleep(1)

            print_step(1, 1, f"Tentando entrar na fila {row_counter + 1}")
            
            # Criar sequências parciais
            # Parte 1: Aliança → Batalha → Fila → Juntar
            sequence_part1 = rally_sequence[0:4]  # passos 1-4
            # Parte 2: Tropas → Marchar  
            sequence_part2 = rally_sequence[4:6]  # passos 5-6
            
            # Executar parte 1
            success_part1 = execultar_acoes(
                action_name=RALLY_ACTION_NAME,
                device_id=DEVICE_ID,
                account_name="current",
                sequence_override=sequence_part1,
            )
            
            if success_part1:
                print("✅ Parte 1 OK - Juntar encontrado, continuando...")
                # Executar parte 2
                success_part2 = execultar_acoes(
                    action_name=RALLY_ACTION_NAME,
                    device_id=DEVICE_ID,
                    account_name="current",
                    sequence_override=sequence_part2,
                )
                if success_part2:
                    print("✅ Rally completo - Tropas e Marchar executados!")
                    successful += 1
                else:
                    print("⚠️ Falha em Tropas/Marchar")
                    failed += 1
            else:
                print("⚠️ Parte 1 falhou - provavelmente 04_juntar não encontrado (já na fila).")
                # Fechar a tela
                try:
                    subprocess.run(["adb", "-s", DEVICE_ID, "shell", "input", "keyevent", "4"], check=True)
                    print("🔙 Tela fechada (back).")
                    time.sleep(1)
                except Exception as e:
                    print(f"❌ Erro ao fechar tela: {e}")
                
                # Clicar 300px abaixo para próxima fila
                try:
                    from adb_utils import simulate_touch
                    # Pegar coordenadas da última tentativa de 03_fila (aproximadamente centro da tela)
                    # Como não temos acesso direto, vamos usar coordenadas estimadas
                    # Baseado no log: Template '03_fila.png' encontrado em (120, 41)
                    # Vamos clicar 300px abaixo dessa região
                    click_x = 1200  # centro horizontal estimado
                    click_y = 500   # posição vertical estimada + 300px
                    simulate_touch(device_id=DEVICE_ID, x=click_x, y=click_y)
                    print(f"👆 Clicou 300px abaixo em ({click_x}, {click_y}) - próxima fila")
                    time.sleep(2)
                except Exception as e:
                    print(f"❌ Erro ao clicar na próxima fila: {e}")
                
                # Parte 2 alternativa: Juntar → Tropas → Marchar (passos 4, 5, 6)
                print("🔄 Executando Parte 2 alternativa (Juntar → Tropas → Marchar)...")
                sequence_part2_alt = rally_sequence[3:6]  # passos 4-6
                success_part2_alt = execultar_acoes(
                    action_name=RALLY_ACTION_NAME,
                    device_id=DEVICE_ID,
                    account_name="current",
                    sequence_override=sequence_part2_alt,
                )
                if success_part2_alt:
                    print("✅ Parte 2 alternativa OK - Rally completo na nova fila!")
                    successful += 1
                else:
                    print("⚠️ Parte 2 alternativa falhou")
                    failed += 1

            row_counter += 1
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n⚠️ Loop interrompido pelo usuário")
    finally:
        total_duration = time.time() - start_time_total
        print_separator()
        print("📊 RESUMO FINAL (loop)")
        print(f"✅ Sucessos: {successful}")
        print(f"❌ Falhas: {failed}")
        print(f"⏱️ Tempo total executado: {total_duration:.1f}s ({total_duration/60:.1f} min)")
        print(f"⏰ Término: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print_separator()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Programa interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n👋 Programa finalizado")
