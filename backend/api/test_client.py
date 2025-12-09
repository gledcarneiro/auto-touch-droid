import requests
import os

# Configs
API_URL = "http://localhost:8000/processar_acao"
TEST_ACTION = "pegar_bau"
# Usando um template como 'screenshot' para garantir match positivo no teste
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "actions", "templates", "pegar_bau")
TEST_IMAGE = os.path.join(TEMPLATE_DIR, "01_bau.png")

def test_api():
    if not os.path.exists(TEST_IMAGE):
        print(f"Erro: Imagem de teste não encontrada em {TEST_IMAGE}")
        return

    print(f"Enviando {TEST_IMAGE} para {API_URL}...")
    
    try:
        with open(TEST_IMAGE, "rb") as f:
            files = {"file": f}
            data = {"action_name": TEST_ACTION}
            response = requests.post(API_URL, files=files, data=data)
            
        if response.status_code == 200:
            print("Resposta da API:")
            print(response.json())
        else:
            print(f"Erro {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"Falha na conexão: {e}")

if __name__ == "__main__":
    test_api()
