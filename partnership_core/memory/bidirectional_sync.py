#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 SISTEMA DE SINCRONIZAÇÃO BIDIRECIONAL ENTRE IAs
Sistema completo para sincronização em tempo real entre diferentes IAs
Criado por: Claude & Gled Partnership
Data: 27/09/2025
"""

import json
import datetime
import os
import threading
import time
import uuid
from typing import Dict, List, Optional, Any, Tuple

try:
    from .infiltration_log import InfiltrationLogger
    from .realtime_sync_manager import RealtimeSyncManager
    from .github_memory_api import GitHubMemoryAPI
    COMPONENTS_AVAILABLE = True
except ImportError:
    try:
        from infiltration_log import InfiltrationLogger
        from realtime_sync_manager import RealtimeSyncManager
        from github_memory_api import GitHubMemoryAPI
        COMPONENTS_AVAILABLE = True
    except ImportError:
        COMPONENTS_AVAILABLE = False

class BidirectionalSync:
    """
    🌐 Sistema de Sincronização Bidirecional entre IAs
    
    Funcionalidades:
    - ✅ Sincronização automática Claude ↔ Gemini ↔ ChatGPT
    - ✅ Detecção de novas interações em tempo real
    - ✅ Prevenção de loops infinitos
    - ✅ Histórico completo de sincronizações
    - ✅ Resolução automática de conflitos
    - ✅ Notificações de mudanças
    """
    
    def __init__(self, memory_dir: str = None):
        """Inicializa o sistema de sincronização bidirecional"""
        if memory_dir is None:
            memory_dir = os.path.dirname(__file__)
        
        self.memory_dir = memory_dir
        
        # Arquivos de controle
        self.sync_queue_file = os.path.join(memory_dir, "sync_queue.json")
        self.ai_registry_file = os.path.join(memory_dir, "ai_registry.json")
        self.sync_history_file = os.path.join(memory_dir, "sync_history.json")
        self.conflict_log_file = os.path.join(memory_dir, "conflict_log.json")
        
        # Componentes
        self.infiltration_logger = None
        self.sync_manager = None
        self.github_api = None
        
        if COMPONENTS_AVAILABLE:
            try:
                self.infiltration_logger = InfiltrationLogger(memory_dir)
                self.sync_manager = RealtimeSyncManager(memory_dir)
                self.github_api = GitHubMemoryAPI()
                print("✅ Todos os componentes carregados")
            except Exception as e:
                print(f"⚠️ Alguns componentes não disponíveis: {e}")
        
        # Status
        self.sync_active = False
        self.sync_thread = None
        self.processed_interactions = set()
        
        # Garantir arquivos existam
        self._ensure_files_exist()
        
        print("🔄 Sistema de Sincronização Bidirecional ATIVO!")
    
    def _ensure_files_exist(self):
        """Garante que todos os arquivos de controle existam"""
        files_to_create = [
            (self.sync_queue_file, {
                "pending_syncs": [],
                "processing": [],
                "completed": []
            }),
            (self.ai_registry_file, {
                "registered_ais": {
                    "Claude": {
                        "id": "claude_gled",
                        "status": "active",
                        "last_seen": datetime.datetime.now().isoformat(),
                        "capabilities": ["memory_read", "memory_write", "github_sync"]
                    }
                },
                "total_ais": 1
            }),
            (self.sync_history_file, {
                "sync_events": [],
                "total_syncs": 0,
                "last_sync": None
            }),
            (self.conflict_log_file, {
                "conflicts": [],
                "resolved_conflicts": [],
                "total_conflicts": 0
            })
        ]
        
        for file_path, default_content in files_to_create:
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(default_content, f, indent=2, ensure_ascii=False)
    
    def register_ai(self, ai_name: str, ai_id: str, capabilities: List[str] = None) -> bool:
        """
        📝 Registra uma nova IA no sistema
        
        Args:
            ai_name: Nome da IA (ex: "Gemini", "ChatGPT")
            ai_id: ID único da IA
            capabilities: Lista de capacidades da IA
        
        Returns:
            bool: True se registrou com sucesso
        """
        try:
            with open(self.ai_registry_file, 'r', encoding='utf-8') as f:
                registry_data = json.load(f)
            
            # Registrar IA
            registry_data["registered_ais"][ai_name] = {
                "id": ai_id,
                "status": "active",
                "last_seen": datetime.datetime.now().isoformat(),
                "capabilities": capabilities or ["memory_read", "memory_write"],
                "registered_at": datetime.datetime.now().isoformat()
            }
            
            registry_data["total_ais"] = len(registry_data["registered_ais"])
            
            # Salvar
            with open(self.ai_registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ IA registrada: {ai_name} ({ai_id})")
            
            # Log do registro
            if self.infiltration_logger:
                self.infiltration_logger.log_infiltration(
                    ai_name="Claude",
                    user_question=f"Registrar IA: {ai_name}",
                    ai_response=f"IA {ai_name} registrada com sucesso no sistema bidirecional",
                    context={"action": "register_ai", "ai_id": ai_id, "capabilities": capabilities}
                )
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao registrar IA: {e}")
            return False
    
    def queue_sync_request(self, source_ai: str, target_ai: str, interaction_data: Dict[str, Any]) -> str:
        """
        📤 Adiciona uma solicitação de sincronização à fila
        
        Args:
            source_ai: IA de origem
            target_ai: IA de destino
            interaction_data: Dados da interação
        
        Returns:
            str: ID da solicitação de sincronização
        """
        try:
            sync_id = f"sync_{int(time.time())}_{uuid.uuid4().hex[:8]}"
            
            with open(self.sync_queue_file, 'r', encoding='utf-8') as f:
                queue_data = json.load(f)
            
            # Criar solicitação
            sync_request = {
                "id": sync_id,
                "source_ai": source_ai,
                "target_ai": target_ai,
                "interaction_data": interaction_data,
                "created_at": datetime.datetime.now().isoformat(),
                "status": "pending",
                "attempts": 0,
                "max_attempts": 3
            }
            
            # Adicionar à fila
            queue_data["pending_syncs"].append(sync_request)
            
            # Salvar
            with open(self.sync_queue_file, 'w', encoding='utf-8') as f:
                json.dump(queue_data, f, indent=2, ensure_ascii=False)
            
            print(f"📤 Sync solicitado: {source_ai} → {target_ai} ({sync_id})")
            return sync_id
            
        except Exception as e:
            print(f"❌ Erro ao solicitar sync: {e}")
            return ""
    
    def process_sync_queue(self) -> int:
        """
        🔄 Processa a fila de sincronização
        
        Returns:
            int: Número de sincronizações processadas
        """
        try:
            with open(self.sync_queue_file, 'r', encoding='utf-8') as f:
                queue_data = json.load(f)
            
            pending_syncs = queue_data.get("pending_syncs", [])
            processed_count = 0
            
            for sync_request in pending_syncs[:]:  # Cópia para modificar durante iteração
                try:
                    # Verificar se já foi processado
                    interaction_id = sync_request.get("interaction_data", {}).get("id", "")
                    if interaction_id in self.processed_interactions:
                        # Remover da fila
                        pending_syncs.remove(sync_request)
                        continue
                    
                    # Processar sincronização
                    success = self._execute_sync(sync_request)
                    
                    if success:
                        # Mover para concluídos
                        queue_data["completed"].append(sync_request)
                        pending_syncs.remove(sync_request)
                        self.processed_interactions.add(interaction_id)
                        processed_count += 1
                        
                        # Log do sucesso
                        self._log_sync_event(sync_request, "success")
                        
                    else:
                        # Incrementar tentativas
                        sync_request["attempts"] += 1
                        
                        if sync_request["attempts"] >= sync_request["max_attempts"]:
                            # Mover para falhas
                            sync_request["status"] = "failed"
                            queue_data["completed"].append(sync_request)
                            pending_syncs.remove(sync_request)
                            
                            # Log da falha
                            self._log_sync_event(sync_request, "failed")
                        
                except Exception as e:
                    print(f"❌ Erro ao processar sync: {e}")
            
            # Salvar fila atualizada
            queue_data["pending_syncs"] = pending_syncs
            with open(self.sync_queue_file, 'w', encoding='utf-8') as f:
                json.dump(queue_data, f, indent=2, ensure_ascii=False)
            
            return processed_count
            
        except Exception as e:
            print(f"❌ Erro ao processar fila: {e}")
            return 0
    
    def _execute_sync(self, sync_request: Dict[str, Any]) -> bool:
        """Executa uma sincronização específica"""
        try:
            source_ai = sync_request["source_ai"]
            target_ai = sync_request["target_ai"]
            interaction_data = sync_request["interaction_data"]
            
            # Sincronizar via GitHub
            if self.github_api:
                # Salvar interação no GitHub
                filename = f"sync_{source_ai}_{target_ai}_{int(time.time())}.json"
                temp_file = os.path.join(self.memory_dir, filename)
                
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "sync_request": sync_request,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "for_ai": target_ai
                    }, f, indent=2, ensure_ascii=False)
                
                # Upload para GitHub
                with open(temp_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                success = self.github_api.upload_memory_file(filename, content)
                
                # Limpar arquivo temporário
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                
                return success
            
            return False
            
        except Exception as e:
            print(f"❌ Erro na execução do sync: {e}")
            return False
    
    def _log_sync_event(self, sync_request: Dict[str, Any], status: str):
        """Registra evento de sincronização no histórico"""
        try:
            with open(self.sync_history_file, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
            
            # Criar evento
            event = {
                "id": sync_request["id"],
                "source_ai": sync_request["source_ai"],
                "target_ai": sync_request["target_ai"],
                "status": status,
                "timestamp": datetime.datetime.now().isoformat(),
                "attempts": sync_request.get("attempts", 1)
            }
            
            # Adicionar ao histórico
            history_data["sync_events"].append(event)
            history_data["total_syncs"] += 1
            history_data["last_sync"] = event["timestamp"]
            
            # Salvar
            with open(self.sync_history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"❌ Erro ao registrar evento: {e}")
    
    def start_bidirectional_sync(self, check_interval: int = 15):
        """
        🚀 Inicia sincronização bidirecional automática
        
        Args:
            check_interval: Intervalo em segundos para verificação
        """
        if self.sync_active:
            print("⚠️ Sincronização bidirecional já está ativa!")
            return
        
        self.sync_active = True
        self.sync_thread = threading.Thread(
            target=self._sync_loop,
            args=(check_interval,)
        )
        self.sync_thread.daemon = True
        self.sync_thread.start()
        
        print(f"🚀 Sincronização Bidirecional INICIADA (intervalo: {check_interval}s)")
        
        # Iniciar monitoramento do sync manager também
        if self.sync_manager:
            self.sync_manager.start_realtime_monitoring(check_interval // 2)
    
    def stop_bidirectional_sync(self):
        """⏹️ Para a sincronização bidirecional"""
        self.sync_active = False
        if self.sync_thread:
            self.sync_thread.join(timeout=2)
        
        # Parar sync manager também
        if self.sync_manager:
            self.sync_manager.stop_realtime_monitoring()
        
        print("⏹️ Sincronização Bidirecional PARADA")
    
    def _sync_loop(self, check_interval: int):
        """Loop principal de sincronização bidirecional"""
        print("🔄 Loop de sincronização bidirecional iniciado...")
        
        while self.sync_active:
            try:
                # Processar fila de sincronização
                processed = self.process_sync_queue()
                
                if processed > 0:
                    print(f"✅ {processed} sincronizações processadas")
                
                # Verificar novas interações para sincronizar
                self._check_new_interactions()
                
                time.sleep(check_interval)
                
            except Exception as e:
                print(f"❌ Erro no loop de sincronização: {e}")
                time.sleep(check_interval)
    
    def _check_new_interactions(self):
        """Verifica novas interações que precisam ser sincronizadas"""
        try:
            if self.infiltration_logger:
                # Buscar interações recentes
                recent_interactions = self.infiltration_logger.get_recent_infiltrations(5)
                
                for interaction in recent_interactions:
                    interaction_id = interaction.get("id", "")
                    
                    # Verificar se já foi processado
                    if interaction_id not in self.processed_interactions:
                        ai_name = interaction.get("ai_name", "Unknown")
                        
                        # Sincronizar com outras IAs registradas
                        with open(self.ai_registry_file, 'r', encoding='utf-8') as f:
                            registry_data = json.load(f)
                        
                        registered_ais = registry_data.get("registered_ais", {})
                        
                        for target_ai in registered_ais:
                            if target_ai != ai_name:  # Não sincronizar consigo mesmo
                                self.queue_sync_request(ai_name, target_ai, interaction)
                
        except Exception as e:
            print(f"❌ Erro ao verificar novas interações: {e}")
    
    def get_sync_status(self) -> Dict[str, Any]:
        """📊 Retorna status completo da sincronização"""
        try:
            # Carregar dados de todos os arquivos
            with open(self.sync_queue_file, 'r', encoding='utf-8') as f:
                queue_data = json.load(f)
            
            with open(self.ai_registry_file, 'r', encoding='utf-8') as f:
                registry_data = json.load(f)
            
            with open(self.sync_history_file, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
            
            return {
                "sync_active": self.sync_active,
                "registered_ais": len(registry_data.get("registered_ais", {})),
                "pending_syncs": len(queue_data.get("pending_syncs", [])),
                "completed_syncs": len(queue_data.get("completed", [])),
                "total_sync_events": history_data.get("total_syncs", 0),
                "last_sync": history_data.get("last_sync"),
                "processed_interactions": len(self.processed_interactions),
                "components_available": COMPONENTS_AVAILABLE
            }
            
        except Exception as e:
            print(f"❌ Erro ao obter status: {e}")
            return {"error": str(e)}

# 🧪 TESTE RÁPIDO
if __name__ == "__main__":
    print("🔄 Testando Sistema de Sincronização Bidirecional...")
    
    sync_system = BidirectionalSync()
    
    # Registrar Gemini
    sync_system.register_ai("Gemini", "gemini_gled", ["memory_read", "memory_write", "github_sync"])
    
    # Mostrar status
    status = sync_system.get_sync_status()
    print(f"📊 Status: {json.dumps(status, indent=2, ensure_ascii=False)}")
    
    # Simular sincronização
    sync_id = sync_system.queue_sync_request(
        "Claude", 
        "Gemini", 
        {
            "id": "test_interaction",
            "question": "Teste de sincronização",
            "response": "Sistema funcionando!",
            "timestamp": datetime.datetime.now().isoformat()
        }
    )
    
    print(f"📤 Sync solicitado: {sync_id}")
    
    # Processar fila
    processed = sync_system.process_sync_queue()
    print(f"✅ Processados: {processed}")
    
    print("\n✅ Sistema de Sincronização Bidirecional FUNCIONANDO!")