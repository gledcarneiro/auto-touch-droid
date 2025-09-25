# Nome do Arquivo: e0196379_gravação_assistida_inicio.py
# Descrição: Script para iniciar o modo de gravação assistida de sequência de ações.
# Versão: 01.00.00
# Analista: Gemini
# Programador: Gled Carneiro
# -----------------------------------------------------------------------------

# Importa a função de gravação assistida do script create_action_template.py
from ..actions.create_action_template import record_action_sequence_assisted

# Configurações
# Substitua 'RXCTB03EXVK' pelo ID do seu dispositivo Android, se for diferente.
# Você pode encontrar o ID executando `adb devices` no terminal.
device_id_recording = 'RXCTB03EXVK'

# Solicita o nome da ação ao usuário no início da execução
action_name_to_record = input("Digite o nome da ação que você quer gravar/editar: ")

if not action_name_to_record:
    print("Nome da ação não fornecido. Cancelando gravação assistida.")
else:
    print(f"\nPreparando para iniciar a gravação assistida para a ação: '{action_name_to_record}'")
    print("Certifique-se de que seu dispositivo Android está conectado via ADB.")

    # Chama a função principal para iniciar o modo de gravação assistida
    # A execução desta célula irá pausar e pedir sua interação no console para cada passo.
    record_action_sequence_assisted(action_name_to_record, device_id=device_id_recording)

    print(f"\nChamada da função de gravação assistida para '{action_name_to_record}' finalizada.")
    print("O arquivo de sequência (sequence.json) foi criado/atualizado na pasta da ação.")