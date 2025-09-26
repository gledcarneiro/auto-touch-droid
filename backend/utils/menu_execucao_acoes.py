# Nome do Arquivo: c20377a5_menu_execucao_acoes.py
# Descrição: Script para apresentar um menu de ações disponíveis (pastas em 'acoes/')
#            e executar a ação escolhida pelo usuário.
# Versão: 01.00.06 -> Adicionado opção para executar sequência de login para todas as contas.
# Versão: 01.00.07 -> Importando 'accounts' e 'execute_login_for_account' dos arquivos correspondentes.
# Versão: 01.00.08 -> Adicionada lógica para executar a ação 'fazer_logout' após cada login bem-sucedido.
# Versão: 01.00.09 -> Incluídas as ações 'pegar_bau' e 'pegar_recursos' no loop de login por conta.
# Analista: Gemini
# Programador: Gled Carneiro
# -----------------------------------------------------------------------------
import os
import time # Importar time para o delay entre contas
import json # Importar json para carregar a sequência original

# Adiciona os diretórios necessários ao path
import sys
import os

# Adiciona o diretório raiz do projeto ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(backend_dir)
sys.path.insert(0, project_root)
sys.path.insert(0, backend_dir)

# Importa a função de execução de ações principal e a função de execução por conta
sys.path.append(os.path.join(backend_dir, 'core'))
sys.path.append(os.path.join(backend_dir, 'config'))

from action_executor import execultar_acoes, execute_login_for_account

# Importa a lista de contas do arquivo de configuração
try:
    from accounts_config import accounts
    print("Lista 'accounts' importada de accounts_config.py")
except ImportError:
    print("Erro: Não foi possível importar a lista 'accounts' de accounts_config.py.")
    print("Certifique-se de que salvou o conteúdo da célula 4879a44f como 'accounts_config.py' no mesmo diretório.")
    accounts = [] # Define accounts como lista vazia para evitar erros, mas a funcionalidade de login unificado não funcionará


# Configurações (reutilizando o device_id)
# Substitua 'RXCTB03EXVK' pelo ID do seu dispositivo Android, se for diferente.
device_id_execution = 'RXCTB03EXVK'

acoes_folder = os.path.join(os.path.dirname(__file__), "..", "actions", "templates")
login_action_name = "fazer_login" # Nome da ação de login
logout_action_name = "fazer_logout" # Nome da ação de logout
pegar_bau_action_name = "pegar_bau" # Nome da ação pegar_bau
pegar_recursos_action_name = "pegar_recursos" # Nome da ação pegar_recursos


print("Carregando ações disponíveis...")

# Listar as pastas dentro da pasta 'acoes'
available_actions = [name for name in os.listdir(acoes_folder) if os.path.isdir(os.path.join(acoes_folder, name))]

# Carregar as sequências originais para as ações de login e logout UMA VEZ ao iniciar o menu
original_action_sequence_for_login = None
login_sequence_filepath = os.path.join(acoes_folder, login_action_name, "sequence.json")
try:
    if os.path.exists(login_sequence_filepath):
        with open(login_sequence_filepath, 'r', encoding='utf-8') as f:
            # Ao carregar o JSON do login, verificamos a estrutura (lista ou dicionário)
            # A função execute_login_for_account espera a lista de passos,
            # mas execultar_acoes precisa da config de success_image se for o novo formato.
            # Vamos carregar o dicionário completo se for o novo formato, e a lista se for o antigo.
            login_action_data = json.load(f)
            if isinstance(login_action_data, list):
                 original_action_sequence_for_login = login_action_data # Formato antigo
                 print(f"Sequência original para '{login_action_name}' carregada (formato lista) para uso no menu.")
            elif isinstance(login_action_data, dict) and "sequence" in login_action_data and isinstance(login_action_data["sequence"], list):
                 original_action_sequence_for_login = login_action_data # Novo formato (dicionário completo)
                 print(f"Sequência original para '{login_action_name}' carregada (formato dicionário) para uso no menu.")
            else:
                 print(f"Erro: O conteúdo do arquivo '{login_sequence_filepath}' não tem a estrutura esperada (lista ou dicionário com chave 'sequence'). A opção de executar login para todas as contas pode não funcionar.")
                 original_action_sequence_for_login = None # Define como None em caso de estrutura inválida

    else:
         print(f"Aviso: Arquivo de sequência para '{login_action_name}' não encontrado em '{login_sequence_filepath}'. A opção de executar login para todas as contas pode não funcionar.")

