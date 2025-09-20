# Nome do Arquivo: 4879a44f_accounts_config.py
# Descrição: Contém a definição da estrutura das contas utilizadas para o login unificado.
# Versão: 01.00.00 -> Inclusão do ID da célula no nome do arquivo.
# Analista: Gemini
# Programador: Gled Carneiro
# -----------------------------------------------------------------------------

# Definindo a estrutura das contas
# Cada dicionário na lista representa uma conta
# O campo 'name' será usado para identificar o template do email (ex: 'login_gled' -> '02_login_gled.png')
accounts = [
    {"name": "login_gled"},
    {"name": "login_inf"},
    {"name": "login_cav"},
    {"name": "login_c52"},
    {"name": "login_c53"},
    {"name": "login_c54"},
    {"name": "login_c55"},
    {"name": "login_c56"},
    {"name": "login_c57"},
    {"name": "login_c58"},
    # Adicione mais contas aqui conforme necessário, seguindo o padrão 'login_<nome_ou_identificador>'
]

print("Definição da lista 'accounts' para configuração.")
# display(accounts) # Descomente para visualizar a lista completa