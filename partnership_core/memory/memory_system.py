"""
🧠 SISTEMA DE MEMÓRIA PERSISTENTE - CLAUDE & GLED
Preparado para expansão futura com SOLO e capacidades avançadas
VERSÃO UNIVERSAL - Funciona em todos os projetos e contextos

Visão: Criar um assistente que nunca esquece e evolui junto com o usuário
Objetivo: Base para integração total no mundo digital do Gled
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import hashlib
from pathlib import Path

# Importar GitHub API se disponível
try:
    from github_memory_api import GitHubMemoryAPI
    GITHUB_AVAILABLE = True
except ImportError:
    try:
        from .github_memory_api import GitHubMemoryAPI
        GITHUB_AVAILABLE = True
    except ImportError:
        GITHUB_AVAILABLE = False

class ClaudeMemorySystem:
    """
    Sistema de memória persistente para Claude
    VERSÃO UNIVERSAL - Acesso de qualquer projeto
    Preparado para futuras integrações com SOLO
    """
    
    def __init__(self, base_path: str = None, enable_github: bool = True):
        # Detectar automaticamente o caminho da partnership
        if base_path is None:
            self.base_path = Path(self.find_partnership_root()) / "memory"
        else:
            self.base_path = Path(base_path)
            
        self.ensure_directories()
        self.current_project = self.detect_current_project()
        
        # Inicializar GitHub API se disponível e habilitado
        self.github_api = None
        if GITHUB_AVAILABLE and enable_github:
            try:
                self.github_api = GitHubMemoryAPI()
                print("🌐 GitHub Memory API inicializada!")
            except Exception as e:
                print(f"⚠️ GitHub API não disponível: {e}")
                self.github_api = None
        
    def find_partnership_root(self):
        """Encontra automaticamente o diretório partnership_core"""
        current = Path.cwd()
        
        # Procurar partnership_core no diretório atual e pais
        for path in [current] + list(current.parents):
            partnership_path = path / "partnership_core"
            if partnership_path.exists():
                return partnership_path
                
        # Se não encontrar, criar no diretório atual
        partnership_path = current / "partnership_core"
        partnership_path.mkdir(exist_ok=True)
        return partnership_path
        
    def detect_current_project(self):
        """Detecta qual projeto está sendo usado atualmente"""
        current = Path.cwd()
        
        # Verificar se há arquivo de integração Claude
        integration_file = current / ".claude_integration.json"
        if integration_file.exists():
            with open(integration_file) as f:
                data = json.load(f)
                return data.get("project_name", "unknown")
                
        # Detectar pelo nome do diretório
        return current.name
        
    def ensure_directories(self):
        """Cria estrutura de diretórios para memória UNIVERSAL"""
        directories = [
            "sessions",
            "context", 
            "conversations",
            "projects",  # Memória específica por projeto
            "universal",  # Memória compartilhada
            "future_capabilities"  # Para SOLO
        ]
        
        for directory in directories:
            (self.base_path / directory).mkdir(parents=True, exist_ok=True)
            
    def save_universal_interaction(self, user_input: str, context: str = "general"):
        """Salva interação que pode ser acessada de qualquer projeto"""
        timestamp = datetime.now().isoformat()
        interaction_id = hashlib.md5(f"{timestamp}{user_input}".encode()).hexdigest()[:8]
        
        interaction_data = {
            "id": interaction_id,
            "timestamp": timestamp,
            "user_input": user_input,
            "context": context,
            "project": getattr(self, 'current_project', 'auto-touch-droid'),
            "universal": True
        }
        
        # Salvar na memória universal
        universal_file = self.base_path / "universal" / f"{timestamp[:10]}.json"
        self.append_to_file(universal_file, interaction_data)
        
        # Salvar na memória específica do projeto
        current_project = getattr(self, 'current_project', 'auto-touch-droid')
        project_file = self.base_path / "projects" / f"{current_project}.json"
        self.append_to_file(project_file, interaction_data)
        
        # Sincronizar com GitHub se disponível
        self.sync_to_github_async()
        
        return interaction_id
        
    def append_to_file(self, file_path: Path, data: dict):
        """Adiciona dados a um arquivo JSON (array)"""
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        else:
            existing_data = []
            
        existing_data.append(data)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
            
    def get_universal_memory(self, limit: int = 50):
        """Recupera memória universal (acessível de qualquer projeto)"""
        universal_dir = self.base_path / "universal"
        all_interactions = []
        
        for file_path in sorted(universal_dir.glob("*.json"), reverse=True):
            with open(file_path, 'r', encoding='utf-8') as f:
                interactions = json.load(f)
                all_interactions.extend(interactions)
                
            if len(all_interactions) >= limit:
                break
                
        return all_interactions[:limit]
        
    def get_project_memory(self, project_name: str = None, limit: int = 50):
        """Recupera memória específica de um projeto"""
        if project_name is None:
            project_name = self.current_project
            
        project_file = self.base_path / "projects" / f"{project_name}.json"
        
        if not project_file.exists():
            return []
            
        with open(project_file, 'r', encoding='utf-8') as f:
            interactions = json.load(f)
            
        return interactions[-limit:] if interactions else []
        
    def search_memory(self, query: str, project_specific: bool = False):
        """Busca na memória por palavras-chave"""
        results = []
        
        if project_specific:
            interactions = self.get_project_memory()
        else:
            interactions = self.get_universal_memory()
            
        query_lower = query.lower()
        
        for interaction in interactions:
            if query_lower in interaction.get("user_input", "").lower():
                results.append(interaction)
                
        return results
        
    def get_partnership_status(self):
        """Retorna status completo da parceria"""
        universal_count = len(self.get_universal_memory(1000))
        project_count = len(self.get_project_memory(1000))
        
        # Contar projetos integrados
        projects_dir = self.base_path / "projects"
        integrated_projects = len(list(projects_dir.glob("*.json")))
        
        return {
            "universal_interactions": universal_count,
            "current_project_interactions": project_count,
            "integrated_projects": integrated_projects,
            "current_project": self.current_project,
            "memory_path": str(self.base_path),
            "status": "ACTIVE" if universal_count > 0 else "INITIALIZING"
        }
        
    def show_recent_memories(self, count: int = 10):
        """Mostra memórias recentes de forma amigável"""
        print(f"🧠 MEMÓRIAS RECENTES ({count} últimas)")
        print("=" * 50)
        
        memories = self.get_universal_memory(count)
        
        if not memories:
            print("📝 Nenhuma memória encontrada ainda")
            print("💡 Comece a conversar para criar memórias!")
            return
            
        for i, memory in enumerate(memories, 1):
            timestamp = memory.get("timestamp", "")
            project = memory.get("project", "unknown")
            user_input = memory.get("user_input", "")[:100]
            
            print(f"\n{i}. 📅 {timestamp[:19]}")
            print(f"   📂 Projeto: {project}")
            print(f"   💬 \"{user_input}{'...' if len(user_input) == 100 else ''}\"")
    
    def sync_to_github_async(self):
        """Sincronização assíncrona com GitHub (não bloqueia)"""
        if not self.github_api:
            return False
            
        try:
            # Sincronização em background (não bloqueia)
            import threading
            thread = threading.Thread(target=self._sync_to_github_background)
            thread.daemon = True
            thread.start()
            return True
        except Exception as e:
            print(f"⚠️ Erro na sincronização assíncrona: {e}")
            return False
    
    def _sync_to_github_background(self):
        """Sincronização em background com GitHub"""
        try:
            success, results = self.github_api.sync_local_to_github(self.base_path)
            if success:
                print("🌐 Memória sincronizada com GitHub!")
            else:
                print(f"⚠️ Erro na sincronização: {results}")
        except Exception as e:
            print(f"⚠️ Erro na sincronização background: {e}")
    
    def sync_to_github_now(self):
        """Sincronização imediata com GitHub"""
        if not self.github_api:
            print("❌ GitHub API não disponível")
            return False
            
        try:
            success, results = self.github_api.sync_local_to_github(self.base_path)
            if success:
                print("✅ Sincronização completa com GitHub!")
                for result in results:
                    print(f"   {result}")
                return True
            else:
                print(f"❌ Erro na sincronização: {results}")
                return False
        except Exception as e:
            print(f"❌ Erro na sincronização: {e}")
            return False
    
    def load_from_github(self):
        """Carrega memória do GitHub para local"""
        if not self.github_api:
            print("❌ GitHub API não disponível")
            return False
            
        try:
            success, results = self.github_api.sync_github_to_local(self.base_path)
            if success:
                print("✅ Memória carregada do GitHub!")
                return True
            else:
                print(f"❌ Erro ao carregar: {results}")
                return False
        except Exception as e:
            print(f"❌ Erro ao carregar do GitHub: {e}")
            return False


if __name__ == "__main__":
    # Teste do sistema
    print("🧠 Sistema de Memória Claude & Gled inicializado!")
    print("📁 Estrutura criada em:", memory_system.base_path)
    print("🚀 Preparado para SOLO:", memory_system.prepare_for_solo())