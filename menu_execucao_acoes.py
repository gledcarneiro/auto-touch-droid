# Nome do Arquivo: c20377a5_menu_execucao_acoes.py
# Descrição: Script para apresentar um menu de ações disponíveis (pastas em 'acoes/')
#            e executar a ação escolhida pelo usuário.
# Versão: 01.00.05 -> Refatorado para ser o script principal e reduzir logs.
# Analista: Gemini
# Programador: Gled Carneiro
# -----------------------------------------------------------------------------
import os
from action_executor import execultar_acoes # Importa a função de execução

# Configurações (reutilizando o device_id)
# Substitua 'RXCTB03EXVK' pelo ID do seu dispositivo Android, se for diferente.
device_id_execution = 'RXCTB03EXVK'

acoes_folder = "acoes"

print("Carregando ações disponíveis...")

# Listar as pastas dentro da pasta 'acoes'
available_actions = [name for name in os.listdir(acoes_folder) if os.path.isdir(os.path.join(acoes_folder, name))]

if not available_actions:
    print(f"Nenhuma pasta de ação encontrada em '{acoes_folder}'. Crie ações usando o modo de gravação assistida primeiro.")
else:
    # Mover a listagem do menu para dentro do loop principal para que apareça a cada iteração
    while True:
        print("\n--- Menu de Execução de Ações ---") # Título do menu movido para dentro do loop
        print("Ações Disponíveis:")
        for i, action_name in enumerate(available_actions):
            print(f"{i + 1}: {action_name}")
        print(f"{len(available_actions) + 1}: Executar Sequência de Ações") # Opção para sequência

        print("\nDigite o número da ação que deseja executar, 's' para executar uma sequência, ou 'q' a qualquer momento para sair.")


        choice = input(f"Escolha uma opção (1-{len(available_actions)}, s, q): ").lower()

        if choice == 'q':
            print("Saindo do menu de execução.")
            break
        elif choice == 's':
            print("\n--- Executar Sequência de Ações ---")
            # Solicitar os índices das ações para a sequência
            sequence_input = input(f"Digite os NÚMEROS das ações para a sequência, separados por vírgula (ex: 1,3,5,2): ")
            if not sequence_input:
                print("Nenhuma ação especificada para a sequência. Voltando ao menu.")
                continue # Volta para o início do loop para mostrar o menu novamente

            # Processar a entrada e validar os índices
            selected_indices_str = [idx.strip() for idx in sequence_input.split(',')]
            sequence_to_execute = []
            valid_sequence = True

            for index_str in selected_indices_str:
                try:
                    index = int(index_str) - 1 # Ajusta para índice baseado em zero
                    if 0 <= index < len(available_actions):
                        sequence_to_execute.append(available_actions[index])
                    else:
                        print(f"Erro: Índice '{index_str}' inválido. Não corresponde a nenhuma ação disponível.")
                        valid_sequence = False
                        break # Interrompe a validação se um índice for inválido
                except ValueError:
                    print(f"Erro: Entrada '{index_str}' inválida. Por favor, digite apenas números separados por vírgula.")
                    valid_sequence = False
                    break # Interrompe a validação se a entrada não for um número

            if valid_sequence and sequence_to_execute:
                print(f"\nIniciando execução da sequência de ações: {sequence_to_execute}")

                # --- Executar a sequência de ações ---
                for i, action_name in enumerate(sequence_to_execute):
                    print(f"\n--- Executando passo {i+1}/{len(sequence_to_execute)} da sequência: Ação '{action_name}' ---")
                    try:
                        # A função execultar_acoes já imprime logs sobre os passos internos
                        execultar_acoes(action_name, device_id=device_id_execution)
                        # print(f"Execução da ação '{action_name}' finalizada.") # Log removido para reduzir verbosidade
                    except Exception as e:
                        print(f"Ocorreu um erro ao executar a ação '{action_name}': {e}")
                        print("Interrompendo a execução da sequência devido ao erro.")
                        break # Interrompe a sequência em caso de erro

                print("\nExecução da sequência de ações finalizada.")
            elif not valid_sequence:
                 print("Sequência inválida. Por favor, tente novamente com índices válidos.")
            else: # sequence_to_execute está vazia (acontece se a entrada for apenas vírgulas, por exemplo)
                 print("Nenhuma ação válida especificada na sequência. Voltando ao menu.")

            continue # Volta para o início do loop principal para mostrar o menu novamente


        try:
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(available_actions):
                selected_action_name = available_actions[choice_index]
                print(f"\nVocê escolheu executar a ação: '{selected_action_name}'")

                # --- Executar a ação escolhida ---
                print(f"Iniciando execução da ação: {selected_action_name}")
                # A função execultar_acoes já imprime logs sobre os passos internos
                execultar_acoes(selected_action_name, device_id=device_id_execution)
                # print(f"Execução da ação '{selected_action_name}' finalizada.") # Log removido para reduzir verbosidade

                # Remove a pergunta "Executar outra ação? (s/n):" e volta direto para o menu
                # run_again = input("\nExecutar outra ação? (s/n): ").lower()
                # if run_again != 's':
                #     print("Saindo do menu de execução.")
                #     break # Sai do loop principal se não quiser rodar novamente

                # print("\nVoltando ao menu de execução...") # Mensagem removida ou ajustada para menos verbosidade
                # O menu será listado automaticamente na próxima iteração do loop while True


            else:
                print("Número inválido. Por favor, digite um número da lista, 's' ou 'q'.")
                # O menu será listado automaticamente na próxima iteração do loop


        except ValueError:
            print("Entrada inválida. Por favor, digite um número da lista, 's' ou 'q'.")
            # O menu será listado automaticamente na próxima iteração do loop

        except Exception as e:
            print(f"Ocorreu um erro durante a execução da ação: {e}")
            # Opcional: Decidir se continua o menu ou sai após um erro
            run_again_on_error = input("Deseja tentar executar outra ação? (s/n): ").lower()
            if run_again_on_error != 's':
                 print("Saindo do menu de execução após erro.")
                 break
            # O menu será listado automaticamente na próxima iteração do loop após escolher continuar


print("\nMenu de execução de ações finalizado.") # Mensagem final após sair do loop