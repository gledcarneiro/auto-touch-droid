# Nome do Arquivo: executar_sequencia_acoes.py
# Descrição: Script para executar uma sequência predefinida de ações.
# Versão: 01.00.00
# Analista: Gemini
# Programador: Gled Carneiro
# -----------------------------------------------------------------------------

# Importa a função de execução de ações
from action_executor import execultar_acoes

# Configurações
# Substitua 'RXCTB03EXVK' pelo ID do seu dispositivo Android, se for diferente.
device_id_execution = 'RXCTB03EXVK'

print("Iniciando execução da sequência de ações...")

# --- Executar a primeira ação: fazer_login ---
action_name_1 = "fazer_login"
print(f"\nExecutando a ação: {action_name_1}")
execultar_acoes(action_name_1, device_id=device_id_execution)

print(f"\nExecução da ação '{action_name_1}' finalizada.")

# --- Executar a segunda ação: pegar_itens ---
action_name_2 = "pegar_itens"
print(f"\nExecutando a ação: {action_name_2}")
execultar_acoes(action_name_2, device_id=device_id_execution)

print(f"\nExecução da ação '{action_name_2}' finalizada.")

print("\nExecução de toda a sequência de ações finalizada.")