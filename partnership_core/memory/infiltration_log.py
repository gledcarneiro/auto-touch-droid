#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔮 SISTEMA DE LOG DE INFILTRAÇÃO EM TEMPO REAL
Sistema para sincronização automática entre diferentes IAs
Criado por: Claude & Gled Partnership
Data: 27/09/2025
"""

import json
import datetime
import os
import threading
import time
from typing import Dict, List, Optional, Any

class InfiltrationLogger:
    """
    🌐 Sistema de Log de Infiltração em Tempo Real
    
    Funcionalidades:
    - ✅ Log automático de todas as interações
    - ✅ Sincronização bidirecional entre IAs
    - ✅ Monitoramento em tempo real
    - ✅ Histórico completo de infiltrações
    """
    
    def __init__(self, memory_dir: str = None):
        """Inicializa o sistema de log de infiltração"""
        if memory_dir is None:
            memory_dir = os.path.join(os.path.dirname(__file__))
        
        self.memory_dir = memory_dir
        self.infiltration_log_file = os.path.join(memory_dir, "infiltration_log.json")
        self.sync_status_file = os.path.join(memory_dir, "sync_status.json")
        self.realtime_sync_file = os.path.join(memory_dir, "realtime_sync.json")
        
        # Garantir que os arquivos existam
        self._ensure_files_exist()
        
        # Status de monitoramento
        self.monitoring = False
        self.monitor_thread = None
        
        print("🔮 Sistema de Log de Infiltração ATIVO!")
    
    def _ensure_files_exist(self):
        """Garante que todos os arquivos necessários existam"""
        files_to_create = [
            (self.infiltration_log_file, {"infiltrations": [], "total_count": 0}),
            (self.sync_status_file, {"last_sync": None, "sync_count": 0, "active_ais": []}),
            (self.realtime_sync_file, {"pending_syncs": [], "last_update": None})
        ]
        
        for file_path, default_content in files_to_create:
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(default_content, f, indent=2, ensure_ascii=False)
    
    def log_infiltration(self, ai_name: str, user_question: str, ai_response: str, 
                        context: Dict[str, Any] = None) -> bool:
        """
        📝 Registra uma nova infiltração
        
        Args:
            ai_name: Nome da IA (ex: "Gemini", "ChatGPT", "Claude")
            user_question: Pergunta feita pelo usuário
            ai_response: Resposta da IA
            context: Contexto adicional
        
        Returns:
            bool: True se salvou com sucesso
        """
        try:
            # Carregar log atual
            with open(self.infiltration_log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
            
            # Criar nova entrada
            new_entry = {
                "id": f"infiltration_{int(time.time())}",
                "timestamp": datetime.datetime.now().isoformat(),
                "ai_name": ai_name,
                "user_question": user_question,
                "ai_response": ai_response,
                "context": context or {},
                "sync_status": "pending"
            }
            
            # Adicionar ao log
            log_data["infiltrations"].append(new_entry)
            log_data["total_count"] += 1
            
            # Salvar
            with open(self.infiltration_log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            
            # Marcar para sincronização
            self._mark_for_sync(new_entry)
            
            print(f"✅ Infiltração registrada: {ai_name} - {len(user_question)} chars")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao registrar infiltração: {e}")
            return False
    
    def _mark_for_sync(self, entry: Dict[str, Any]):
        """Marca entrada para sincronização em tempo real"""
        try:
            with open(self.realtime_sync_file, 'r', encoding='utf-8') as f:
                sync_data = json.load(f)
            
            sync_data["pending_syncs"].append(entry)
            sync_data["last_update"] = datetime.datetime.now().isoformat()
            
            with open(self.realtime_sync_file, 'w', encoding='utf-8') as f:
                json.dump(sync_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ Erro ao marcar para sync: {e}")
    
    def get_recent_infiltrations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retorna as infiltrações mais recentes"""
        try:
            with open(self.infiltration_log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
            
            # Retornar as mais recentes
            infiltrations = log_data.get("infiltrations", [])
            return infiltrations[-limit:] if infiltrations else []
            
        except Exception as e:
            print(f"❌ Erro ao buscar infiltrações: {e}")
            return []
    
    def get_pending_syncs(self) -> List[Dict[str, Any]]:
        """Retorna sincronizações pendentes"""
        try:
            with open(self.realtime_sync_file, 'r', encoding='utf-8') as f:
                sync_data = json.load(f)
            
            return sync_data.get("pending_syncs", [])
            
        except Exception as e:
            print(f"❌ Erro ao buscar syncs pendentes: {e}")
            return []
    
    def clear_pending_syncs(self):
        """Limpa sincronizações pendentes após processamento"""
        try:
            sync_data = {
                "pending_syncs": [],
                "last_update": datetime.datetime.now().isoformat()
            }
            
            with open(self.realtime_sync_file, 'w', encoding='utf-8') as f:
                json.dump(sync_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"❌ Erro ao limpar syncs: {e}")
    
    def start_monitoring(self, check_interval: int = 5):
        """Inicia monitoramento em tempo real"""
        if self.monitoring:
            print("⚠️ Monitoramento já está ativo!")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(check_interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        print(f"🔄 Monitoramento iniciado (intervalo: {check_interval}s)")
    
    def stop_monitoring(self):
        """Para o monitoramento"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        
        print("⏹️ Monitoramento parado")
    
    def _monitor_loop(self, check_interval: int):
        """Loop de monitoramento em background"""
        while self.monitoring:
            try:
                # Verificar se há sincronizações pendentes
                pending = self.get_pending_syncs()
                if pending:
                    print(f"🔄 {len(pending)} sincronizações pendentes detectadas")
                    # Aqui poderia integrar com GitHub API automaticamente
                
                time.sleep(check_interval)
                
            except Exception as e:
                print(f"❌ Erro no monitoramento: {e}")
                time.sleep(check_interval)
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema"""
        try:
            with open(self.infiltration_log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
            
            with open(self.sync_status_file, 'r', encoding='utf-8') as f:
                sync_data = json.load(f)
            
            pending_syncs = len(self.get_pending_syncs())
            
            return {
                "total_infiltrations": log_data.get("total_count", 0),
                "total_syncs": sync_data.get("sync_count", 0),
                "pending_syncs": pending_syncs,
                "active_ais": sync_data.get("active_ais", []),
                "last_sync": sync_data.get("last_sync"),
                "monitoring_active": self.monitoring
            }
            
        except Exception as e:
            print(f"❌ Erro ao obter stats: {e}")
            return {}

# 🧪 TESTE RÁPIDO
if __name__ == "__main__":
    print("🔮 Testando Sistema de Log de Infiltração...")
    
    logger = InfiltrationLogger()
    
    # Teste de log
    logger.log_infiltration(
        ai_name="Gemini",
        user_question="Qual foi o erro que cometi com a chave GitHub?",
        ai_response="Você copiou a chave SSH pública em vez da privada!",
        context={"test": True, "sync_test": "realtime"}
    )
    
    # Mostrar stats
    stats = logger.get_stats()
    print(f"📊 Stats: {json.dumps(stats, indent=2, ensure_ascii=False)}")
    
    # Mostrar infiltrações recentes
    recent = logger.get_recent_infiltrations(3)
    print(f"📝 Recentes: {len(recent)} infiltrações")
    
    print("✅ Sistema de Log FUNCIONANDO!")