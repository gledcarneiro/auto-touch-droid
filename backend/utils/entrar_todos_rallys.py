# Nome do Arquivo: entrar_todos_rallys.py
# Descrição: Automatiza a entrada em todos os Monster Rallys usando os templates criados em backend/actions/templates/entrar_rallys.
# Versão: 02.00.00
# Analista: Antigravity
# Programador: Gled Carneiro
# -----------------------------------------------------------------------------

"""
Este script percorre até 9 filas de rally em loop infinito 24/7.
Cada ciclo executa PARTES 1 e 2 (Aliança → Batalha) antes de processar cada fila.

Fluxo por fila:
- PARTE 1: Tela0 → Clicar Aliança (01_alianca.png) → Tela1
- PARTE 2: Tela1 → Clicar Batalha (02_batalha.png) → Tela1-Aba
- PARTE 3: Tela1-Aba → Detectar/Clicar Fila (03_fila.png + offset) → Tela2
- PARTE 4: Tela2 → Clicar Juntar (04_juntar.png) → Tela3
- PARTE 5: Tela3 → Clicar Tropas (05_tropas.png)
- PARTE 6: Tela3 → Clicar Marchar (06_marchar.png) → Tela0

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

def execute_back(device_id, times=1, delay=0.3):
    """Executa o comando BACK N vezes."""
    for _ in range(times):
        try:
            subprocess.run(["adb", "-s", device_id, "shell", "input", "keyevent", "4"], check=True)
            time.sleep(delay)
        except Exception as e:
            print(f"⚠️ Erro ao executar BACK: {e}")

# ---------------------------------------------------------------------------
# Função principal que executa o rally para cada conta
# ---------------------------------------------------------------------------
def main():
    """Loop infinito 24/7 entrando nos rallys usando template fixo + offsets incrementais."""
    print_header("🚀 Entrar no Monster Rally (loop infinito 24/7)")
    print(f"📱 Device ID: {DEVICE_ID}")
    
    # Carregar a sequência de rally
    rally_sequence = load_sequence(RALLY_ACTION_NAME)
    if rally_sequence is None:
        print("❌ Não foi possível carregar a sequência de rally. Abortando.")
        return
    print(f"✅ Sequência de rally carregada ({len(rally_sequence)} passos)\n")

    # Constantes
    MAX_FILAS = 9
    OFFSETS_FIXOS = {
        1: 140,   # Fila 1 (primeira visível)
        2: 360,   # Fila 2 (segunda visível)
        3: 590,   # Fila 3 (terceira visível)
    }
    OFFSET_CLICK_APOS_SCROLL = 590  # Sempre clicar na posição da fila 3 após scroll
    
    successful_total = 0
    failed_total = 0
    ciclos_completos = 0
    start_time_total = time.time()

    try:
        # Importar funções necessárias
        from adb_utils import simulate_touch, capture_screen
        from action_executor import simulate_scroll
        from image_detection import find_image_on_screen
        
        # LOOP INFINITO 24/7
        while True:
            ciclos_completos += 1
            print_separator("=", 80)
            print(f"🔄 INICIANDO CICLO {ciclos_completos}")
            print_separator("=", 80)
            
            successful = 0
            failed = 0
            
            # ================================================================
            # PARTE 1 e 2: NAVEGAÇÃO INICIAL (executar apenas 1x por ciclo)
            # Tela0 → Tela1 (Aliança → Batalha)
            # ================================================================
            print_separator("=", 80)
            print("🏰 INICIANDO NAVEGAÇÃO: Aliança → Batalha")
            print_separator("=", 80)
            
            # PARTE 1: Clicar em Aliança
            print(f"🏰 [PARTE 1] Clicando em 'Aliança' (01_alianca.png)")
            sequence_alianca = [rally_sequence[0]]  # passo 1 (Aliança)
            
            success_alianca = execultar_acoes(
                action_name=RALLY_ACTION_NAME,
                device_id=DEVICE_ID,
                account_name="current",
                sequence_override=sequence_alianca,
            )
            
            if not success_alianca:
                print("❌ Falha ao clicar em Aliança")
                print("🔙 Voltando à Tela0 (5x BACK)...")
                execute_back(DEVICE_ID, times=5)
                time.sleep(0.5)
                continue  # Reinicia o ciclo (while True)
            
            print("✅ 'Aliança' clicado - Tela1 aberta")
            time.sleep(0.5)
            
            # PARTE 2: Clicar em Batalha
            print(f"⚔️ [PARTE 2] Clicando em 'Batalha' (02_batalha.png)")
            sequence_batalha = [rally_sequence[1]]  # passo 2 (Batalha)
            
            success_batalha = execultar_acoes(
                action_name=RALLY_ACTION_NAME,
                device_id=DEVICE_ID,
                account_name="current",
                sequence_override=sequence_batalha,
            )
            
            if not success_batalha:
                print("❌ Falha ao clicar em Batalha")
                print("🔙 Voltando à Tela0 (1x BACK)...")
                execute_back(DEVICE_ID, times=1)
                time.sleep(0.5)
                continue  # Reinicia o ciclo (while True)
            
            print("✅ 'Batalha' clicado - Tela1-Aba (Filas) aberta\n")
            time.sleep(0.5)
            
            # ================================================================
            # LOOP DE FILAS (processar até 9 filas)
            # ================================================================
            for fila_num in range(1, MAX_FILAS + 1):
                print_separator("-", 80)
                print(f"🎯 PROCESSANDO FILA {fila_num}/{MAX_FILAS}")
                print_separator("-", 80)
                
                # ============================================================
                # PARTE 3: DETECTAR TEMPLATE E CLICAR NA FILA
                # Tela1-Aba (Filas) → Tela2
                # ============================================================
                print(f"🔍 [PARTE 3] Detectando e clicando na fila {fila_num}")
                
                # SCROLL (se necessário para filas 4+)
                if fila_num >= 4:
                    # LÓGICA DECREMENTAL: Quanto mais distante a fila, MENOR a duração (mais rápido = mais força)
                    # Fila 4: 600ms (lento) - scroll leve
                    # Fila 5: 500ms (médio)
                    # Fila 6: 400ms (rápido)
                    # Fila 7: 300ms (mais rápido)
                    # Fila 8: 200ms (muito rápido)
                    # Fila 9: 100ms (super rápido)
                    
                    base_duration = 1900  # Duração máxima para fila 4
                    decrement = 100  # Decremento por fila
                    num_filas_apos_3 = fila_num - 3  # Fila 4=1, Fila 5=2, etc.
                    scroll_duration = 2600 #base_duration - (decrement * num_filas_apos_3)
                    
                    # Garantir mínimo de 100ms
                    # scroll_duration = max(scroll_duration, 100)
                    
                    print(f"📜 Fazendo scroll UP (duração: {scroll_duration}ms) para revelar fila {fila_num}")
                    try:
                        simulate_scroll(device_id=DEVICE_ID, direction="up", duration_ms=scroll_duration)
                        time.sleep(0.5)  # Aguardar estabilização da tela
                        print(f"✅ Scroll executado - Fila {fila_num} deve estar na posição da Fila 3")
                    except Exception as e:
                        print(f"❌ Erro ao executar scroll: {e}")
                        print("🔙 Voltando à Tela0 (5x BACK) e reiniciando ciclo...")
                        execute_back(DEVICE_ID, times=5)
                        time.sleep(0.5)
                        break  # Sai do loop de filas e reinicia ciclo
                
                # Determinar offset Y baseado na fila
                if fila_num in OFFSETS_FIXOS:
                    offset_y = OFFSETS_FIXOS[fila_num]
                    print(f"📍 Fila {fila_num}: Offset fixo de {offset_y}px")
                else:
                    offset_y = OFFSET_CLICK_APOS_SCROLL
                    print(f"📍 Fila {fila_num}: Offset pós-scroll de {offset_y}px (posição da Fila 3)")
                
                # Detectar template 03_fila.png (posição fixa)
                template_path = os.path.join(project_root, "backend", "actions", "templates", "entrar_rallys", "03_fila.png")
                screenshot_path = "temp_screenshot_rally.png"
                
                try:
                    # Capturar tela
                    capture_screen(device_id=DEVICE_ID, output_path=screenshot_path)
                    
                    # Encontrar template (retorna (x, y, w, h) ou None)
                    result = find_image_on_screen(screenshot_path, template_path)
                    
                    if result is None:
                        print(f"⚠️ Template 03_fila.png não encontrado - sem mais filas disponíveis")
                        print("🔙 Voltando à Tela0 (5x BACK) e finalizando ciclo...")
                        execute_back(DEVICE_ID, times=5)
                        time.sleep(0.5)
                        break  # Sai do loop de filas e reinicia ciclo
                    
                    # Extrair coordenadas (x, y, w, h)
                    x, y, w, h = result
                    center_x = x + w // 2
                    center_y = y + h // 2
                    
                    # Calcular posição de clique com offset
                    click_x = center_x
                    click_y = center_y + offset_y
                    
                    print(f"✅ Template encontrado em ({x}, {y}), centro: ({center_x}, {center_y})")
                    print(f"👆 Clicando com offset +{offset_y}px → ({click_x}, {click_y})")
                    
                    # DEBUG: Desenhar círculo vermelho na posição de clique
                    try:
                        import cv2
                        debug_img = cv2.imread(screenshot_path)
                        if debug_img is not None:
                            cv2.circle(debug_img, (click_x, click_y), 30, (0, 0, 255), 5)
                            cv2.line(debug_img, (click_x - 20, click_y), (click_x + 20, click_y), (0, 0, 255), 3)
                            cv2.line(debug_img, (click_x, click_y - 20), (click_x, click_y + 20), (0, 0, 255), 3)
                            cv2.putText(debug_img, f"Fila {fila_num}: ({click_x}, {click_y})", 
                                       (click_x + 40, click_y), cv2.FONT_HERSHEY_SIMPLEX, 
                                       1, (0, 0, 255), 2)
                            debug_path = f"debug_click_fila_{fila_num}_offset_{offset_y}.png"
                            cv2.imwrite(debug_path, debug_img)
                            print(f"🖼️ Debug: Imagem salva em '{debug_path}'")
                    except Exception as e:
                        print(f"⚠️ Erro ao criar debug visual: {e}")
                    
                    # Clicar na fila (Tela1-Aba → Tela2)
                    simulate_touch(device_id=DEVICE_ID, x=click_x, y=click_y)
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"❌ Erro ao detectar/clicar em fila: {e}")
                    print("🔙 Voltando à Tela0 (5x BACK) e reiniciando ciclo...")
                    execute_back(DEVICE_ID, times=5)
                    time.sleep(0.5)
                    break  # Sai do loop de filas e reinicia ciclo
                
                # ============================================================
                # PARTE 4: CLICAR EM JUNTAR (Tela2 → Tela3)
                # ============================================================
                print(f"🔘 [PARTE 4] Clicando em 'Juntar' (04_juntar.png)")
                sequence_juntar = [rally_sequence[3]]  # passo 4 (Juntar)
                
                success_juntar = execultar_acoes(
                    action_name=RALLY_ACTION_NAME,
                    device_id=DEVICE_ID,
                    account_name="current",
                    sequence_override=sequence_juntar,
                )
                
                if not success_juntar:
                    print(f"⚠️ Botão 'Juntar' não encontrado ou desabilitado (FALHA ESPERADA)")
                    print("🔙 Voltando para Tela1-Aba (1x BACK)")
                    execute_back(DEVICE_ID, times=1)
                    time.sleep(0.5)
                    
                    failed += 1
                    failed_total += 1
                    
                    print(f"➡️ Continuando para próxima fila (permanece na Tela1-Aba)...")
                    continue  # Próxima fila (não precisa clicar Aliança/Batalha novamente)
                
                print("✅ 'Juntar' clicado - Tela3 deve abrir")
                time.sleep(0.5)
                
                # ============================================================
                # PARTE 5: CLICAR EM TROPAS (Tela3)
                # ============================================================
                print(f"💥 [PARTE 5] Clicando em 'Tropas' (05_tropas.png)")
                sequence_tropas = [rally_sequence[4]]  # passo 5 (Tropas)
                
                success_tropas = execultar_acoes(
                    action_name=RALLY_ACTION_NAME,
                    device_id=DEVICE_ID,
                    account_name="current",
                    sequence_override=sequence_tropas,
                )
                
                if not success_tropas:
                    # FALHA ESPERADA: Tela3 não abriu (ainda em Tela2)
                    # Significa que já estamos nesta fila
                    print(f"⚠️ [FALHA ESPERADA] 05_tropas não encontrado - Já estamos nesta fila!")
                    print("🔙 Voltando para Tela1-Aba (1x BACK)")
                    
                    execute_back(DEVICE_ID, times=1)
                    time.sleep(0.5)
                    
                    failed += 1
                    failed_total += 1
                    
                    print(f"➡️ Continuando para próxima fila (permanece na Tela1-Aba)...")
                    continue  # Próxima fila (não precisa clicar Aliança/Batalha novamente)
                
                print("✅ 'Tropas' clicado")
                time.sleep(0.5)
                
                # ============================================================
                # PARTE 6: CLICAR EM MARCHAR (Tela3 → Tela0)
                # ============================================================
                print(f"⚔️ [PARTE 6] Clicando em 'Marchar' (06_marchar.png)")
                sequence_marchar = [rally_sequence[5]]  # passo 6 (Marchar)
                
                success_marchar = execultar_acoes(
                    action_name=RALLY_ACTION_NAME,
                    device_id=DEVICE_ID,
                    account_name="current",
                    sequence_override=sequence_marchar,
                )
                
                if success_marchar:
                    print(f"✅ Fila {fila_num} processada com SUCESSO!")
                    successful += 1
                    successful_total += 1
                    
                    # Garantir que voltou à Tela0 (5x BACK por segurança)
                    print("🔙 Voltando para Tela0 (5x BACK por segurança)")
                    execute_back(DEVICE_ID, times=5, delay=0.3)
                    time.sleep(0.5)
                else:
                    print(f"⚠️ Falha ao clicar em 'Marchar' (possível lag)")
                    failed += 1
                    failed_total += 1
                    
                    # Garantir que voltou à Tela0 (5x BACK)
                    print("🔙 Voltando para Tela0 (5x BACK)")
                    execute_back(DEVICE_ID, times=5, delay=0.3)
                    time.sleep(0.5)

            
            # Resumo do ciclo
            print_separator("=", 80)
            print(f"📊 RESUMO DO CICLO {ciclos_completos}")
            print(f"✅ Sucessos neste ciclo: {successful}")
            print(f"❌ Falhas neste ciclo: {failed}")
            print_separator("=", 80)
            
            # Aguardar antes do próximo ciclo
            print("⏳ Aguardando 3 segundos antes do próximo ciclo...")
            time.sleep(0.5)
        
    except KeyboardInterrupt:
        print("\n⚠️ Loop interrompido pelo usuário")
    finally:
        total_duration = time.time() - start_time_total
        print_separator()
        print("📊 RESUMO FINAL (24/7)")
        print(f"🔄 Ciclos completos: {ciclos_completos}")
        print(f"✅ Total de sucessos: {successful_total}")
        print(f"❌ Total de falhas: {failed_total}")
        print(f"⏱️ Tempo total executado: {total_duration:.1f}s ({total_duration/3600:.1f} horas)")
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