except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Erro ao carregar o arquivo de sequência '{login_sequence_filepath}' para uso no menu: {e}. A opção de executar login para todas as contas pode não funcionar.")
    original_action_sequence_for_login = None

original_action_sequence_for_logout = None
logout_sequence_filepath = os.path.join(acoes_folder, logout_action_name, "sequence.json")
try:
    if os.path.exists(logout_sequence_filepath):
        with open(logout_sequence_filepath, 'r', encoding='utf-8') as f:
            logout_action_data = json.load(f) # Carrega o conteúdo do JSON de logout

            # --- CORREÇÃO AQUI: Extrair a lista de passos da chave "sequence" ---
            if isinstance(logout_action_data, list):
                 original_action_sequence_for_logout = logout_action_data # Formato antigo (lista direta)
                 print(f"Sequência original para '{logout_action_name}' carregada (formato lista) para uso no menu.")
            elif isinstance(logout_action_data, dict) and "sequence" in logout_action_data and isinstance(logout_action_data["sequence"], list):
                 original_action_sequence_for_logout = logout_action_data["sequence"] # Extrai APENAS a lista da chave 'sequence'
                 print(f"Sequência original para '{logout_action_name}' carregada (formato dicionário - extraindo 'sequence') para uso no menu.")
            else:
                 print(f"Erro: O conteúdo do arquivo '{logout_sequence_filepath}' não tem a estrutura esperada (lista ou dicionário com chave 'sequence'). A opção de executar login para todas as contas pode não funcionar.")
                 original_action_sequence_for_logout = None # Define como None em caso de estrutura inválida


    else:
         print(f"Aviso: Arquivo de sequência para '{logout_action_name}' não encontrado em '{logout_sequence_filepath}'. A opção de executar login para todas as contas pode não funcionar.")

except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Erro ao carregar o arquivo de sequência '{logout_sequence_filepath}' para uso no menu: {e}. A opção de executar login para todas as contas pode não funcionar.")
    original_action_sequence_for_logout = None


# Reutilizando a lista de contas definida anteriormente (assumindo que a célula 4879a44f foi executada)
# Se a lista 'accounts' não estiver no escopo, esta parte precisará ser ajustada
# if 'accounts' not in locals(): # Esta verificação agora é feita pelo try-except da importação
#      print("Aviso: A lista 'accounts' não está definida no escopo global. A opção de executar login para todas as contas pode não funcionar.")
#      accounts = [] # Define como vazia para evitar erro, mas a funcionalidade de login unificado não funcionará


if not available_actions and not accounts: # Verificar se há ações OU contas para login
    print(f"Nenhuma pasta de ação encontrada em '{acoes_folder}' e a lista de contas não está definida ou não foi importada. Crie ações usando o modo de gravação assistida primeiro ou defina as contas e salve 'accounts_config.py'.")
