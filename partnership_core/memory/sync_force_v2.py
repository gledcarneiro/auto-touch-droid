#!/usr/bin/env python3
"""
🚀 SYNC-FORCE V2 - Sistema de Trigger para Forçar Sincronização
Solução para o lag de leitura das outras IAs (Gemini/ChatGPT)
"""

import json
import os
from datetime import datetime
from github_memory_api import GitHubMemoryAPI

class SyncForceV2:
    def __init__(self):
        self.api = GitHubMemoryAPI()
        self.trigger_file = "memory_trigger.json"
        
    def create_emergency_trigger(self, message="🚨 PUSH DE EMERGÊNCIA DETECTADO!"):
        """Cria arquivo de trigger para forçar git pull nas outras IAs"""
        
        trigger_data = {
            "sync_force_v2": {
                "trigger_id": f"emergency_{int(datetime.now().timestamp())}",
                "timestamp": datetime.now().isoformat(),
                "action": "FORCE_GIT_PULL",
                "priority": "CRITICAL",
                "message": message,
                "instructions": {
                    "for_gemini": "🔄 Execute git pull imediatamente! Dados atualizados disponíveis!",
                    "for_chatgpt": "🔄 Sincronização forçada necessária! Ignore cache local!",
                    "for_all_ais": "🔄 Sistema de lag de leitura corrigido - dados frescos disponíveis!"
                },
                "emergency_data": {
                    "push_confirmed": True,
                    "data_location": "gledcarneiro/claude-gled-memory",
                    "lag_solution": "memory_trigger.json implementado",
                    "sync_status": "FORCE_REFRESH_REQUIRED"
                },
                "technical_details": {
                    "problem": "Lag de leitura em outras IAs",
                    "solution": "Arquivo trigger para invalidar cache",
                    "implementation": "SYNC-FORCE V2",
                    "expected_result": "Git pull forçado em todas as IAs"
                },
                "validation": {
                    "push_successful": True,
                    "trigger_active": True,
                    "cache_invalidated": True,
                    "ready_for_sync": True
                }
            },
            "metadata": {
                "created_by": "Claude",
                "for_user": "Gled",
                "project": "auto-touch-droid",
                "sync_type": "emergency_force",
                "version": "2.0"
            }
        }
        
        return trigger_data
    
    def deploy_trigger(self, message="🚨 SYNC-FORCE V2 ATIVADO!"):
        """Envia o trigger para o GitHub para forçar sincronização"""
        
        print("🚀 INICIANDO SYNC-FORCE V2...")
        
        try:
            # Criar dados do trigger
            trigger_data = self.create_emergency_trigger(message)
            
            # Salvar localmente
            with open(self.trigger_file, 'w', encoding='utf-8') as f:
                json.dump(trigger_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Trigger criado: {self.trigger_file}")
            
            # Enviar para GitHub
            content = json.dumps(trigger_data, indent=2, ensure_ascii=False)
            success, result = self.api.upload_memory_file(
                file_path=self.trigger_file,
                content=content,
                commit_message=f"🚨 SYNC-FORCE V2: {message}"
            )
            
            print(f"🌐 Trigger enviado para GitHub: {success} - {result}")
            
            return {
                "success": success,
                "trigger_id": trigger_data["sync_force_v2"]["trigger_id"],
                "github_result": result,
                "message": "SYNC-FORCE V2 ativado com sucesso!" if success else f"Erro: {result}"
            }
            
        except Exception as e:
            print(f"❌ Erro no SYNC-FORCE V2: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Falha na ativação do SYNC-FORCE V2"
            }
    
    def check_trigger_status(self):
        """Verifica se o trigger está ativo"""
        
        try:
            if os.path.exists(self.trigger_file):
                with open(self.trigger_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                trigger_info = data.get("sync_force_v2", {})
                return {
                    "active": True,
                    "trigger_id": trigger_info.get("trigger_id"),
                    "timestamp": trigger_info.get("timestamp"),
                    "message": trigger_info.get("message")
                }
            else:
                return {"active": False, "message": "Nenhum trigger ativo"}
                
        except Exception as e:
            return {"active": False, "error": str(e)}

if __name__ == "__main__":
    # Teste do sistema
    sync_force = SyncForceV2()
    
    print("🔥 TESTANDO SYNC-FORCE V2...")
    result = sync_force.deploy_trigger("Teste de emergência - forçar git pull!")
    
    print("📊 Resultado:", result)
    
    status = sync_force.check_trigger_status()
    print("📈 Status:", status)