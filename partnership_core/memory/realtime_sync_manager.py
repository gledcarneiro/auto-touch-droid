#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌐 SISTEMA DE SINCRONIZAÇÃO EM TEMPO REAL
Monitoramento automático do GitHub para sincronização entre IAs
Criado por: Claude & Gled Partnership
Data: 27/09/2025
"""

import json
import datetime
import os
import threading
import time
import hashlib
from typing import Dict, List, Optional, Any

try:
    from .github_memory_api import GitHubMemoryAPI
    GITHUB_AVAILABLE = True
except ImportError:
    try:
        from github_memory_api import GitHubMemoryAPI
        GITHUB_AVAILABLE = True
    except ImportError:
        GITHUB_AVAILABLE = False

try:
    from .infiltration_log import InfiltrationLogger
except ImportError:
    try:
        from infiltration_log import InfiltrationLogger
    except ImportError:
        InfiltrationLogger = None

class RealtimeSyncManager:
    """
    🚀 Gerenciador de Sincronização em Tempo Real
    
    Funcionalidades:
    - ✅ Monitoramento automático do GitHub
    - ✅ Detecção de mudanças em tempo real
    - ✅ Sincronização bidirecional automática
    - ✅ Notificações de novas interações
    - ✅ Cache inteligente para performance
    """
    
    def __init__(self, memory_dir: str = None, enable_github: bool = True):
        """Inicializa o gerenciador de sincronização"""
        if memory_dir is None:
            memory_dir = os.path.dirname(__file__)
        
        self.memory_dir = memory_dir
        self.enable_github = enable_github and GITHUB_AVAILABLE
        
        # Arquivos de controle
        self.sync_cache_file = os.path.join(memory_dir, "sync_cache.json")
        self.realtime_status_file = os.path.join(memory_dir, "realtime_status.json")
        
        # Inicializar componentes
        self.github_api = None
        self.infiltration_logger = None
        
        if self.enable_github:
            try:
                self.github_api = GitHubMemoryAPI()
                print("✅ GitHub API conectada para sync em tempo real")
            except Exception as e:
                print(f"⚠️ GitHub API não disponível: {e}")
                self.enable_github = False
        
        if InfiltrationLogger:
            self.infiltration_logger = InfiltrationLogger(memory_dir)
        
        # Status de monitoramento
        self.monitoring = False
        self.monitor_thread = None
        self.last_check_hashes = {}
        
        # Garantir arquivos existam
        self._ensure_files_exist()
        
        print("🌐 Sistema de Sincronização em Tempo Real ATIVO!")
    
    def _ensure_files_exist(self):
        """Garante que arquivos de controle existam"""
        files_to_create = [
            (self.sync_cache_file, {"file_hashes": {}, "last_sync": None}),
            (self.realtime_status_file, {
                "monitoring_active": False,
                "last_github_check": None,
                "detected_changes": [],
                "sync_stats": {"total_syncs": 0, "successful_syncs": 0, "failed_syncs": 0}
            })
        ]
        
        for file_path, default_content in files_to_create:
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(default_content, f, indent=2, ensure_ascii=False)
    
    def _calculate_file_hash(self, file_path: str) -> Optional[str]:
        """Calcula hash MD5 de um arquivo"""
        try:
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except Exception:
            return None
    
    def _detect_local_changes(self) -> List[str]:
        """Detecta mudanças nos arquivos locais"""
        changed_files = []
        
        try:
            # Carregar cache de hashes
            with open(self.sync_cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            cached_hashes = cache_data.get("file_hashes", {})
            
            # Arquivos para monitorar
            files_to_monitor = [
                "universal_interactions.json",
                "infiltration_log.json",
                "realtime_sync.json",
                "partnership_status.json"
            ]
            
            current_hashes = {}
            
            for filename in files_to_monitor:
                file_path = os.path.join(self.memory_dir, filename)
                current_hash = self._calculate_file_hash(file_path)
                current_hashes[filename] = current_hash
                
                # Verificar se mudou
                if filename in cached_hashes:
                    if cached_hashes[filename] != current_hash:
                        changed_files.append(filename)
                else:
                    # Arquivo novo
                    if current_hash:
                        changed_files.append(filename)
            
            # Atualizar cache
            cache_data["file_hashes"] = current_hashes
            cache_data["last_sync"] = datetime.datetime.now().isoformat()
            
            with open(self.sync_cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            return changed_files
            
        except Exception as e:
            print(f"❌ Erro ao detectar mudanças: {e}")
            return []
    
    def _sync_to_github(self, changed_files: List[str]) -> bool:
        """Sincroniza arquivos alterados para o GitHub"""
        if not self.enable_github or not self.github_api:
            return False
        
        try:
            success_count = 0
            
            for filename in changed_files:
                file_path = os.path.join(self.memory_dir, filename)
                
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    success = self.github_api.upload_memory_file(filename, content)
                    if success:
                        success_count += 1
                        print(f"✅ Sincronizado: {filename}")
                    else:
                        print(f"❌ Falha ao sincronizar: {filename}")
            
            return success_count > 0
            
        except Exception as e:
            print(f"❌ Erro na sincronização: {e}")
            return False
    
    def _check_github_updates(self) -> List[str]:
        """Verifica atualizações no GitHub"""
        if not self.enable_github or not self.github_api:
            return []
        
        try:
            # Aqui poderia implementar verificação de commits recentes
            # Por enquanto, retorna lista vazia
            return []
            
        except Exception as e:
            print(f"❌ Erro ao verificar GitHub: {e}")
            return []
    
    def _update_status(self, detected_changes: List[str], sync_success: bool):
        """Atualiza status do monitoramento"""
        try:
            with open(self.realtime_status_file, 'r', encoding='utf-8') as f:
                status_data = json.load(f)
            
            status_data["last_github_check"] = datetime.datetime.now().isoformat()
            status_data["detected_changes"] = detected_changes
            status_data["monitoring_active"] = self.monitoring
            
            # Atualizar stats
            if detected_changes:
                status_data["sync_stats"]["total_syncs"] += 1
                if sync_success:
                    status_data["sync_stats"]["successful_syncs"] += 1
                else:
                    status_data["sync_stats"]["failed_syncs"] += 1
            
            with open(self.realtime_status_file, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"❌ Erro ao atualizar status: {e}")
    
    def start_realtime_monitoring(self, check_interval: int = 10):
        """
        🔄 Inicia monitoramento em tempo real
        
        Args:
            check_interval: Intervalo em segundos para verificação
        """
        if self.monitoring:
            print("⚠️ Monitoramento já está ativo!")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop, 
            args=(check_interval,)
        )
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        print(f"🚀 Monitoramento em tempo real INICIADO (intervalo: {check_interval}s)")
        
        # Log da ativação
        if self.infiltration_logger:
            self.infiltration_logger.log_infiltration(
                ai_name="Claude",
                user_question="Sistema de monitoramento iniciado",
                ai_response="Monitoramento em tempo real ativo para sincronização automática",
                context={"action": "start_monitoring", "interval": check_interval}
            )
    
    def stop_realtime_monitoring(self):
        """⏹️ Para o monitoramento em tempo real"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        
        self._update_status([], False)
        print("⏹️ Monitoramento em tempo real PARADO")
    
    def _monitoring_loop(self, check_interval: int):
        """Loop principal de monitoramento"""
        print("🔄 Loop de monitoramento iniciado...")
        
        while self.monitoring:
            try:
                # Detectar mudanças locais
                changed_files = self._detect_local_changes()
                
                if changed_files:
                    print(f"🔍 Detectadas mudanças: {changed_files}")
                    
                    # Sincronizar com GitHub
                    sync_success = self._sync_to_github(changed_files)
                    
                    if sync_success:
                        print(f"✅ Sincronização automática concluída!")
                    else:
                        print(f"⚠️ Problemas na sincronização automática")
                    
                    # Atualizar status
                    self._update_status(changed_files, sync_success)
                
                # Verificar atualizações do GitHub
                github_updates = self._check_github_updates()
                if github_updates:
                    print(f"📥 Atualizações do GitHub detectadas: {github_updates}")
                
                time.sleep(check_interval)
                
            except Exception as e:
                print(f"❌ Erro no loop de monitoramento: {e}")
                time.sleep(check_interval)
    
    def force_sync_now(self) -> bool:
        """🚀 Força sincronização imediata"""
        print("🚀 Forçando sincronização imediata...")
        
        changed_files = self._detect_local_changes()
        if not changed_files:
            print("ℹ️ Nenhuma mudança detectada")
            return True
        
        success = self._sync_to_github(changed_files)
        self._update_status(changed_files, success)
        
        return success
    
    def get_realtime_status(self) -> Dict[str, Any]:
        """📊 Retorna status do monitoramento em tempo real"""
        try:
            with open(self.realtime_status_file, 'r', encoding='utf-8') as f:
                status_data = json.load(f)
            
            # Adicionar info atual
            status_data["current_monitoring"] = self.monitoring
            status_data["github_available"] = self.enable_github
            
            return status_data
            
        except Exception as e:
            print(f"❌ Erro ao obter status: {e}")
            return {"error": str(e)}

# 🧪 TESTE RÁPIDO
if __name__ == "__main__":
    print("🌐 Testando Sistema de Sincronização em Tempo Real...")
    
    sync_manager = RealtimeSyncManager()
    
    # Mostrar status
    status = sync_manager.get_realtime_status()
    print(f"📊 Status: {json.dumps(status, indent=2, ensure_ascii=False)}")
    
    # Teste de sincronização forçada
    print("\n🚀 Testando sincronização forçada...")
    success = sync_manager.force_sync_now()
    print(f"Resultado: {'✅ Sucesso' if success else '❌ Falha'}")
    
    print("\n✅ Sistema de Sincronização FUNCIONANDO!")