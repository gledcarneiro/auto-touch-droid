"""
GitHub Memory API - Sistema de Memória Online
Conecta nossa memória local com repositório GitHub para acesso universal
"""

import json
import requests
import base64
from pathlib import Path
from datetime import datetime
import os

class GitHubMemoryAPI:
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.owner = None  # Será definido quando tivermos o token
        self.repo_name = "claude-gled-memory"
        self.token = self._load_token()
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def _load_token(self):
        """Carrega token do arquivo seguro"""
        token_file = Path(__file__).parent / ".github_token"
        if token_file.exists():
            with open(token_file, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        return line
        return None
    
    def test_connection(self):
        """Testa conexão com GitHub"""
        if not self.token:
            return False, "Token não encontrado"
        
        try:
            response = requests.get(f"{self.base_url}/user", headers=self.headers)
            if response.status_code == 200:
                user_data = response.json()
                self.owner = user_data['login']
                return True, f"Conectado como {user_data['login']}"
            else:
                return False, f"Erro de autenticação: {response.status_code}"
        except Exception as e:
            return False, f"Erro de conexão: {str(e)}"
    
    def create_memory_repository(self):
        """Cria repositório dedicado para memória"""
        if not self.owner:
            success, msg = self.test_connection()
            if not success:
                return False, msg
        
        repo_data = {
            "name": self.repo_name,
            "description": "Claude-Gled Partnership Memory System - Universal AI Memory",
            "private": True,  # Repositório privado por segurança
            "auto_init": True
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/user/repos",
                headers=self.headers,
                json=repo_data
            )
            
            if response.status_code == 201:
                return True, "Repositório criado com sucesso!"
            elif response.status_code == 422:
                return True, "Repositório já existe!"
            else:
                return False, f"Erro ao criar repositório: {response.status_code}"
        except Exception as e:
            return False, f"Erro: {str(e)}"
    
    def upload_memory_file(self, file_path, content, commit_message=None):
        """Faz upload de arquivo de memória para GitHub"""
        if not commit_message:
            commit_message = f"Update memory: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Codifica conteúdo em base64
        content_encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        # Verifica se arquivo já existe
        file_url = f"{self.base_url}/repos/{self.owner}/{self.repo_name}/contents/{file_path}"
        
        try:
            # Tenta obter SHA do arquivo existente
            response = requests.get(file_url, headers=self.headers)
            sha = None
            if response.status_code == 200:
                sha = response.json()['sha']
            
            # Dados para upload
            upload_data = {
                "message": commit_message,
                "content": content_encoded
            }
            
            if sha:
                upload_data["sha"] = sha
            
            # Faz upload
            response = requests.put(file_url, headers=self.headers, json=upload_data)
            
            if response.status_code in [200, 201]:
                return True, "Arquivo enviado com sucesso!"
            else:
                return False, f"Erro no upload: {response.status_code}"
                
        except Exception as e:
            return False, f"Erro: {str(e)}"
    
    def download_memory_file(self, file_path):
        """Baixa arquivo de memória do GitHub"""
        file_url = f"{self.base_url}/repos/{self.owner}/{self.repo_name}/contents/{file_path}"
        
        try:
            response = requests.get(file_url, headers=self.headers)
            
            if response.status_code == 200:
                file_data = response.json()
                content = base64.b64decode(file_data['content']).decode('utf-8')
                return True, content
            else:
                return False, f"Arquivo não encontrado: {response.status_code}"
                
        except Exception as e:
            return False, f"Erro: {str(e)}"
    
    def sync_local_to_github(self, local_memory_path):
        """Sincroniza memória local com GitHub"""
        local_path = Path(local_memory_path)
        if not local_path.exists():
            return False, "Diretório local não encontrado"
        
        results = []
        
        # Sincroniza todos os arquivos JSON
        for json_file in local_path.rglob("*.json"):
            relative_path = json_file.relative_to(local_path)
            github_path = str(relative_path).replace("\\", "/")
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                success, msg = self.upload_memory_file(
                    github_path, 
                    content, 
                    f"Sync: {relative_path}"
                )
                results.append(f"{github_path}: {msg}")
                
            except Exception as e:
                results.append(f"{github_path}: Erro - {str(e)}")
        
        return True, results

# Função de teste rápido
def test_github_memory():
    """Testa sistema de memória GitHub"""
    api = GitHubMemoryAPI()
    
    print("🔍 Testando conexão...")
    success, msg = api.test_connection()
    print(f"   {msg}")
    
    if success:
        print("\n📁 Criando repositório...")
        success, msg = api.create_memory_repository()
        print(f"   {msg}")
        
        if success:
            print("\n🚀 Sistema GitHub Memory pronto!")
            return True
    
    return False

if __name__ == "__main__":
    test_github_memory()