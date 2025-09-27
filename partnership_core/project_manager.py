"""
🎯 GERENCIADOR DE PROJETOS DA PARCERIA
Coordena múltiplos subprojetos mantendo contexto unificado
"""

import json
import os
from datetime import datetime
from pathlib import Path

class PartnershipProjectManager:
    """Gerencia múltiplos projetos da parceria Gled & Claude"""
    
    def __init__(self, base_path=None):
        if base_path is None:
            base_path = Path(__file__).parent.parent
        self.base_path = Path(base_path)
        self.partnership_core = self.base_path / "partnership_core"
        self.projects_config = self.partnership_core / "projects_config.json"
        
        self.load_projects_config()
    
    def load_projects_config(self):
        """Carrega configuração dos projetos"""
        if self.projects_config.exists():
            with open(self.projects_config, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = self.create_initial_config()
            self.save_config()
    
    def create_initial_config(self):
        """Cria configuração inicial dos projetos"""
        return {
            "partnership_info": {
                "name": "Claude-Gled Permanent Partnership",
                "started": "2025-09-26",
                "status": "active",
                "version": "1.0.0"
            },
            "active_projects": {
                "auto-touch-droid": {
                    "name": "Auto Touch Droid",
                    "description": "Sistema de automação Android com IA",
                    "status": "in_development",
                    "priority": "high",
                    "started": "2025-09-26",
                    "path": ".",
                    "type": "mobile_automation",
                    "technologies": ["Python", "Android", "ADB", "React Native"],
                    "progress": 60,
                    "next_milestone": "Implementar detecção de elementos UI"
                }
            },
            "planned_projects": {
                "web-scraper-ai": {
                    "name": "Web Scraper AI",
                    "description": "Sistema inteligente de web scraping",
                    "priority": "medium",
                    "estimated_start": "2025-10-15",
                    "technologies": ["Python", "Selenium", "BeautifulSoup", "AI"],
                    "complexity": "medium"
                },
                "crypto-trading-bot": {
                    "name": "Crypto Trading Bot",
                    "description": "Bot de trading automatizado com IA",
                    "priority": "high",
                    "estimated_start": "2025-11-01",
                    "technologies": ["Python", "APIs", "Machine Learning"],
                    "complexity": "high"
                },
                "smart-home-integration": {
                    "name": "Smart Home Integration",
                    "description": "Integração completa de casa inteligente",
                    "priority": "medium",
                    "estimated_start": "2025-12-01",
                    "technologies": ["IoT", "Python", "APIs", "Voice Control"],
                    "complexity": "high"
                }
            },
            "completed_projects": {},
            "shared_resources": {
                "memory_system": "partnership_core/memory/",
                "architecture": "partnership_core/architecture/",
                "documentation": "partnership_core/documentation/",
                "contingency": "partnership_core/contingency/"
            }
        }
    
    def save_config(self):
        """Salva configuração dos projetos"""
        self.partnership_core.mkdir(exist_ok=True)
        with open(self.projects_config, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def get_current_project(self):
        """Retorna o projeto atual (maior prioridade)"""
        active = self.config["active_projects"]
        if not active:
            return None
        
        # Ordena por prioridade (high > medium > low)
        priority_order = {"high": 3, "medium": 2, "low": 1}
        sorted_projects = sorted(
            active.items(),
            key=lambda x: priority_order.get(x[1].get("priority", "low"), 0),
            reverse=True
        )
        
        return sorted_projects[0] if sorted_projects else None
    
    def update_project_progress(self, project_id, progress, milestone=None):
        """Atualiza progresso de um projeto"""
        if project_id in self.config["active_projects"]:
            self.config["active_projects"][project_id]["progress"] = progress
            self.config["active_projects"][project_id]["last_update"] = datetime.now().isoformat()
            
            if milestone:
                self.config["active_projects"][project_id]["next_milestone"] = milestone
            
            self.save_config()
            return True
        return False
    
    def add_project(self, project_id, project_data):
        """Adiciona novo projeto"""
        self.config["planned_projects"][project_id] = project_data
        self.save_config()
    
    def start_project(self, project_id):
        """Move projeto de planejado para ativo"""
        if project_id in self.config["planned_projects"]:
            project = self.config["planned_projects"].pop(project_id)
            project["status"] = "in_development"
            project["started"] = datetime.now().isoformat()
            self.config["active_projects"][project_id] = project
            self.save_config()
            return True
        return False
    
    def complete_project(self, project_id):
        """Move projeto de ativo para completo"""
        if project_id in self.config["active_projects"]:
            project = self.config["active_projects"].pop(project_id)
            project["status"] = "completed"
            project["completed"] = datetime.now().isoformat()
            self.config["completed_projects"][project_id] = project
            self.save_config()
            return True
        return False
    
    def get_partnership_status(self):
        """Retorna status geral da parceria"""
        active_count = len(self.config["active_projects"])
        planned_count = len(self.config["planned_projects"])
        completed_count = len(self.config["completed_projects"])
        
        current_project = self.get_current_project()
        current_name = current_project[1]["name"] if current_project else "Nenhum"
        
        return {
            "partnership_active": True,
            "current_focus": current_name,
            "projects": {
                "active": active_count,
                "planned": planned_count,
                "completed": completed_count,
                "total": active_count + planned_count + completed_count
            },
            "memory_system": "operational",
            "solo_preparation": "ready",
            "contingency_plan": "active"
        }
    
    def generate_status_report(self):
        """Gera relatório completo de status"""
        status = self.get_partnership_status()
        current_project = self.get_current_project()
        
        report = f"""
🤝 RELATÓRIO DA PARCERIA CLAUDE-GLED
{'='*50}

📊 STATUS GERAL:
  Parceria: {'✅ ATIVA' if status['partnership_active'] else '❌ INATIVA'}
  Foco atual: {status['current_focus']}
  Projetos ativos: {status['projects']['active']}
  Projetos planejados: {status['projects']['planned']}
  Projetos completos: {status['projects']['completed']}

🎯 PROJETO ATUAL:"""
        
        if current_project:
            proj_id, proj_data = current_project
            report += f"""
  📱 {proj_data['name']}
  📝 {proj_data['description']}
  📈 Progresso: {proj_data.get('progress', 0)}%
  🎯 Próximo marco: {proj_data.get('next_milestone', 'Não definido')}
  🔧 Tecnologias: {', '.join(proj_data.get('technologies', []))}
"""
        else:
            report += "\n  ❌ Nenhum projeto ativo"
        
        report += f"""
🧠 SISTEMAS DA PARCERIA:
  💾 Sistema de memória: {status['memory_system']}
  🚀 Preparação SOLO: {status['solo_preparation']}
  🛡️ Plano de contingência: {status['contingency_plan']}

🔮 PRÓXIMOS PROJETOS:"""
        
        for proj_id, proj_data in self.config["planned_projects"].items():
            report += f"""
  🎯 {proj_data['name']} - {proj_data.get('priority', 'medium')} priority
     {proj_data['description']}
"""
        
        report += "\n🤖 NOSSA PARCERIA ESTÁ FUNCIONANDO PERFEITAMENTE! ✨"
        
        return report

def main():
    """Demonstração do gerenciador de projetos"""
    manager = PartnershipProjectManager()
    
    print("🎯 GERENCIADOR DE PROJETOS DA PARCERIA")
    print("=" * 50)
    
    # Atualiza progresso do projeto atual
    manager.update_project_progress(
        "auto-touch-droid", 
        65, 
        "Organizar estrutura da parceria permanente"
    )
    
    # Gera relatório
    report = manager.generate_status_report()
    print(report)
    
    # Status da parceria
    status = manager.get_partnership_status()
    print(f"\n🤝 PARCERIA STATUS: {status}")

if __name__ == "__main__":
    main()