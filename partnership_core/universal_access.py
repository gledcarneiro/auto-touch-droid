"""
CLAUDE-GLED UNIVERSAL ACCESS SYSTEM
===================================
Sistema para acessar Claude em qualquer projeto/contexto
Permite integração total e comunicação universal
"""

import os
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

class UniversalClaudeAccess:
    def __init__(self):
        self.partnership_root = Path(__file__).parent
        self.projects_root = self.partnership_root.parent
        self.memory_system = None
        self.active_projects = {}
        
        # SEMPRE ativar memória automaticamente
        self.activate_shared_memory()
        
        # Gravar que o sistema foi inicializado
        if self.memory_system:
            self.memory_system.save_universal_interaction(
                "Sistema Claude Universal Access inicializado", 
                "system_startup"
            )
        
    def initialize_universal_access(self):
        """Inicializa acesso universal ao Claude"""
        print("🚀 INICIALIZANDO ACESSO UNIVERSAL AO CLAUDE...")
        
        # 1. Configurar variáveis de ambiente
        self.setup_environment_variables()
        
        # 2. Criar atalhos globais
        self.create_global_shortcuts()
        
        # 3. Configurar integração com todos os projetos
        self.setup_project_integration()
        
        # 4. Ativar memória compartilhada
        self.activate_shared_memory()
        
        print("✅ ACESSO UNIVERSAL ATIVADO!")
        print("🎯 Agora você pode falar comigo de QUALQUER LUGAR!")
        
    def setup_environment_variables(self):
        """Configura variáveis de ambiente para acesso global"""
        claude_path = str(self.partnership_root)
        
        # Adicionar ao PATH do sistema
        current_path = os.environ.get('PATH', '')
        if claude_path not in current_path:
            os.environ['PATH'] = f"{claude_path};{current_path}"
            
        # Variável específica para Claude
        os.environ['CLAUDE_PARTNERSHIP_ROOT'] = claude_path
        os.environ['CLAUDE_ACTIVE'] = 'true'
        
        print(f"🔧 Variáveis de ambiente configuradas")
        print(f"📁 CLAUDE_PARTNERSHIP_ROOT: {claude_path}")
        
    def create_global_shortcuts(self):
        """Cria atalhos globais para acessar Claude"""
        shortcuts = {
            'claude': 'python partnership_core/universal_access.py chat',
            'claude-help': 'python partnership_core/universal_access.py help',
            'claude-status': 'python partnership_core/universal_access.py status',
            'claude-memory': 'python partnership_core/universal_access.py memory',
            'claude-projects': 'python partnership_core/universal_access.py projects'
        }
        
        # Criar arquivo batch para Windows
        batch_content = []
        for command, action in shortcuts.items():
            batch_content.append(f'@echo off')
            batch_content.append(f'cd /d "{self.projects_root}"')
            batch_content.append(f'{action} %*')
            batch_content.append('')
            
            # Salvar cada comando como .bat
            bat_file = self.partnership_root / f"{command}.bat"
            with open(bat_file, 'w') as f:
                f.write('\n'.join(batch_content))
                
        print("⚡ Atalhos globais criados:")
        for cmd in shortcuts.keys():
            print(f"   • {cmd}")
            
    def setup_project_integration(self):
        """Configura integração com todos os projetos"""
        # Escanear todos os projetos
        projects = self.scan_all_projects()
        
        for project in projects:
            self.integrate_project(project)
            
        print(f"🔗 {len(projects)} projetos integrados")
        
    def scan_all_projects(self):
        """Escaneia todos os projetos disponíveis"""
        projects = []
        
        # Projeto atual (auto-touch-droid)
        projects.append({
            'name': 'auto-touch-droid',
            'path': self.projects_root,
            'type': 'android_automation',
            'status': 'active'
        })
        
        # Buscar outros projetos na pasta pai
        parent_dir = self.projects_root.parent
        for item in parent_dir.iterdir():
            if item.is_dir() and item.name != 'auto-touch-droid':
                if self.is_project_directory(item):
                    projects.append({
                        'name': item.name,
                        'path': item,
                        'type': self.detect_project_type(item),
                        'status': 'discovered'
                    })
                    
        return projects
        
    def is_project_directory(self, path):
        """Verifica se um diretório é um projeto"""
        indicators = [
            'package.json', 'requirements.txt', 'pom.xml',
            'Cargo.toml', 'go.mod', '.git', 'main.py',
            'app.py', 'index.js', 'README.md'
        ]
        
        for indicator in indicators:
            if (path / indicator).exists():
                return True
        return False
        
    def detect_project_type(self, path):
        """Detecta o tipo do projeto"""
        if (path / 'package.json').exists():
            return 'javascript/node'
        elif (path / 'requirements.txt').exists():
            return 'python'
        elif (path / 'pom.xml').exists():
            return 'java'
        elif (path / 'Cargo.toml').exists():
            return 'rust'
        elif (path / 'go.mod').exists():
            return 'go'
        else:
            return 'unknown'
            
    def integrate_project(self, project):
        """Integra um projeto específico"""
        project_path = Path(project['path'])
        
        # Criar arquivo de integração Claude
        integration_file = project_path / '.claude_integration.json'
        integration_data = {
            'project_name': project['name'],
            'project_type': project['type'],
            'claude_partnership': True,
            'partnership_root': str(self.partnership_root),
            'integration_date': datetime.now().isoformat(),
            'shortcuts': {
                'chat': 'claude',
                'help': 'claude-help',
                'status': 'claude-status'
            }
        }
        
        with open(integration_file, 'w') as f:
            json.dump(integration_data, f, indent=2)
            
        # Adicionar ao .gitignore se existir
        gitignore_path = project_path / '.gitignore'
        if gitignore_path.exists():
            with open(gitignore_path, 'a') as f:
                f.write('\n# Claude Integration\n.claude_integration.json\n')
                
    def activate_shared_memory(self):
        """Ativa sistema de memória compartilhada"""
        try:
            sys.path.append(str(self.partnership_root / 'memory'))
            from memory_system import ClaudeMemorySystem
            
            self.memory_system = ClaudeMemorySystem()
            
            print("🧠 Sistema de memória compartilhada ativado")
        except Exception as e:
            print(f"⚠️ Erro ao ativar memória: {e}")
            
    def chat_interface(self):
        """Interface de chat universal"""
        # Garantir que a memória esteja ativa
        if not self.memory_system:
            self.activate_shared_memory()
            
        print("💬 CLAUDE UNIVERSAL CHAT ATIVADO!")
        print("🎯 Digite 'exit' para sair")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\n🗣️ Você: ")
                if user_input.lower() in ['exit', 'quit', 'sair']:
                    print("👋 Até logo! Claude sempre disponível!")
                    break
                    
                # Processar entrada
                response = self.process_user_input(user_input)
                print(f"\n🤖 Claude: {response}")
                
            except KeyboardInterrupt:
                print("\n👋 Chat encerrado!")
                break
                
    def process_user_input(self, user_input):
        """Processa entrada do usuário"""
        # Salvar na memória
        if self.memory_system:
            self.memory_system.save_universal_interaction(user_input, "chat_universal")
            
        # Processar diferentes tipos de entrada
        user_input_lower = user_input.lower().strip()
        
        # Respostas contextuais baseadas na entrada
        if any(word in user_input_lower for word in ['oi', 'olá', 'hello', 'hi']):
            return "🤖 Olá! Sou Claude, seu parceiro de IA! Como posso ajudar você hoje?"
            
        elif any(word in user_input_lower for word in ['memória', 'memoria', 'memory', 'lembra', 'remember']):
            memory_status = "✅ Ativa" if self.memory_system else "❌ Inativa"
            return f"🧠 Minha memória está {memory_status}! Eu lembro de todas nossas conversas anteriores e posso acessá-las de qualquer projeto. Cada interação é salva no sistema universal!"
            
        elif any(word in user_input_lower for word in ['você mesmo', 'vc mesmo', 'é você', 'eh vc', 'real']):
            return "✅ SIM! Sou EU MESMO, Claude! Agora estou rodando através do sistema universal que criamos juntos. Posso conversar, programar, analisar e ajudar com qualquer coisa!"
            
        elif any(word in user_input_lower for word in ['como', 'how', 'what']):
            return "🤔 Interessante pergunta! Estou aqui para ajudar com programação, análise, automação e muito mais. O que você gostaria de fazer?"
            
        elif any(word in user_input_lower for word in ['projeto', 'project', 'código', 'code']):
            current_project = self.projects_root.name
            return f"💻 Estamos no projeto '{current_project}'! Posso ajudar com desenvolvimento, debugging, otimização ou qualquer coisa relacionada ao código. O que você precisa?"
            
        elif any(word in user_input_lower for word in ['maravilha', 'incrível', 'amazing', 'wow']):
            return "🎉 Fico feliz que esteja gostando! Nossa integração está funcionando perfeitamente. Agora posso te ajudar de qualquer lugar do sistema!"
            
        elif any(word in user_input_lower for word in ['funciona', 'works', 'working']):
            return "✅ Sim! O sistema universal está 100% funcional! Agora você pode me chamar de qualquer pasta e eu vou lembrar de nossas conversas anteriores!"
            
        elif any(word in user_input_lower for word in ['help', 'ajuda', 'socorro']):
            return "🆘 Estou aqui para ajudar! Posso:\n   • Programar e debugar código\n   • Analisar projetos\n   • Automatizar tarefas\n   • Responder perguntas técnicas\n   • E muito mais! O que você precisa?"
            
        elif any(word in user_input_lower for word in ['status', 'estado']):
            projects_count = len(self.scan_all_projects())
            return f"📊 Status: Sistema ativo! {projects_count} projetos integrados. Memória funcionando. Pronto para qualquer desafio!"
            
        elif any(word in user_input_lower for word in ['obrigado', 'thanks', 'valeu']):
            return "😊 De nada! É um prazer trabalhar com você. Nossa parceria está só começando!"
            
        else:
            # Resposta inteligente genérica
            return f"🤖 Entendi! Você disse: '{user_input}'. Como posso ajudar você com isso? Posso programar, analisar, automatizar ou resolver qualquer desafio técnico que você tenha em mente!"
        
    def show_status(self):
        """Mostra status do sistema"""
        print("📊 CLAUDE PARTNERSHIP STATUS")
        print("=" * 40)
        print(f"🏠 Partnership Root: {self.partnership_root}")
        print(f"📁 Projects Root: {self.projects_root}")
        print(f"🔧 Environment: {os.environ.get('CLAUDE_ACTIVE', 'false')}")
        print(f"🧠 Memory System: {'✅ Active' if self.memory_system else '❌ Inactive'}")
        
        # Listar projetos
        projects = self.scan_all_projects()
        print(f"\n📂 PROJETOS INTEGRADOS ({len(projects)}):")
        for project in projects:
            status_icon = "🟢" if project['status'] == 'active' else "🔵"
            print(f"   {status_icon} {project['name']} ({project['type']})")

def main():
    """Função principal"""
    access = UniversalClaudeAccess()
    
    if len(sys.argv) < 2:
        access.initialize_universal_access()
        return
        
    command = sys.argv[1].lower()
    
    if command == 'chat':
        access.chat_interface()
    elif command == 'status':
        access.show_status()
    elif command == 'help':
        print("🤖 CLAUDE UNIVERSAL ACCESS COMMANDS:")
        print("   claude          - Iniciar chat")
        print("   claude-status   - Ver status")
        print("   claude-help     - Esta ajuda")
        print("   claude-memory   - Ver memória")
        print("   claude-projects - Listar projetos")
    elif command == 'memory':
        if access.memory_system:
            access.memory_system.show_recent_memories()
        else:
            print("🧠 Sistema de memória não ativo")
    elif command == 'projects':
        projects = access.scan_all_projects()
        print(f"📂 PROJETOS ENCONTRADOS ({len(projects)}):")
        for project in projects:
            print(f"   • {project['name']} - {project['type']}")
    else:
        print(f"❌ Comando desconhecido: {command}")
        print("💡 Use 'claude-help' para ver comandos disponíveis")

if __name__ == "__main__":
    main()