"""
Sincronização da Memória Local com GitHub
"""

from github_memory_api import GitHubMemoryAPI
from pathlib import Path

def sync_all_memory():
    """Sincroniza toda a memória local com GitHub"""
    print("🔄 Iniciando sincronização da memória...")
    
    api = GitHubMemoryAPI()
    
    # Testa conexão
    success, msg = api.test_connection()
    if not success:
        print(f"❌ Erro de conexão: {msg}")
        return False
    
    print(f"✅ {msg}")
    
    # Sincroniza memória local
    memory_path = Path(__file__).parent
    success, results = api.sync_local_to_github(memory_path)
    
    if success:
        print("\n📤 Resultados da sincronização:")
        for result in results:
            print(f"   {result}")
        print("\n🌟 MEMÓRIA SINCRONIZADA COM SUCESSO!")
        print(f"🔗 Acesse: https://github.com/{api.owner}/{api.repo_name}")
        return True
    else:
        print(f"❌ Erro na sincronização: {results}")
        return False

if __name__ == "__main__":
    sync_all_memory()