else:
    while True:
        print("\n--- Menu de Execução de Ações ---")
        print("Ações Disponíveis:")
        for i, action_name in enumerate(available_actions):
            print(f"{i + 1}: {action_name}")

        print("\nOpções Especiais:")
        print("l: Executar Fluxo Completo para Todas as Contas (Login → Ações → Logout)")
        print("s: Executar Sequência Customizada")

        print("\nDigite o número da ação individual, 'l' para fluxo completo, 's' para sequência customizada, ou 'q' para sair.")

        choice = input(f"Escolha uma opção (1-{len(available_actions)}, l, s, q): ").lower()

        if choice == 'q':
            print("Saindo do menu de execução.")
            break

        elif choice == 'l': # Nova opção para executar login em todas as contas (Sequência)
            if not accounts:
                 print("Erro: A lista de contas ('accounts') está vazia ou não foi importada corretamente. Não é possível executar o login para todas as contas.")
            # A verificação da sequência de login agora precisa considerar que original_action_sequence_for_login pode ser uma lista OU um dicionário
            elif original_action_sequence_for_login is None or (isinstance(original_action_sequence_for_login, dict) and "sequence" not in original_action_sequence_for_login):
                 print(f"Erro: A sequência de ação para '{login_action_name}' não foi carregada corretamente ou não tem a estrutura esperada. Não é possível executar o login para todas as contas.")
            elif original_action_sequence_for_logout is None: # original_action_sequence_for_logout JÁ é a lista de passos aqui
                 print(f"Erro: A lista de passos para a sequência de ação '{logout_action_name}' não foi carregada corretamente. Não é possível executar o login para todas as contas.")

            else:
                print("\n--- Executando Sequência de Login para Todas as Contas ---")
                # Iterar sobre a lista de contas e chamar a função de execução para cada uma
                if 'execute_login_for_account' in locals(): # Verifica se a função execute_login_for_account foi importada/definida
                    # Ao chamar execute_login_for_account, passamos o original_action_sequence_for_login
                    # que PODE SER o dicionário completo se for o novo formato de JSON de login.
                    # A função execute_login_for_account precisará extrair a lista de passos se for um dicionário.
                    # Já ajustamos execute_login_for_account para fazer isso.
                    for account in accounts:
                        # 1. Executar Login para a conta atual
                        print(f"\n-> Iniciando LOGIN para a conta: {account.get('name')} <-")
                        # execute_login_for_account agora retorna True/False indicando se a imagem de sucesso foi encontrada
                        login_success = execute_login_for_account(account, original_action_sequence_for_login, device_id=device_id_execution)

                        if login_success:
                            print(f"\n-> LOGIN bem-sucedido para a conta: {account.get('name')} <-")
                            # Adicionar um pequeno delay após o login antes de tentar deslogar ou ir para a próxima
                            time.sleep(3) # Ajuste conforme necessário

                            # 2. Executar ações (pegar_bau, pegar_recursos)
                            print(f"\n-> Executando ações (pegar_bau, pegar_recursos) para a conta: {account.get('name')} <-")

                            # Executar pegar_bau
                            print(f"\nExecutando a ação: {pegar_bau_action_name}")
                            # Para ações únicas do menu, carregamos do arquivo (sem override)
                            execultar_acoes(pegar_bau_action_name, device_id=device_id_execution)
                            time.sleep(2) # Pequeno delay entre ações

                            # Executar pegar_recursos
                            print(f"\nExecutando a ação: {pegar_recursos_action_name}")
                            # Para ações únicas do menu, carregamos do arquivo (sem override)
                            execultar_acoes(pegar_recursos_action_name, device_id=device_id_execution)
                            time.sleep(2) # Pequeno delay após a última ação


                            # 3. Fazer Logout
                            print(f"\n-> Iniciando LOGOUT após ações para a conta: {account.get('name')} <-")
                            # Chamar a função execultar_acoes com a sequência de logout
                            # Passamos a sequência original do logout como override, pois ela já foi carregada
                            # original_action_sequence_for_logout AGORA É A LISTA DE PASSOS DIRETA
                            logout_success = execultar_acoes(action_name=logout_action_name, device_id=device_id_execution, sequence_override=original_action_sequence_for_logout)

                            if logout_success:
                                print(f"\n-> LOGOUT bem-sucedido após login da conta: {account.get('name')} <-")
                                # Adicionar um delay entre as contas APÓS o logout
                                time.sleep(5) # Espera 5 segundos entre as contas (ajuste conforme necessário)
                            else:
                                print(f"Aviso: Falha ao executar LOGOUT após login da conta {account.get('name')}.")
                                # Decida o que fazer em caso de falha no logout (parar ou continuar?)
                                # Por enquanto, vamos CONTINUAR para a próxima conta, assumindo que o próximo login pode corrigir o estado.
                                pass


                        else:
                            print(f"\n-> FALHA no LOGIN para a conta: {account.get('name')} <-")
                            print("Pulando ações e logout para esta conta e continuando para a próxima.")
                            # Não tenta deslogar se o login falhou.
                            # Adicionar um delay antes de ir para a próxima conta, mesmo após falha no login.
                            time.sleep(5) # Ajuste conforme necessário

                    print("\nExecução da sequência de Login/Logout para todas as contas finalizada.")
                else:
                    print("Erro interno: A função 'execute_login_for_account' não foi encontrada após a importação. Por favor, verifique o arquivo action_executor.py.")


            continue # Volta para o início do loop principal para mostrar o menu novamente


        elif choice == 's': # Opção existente para sequência customizada
            print("\n--- Executar Sequência Customizada ---")
            sequence_input = input(f"Digite os NÚMEROS das ações para a sequência, separados por vírgula (ex: 1,3,5,2): ")
            if not sequence_input:
                print("Nenhuma ação especificada para a sequência. Voltando ao menu.")
                continue

            selected_indices_str = [idx.strip() for idx in sequence_input.split(',')]
            sequence_to_execute = []
            valid_sequence = True

            for index_str in selected_indices_str:
                try:
                    index = int(index_str) - 1
                    if 0 <= index < len(available_actions):
                        sequence_to_execute.append(available_actions[index])
                    else:
                        print(f"Erro: Índice '{index_str}' inválido. Não corresponde a nenhuma ação disponível.")
                        valid_sequence = False
                        break
                except ValueError:
                    print(f"Erro: Entrada '{index_str}' inválida. Por favor, digite apenas números separados por vírgula.")
                    valid_sequence = False
                    break

            if valid_sequence and sequence_to_execute:
                print(f"\nIniciando execução da sequência de ações: {sequence_to_execute}")

                for i, action_name in enumerate(sequence_to_execute):
                    print(f"\n--- Executando passo {i+1}/{len(sequence_to_execute)} da sequência: Ação '{action_name}' ---")
                    try:
                        # Para sequências customizadas, não usamos sequence_override, carregamos do arquivo
                        execultar_acoes(action_name, device_id=device_id_execution)
                    except Exception as e:
                        print(f"Ocorreu um erro ao executar a ação '{action_name}': {e}")
                        print("Interrompendo a execução da sequência devido ao erro.")
                        break

                print("\nExecução da sequência de ações finalizada.")
            elif not valid_sequence:
                 print("Sequência inválida. Por favor, tente novamente com índices válidos.")
            else:
                 print("Nenhuma ação válida especificada na sequência. Voltando ao menu.")

            continue


        try:
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(available_actions):
                selected_action_name = available_actions[choice_index]
                print(f"\nVocê escolheu executar a ação: '{selected_action_name}'")

                print(f"Iniciando execução da ação: {selected_action_name}")
                # Para ações únicas do menu, carregamos do arquivo
                execultar_acoes(selected_action_name, device_id=device_id_execution)

            else:
                print("Número inválido. Por favor, digite um número da lista, 's', 'l', ou 'q'.")


        except ValueError:
            print("Entrada inválida. Por favor, digite um número da lista, 's', 'l', ou 'q'.")

        except Exception as e:
            print(f"Ocorreu um erro durante a execução da ação: {e}")
            run_again_on_error = input("Deseja tentar executar outra ação? (s/n): ").lower()
            if run_again_on_error != 's':
                 print("Saindo do menu de execução após erro.")
                 break


print("\nMenu de execução de ações finalizado.")