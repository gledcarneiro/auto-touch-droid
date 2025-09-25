#!/usr/bin/env python3
"""
Servidor HTTP para receber comandos do overlay React Native
e executar ações ADB no League of Kingdoms
"""

import json
import subprocess
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import sys
import os

# Adicionar o diretório atual ao path para importar módulos locais
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from action_executor import ActionExecutor
from adb_utils import ADBUtils

class OverlayRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.action_executor = ActionExecutor()
        self.adb_utils = ADBUtils()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Lidar com requisições GET"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/status':
            self.send_status_response()
        elif parsed_path.path == '/actions':
            self.send_actions_list()
        else:
            self.send_error_response(404, "Endpoint não encontrado")
    
    def do_POST(self):
        """Lidar com requisições POST"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/execute':
            self.handle_execute_action()
        elif parsed_path.path == '/detect_game':
            self.handle_detect_game()
        else:
            self.send_error_response(404, "Endpoint não encontrado")
    
    def handle_execute_action(self):
        """Executar ação solicitada pelo overlay"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            action_name = data.get('action')
            account = data.get('account', 'default')
            
            print(f"Executando ação: {action_name} para conta: {account}")
            
            # Verificar se o dispositivo está conectado
            if not self.adb_utils.is_device_connected():
                self.send_error_response(400, "Dispositivo Android não conectado")
                return
            
            # Executar ação em thread separada para não bloquear
            def execute_async():
                try:
                    result = self.action_executor.execute_action(action_name, account)
                    print(f"Ação {action_name} executada: {result}")
                except Exception as e:
                    print(f"Erro ao executar ação {action_name}: {e}")
            
            thread = threading.Thread(target=execute_async)
            thread.daemon = True
            thread.start()
            
            self.send_success_response({
                'message': f'Ação {action_name} iniciada',
                'action': action_name,
                'account': account
            })
            
        except Exception as e:
            print(f"Erro ao processar requisição: {e}")
            self.send_error_response(500, f"Erro interno: {str(e)}")
    
    def handle_detect_game(self):
        """Detectar se o League of Kingdoms está aberto"""
        try:
            # Verificar se o jogo está em primeiro plano
            game_detected = self.adb_utils.is_app_in_foreground("com.nhnent.SKLEAGUE")
            
            self.send_success_response({
                'game_detected': game_detected,
                'app_package': 'com.nhnent.SKLEAGUE'
            })
            
        except Exception as e:
            print(f"Erro ao detectar jogo: {e}")
            self.send_error_response(500, f"Erro ao detectar jogo: {str(e)}")
    
    def send_status_response(self):
        """Enviar status do servidor"""
        try:
            device_connected = self.adb_utils.is_device_connected()
            available_actions = self.action_executor.get_available_actions()
            
            status = {
                'server': 'online',
                'device_connected': device_connected,
                'available_actions': available_actions,
                'adb_version': self.adb_utils.get_adb_version()
            }
            
            self.send_success_response(status)
            
        except Exception as e:
            self.send_error_response(500, f"Erro ao obter status: {str(e)}")
    
    def send_actions_list(self):
        """Enviar lista de ações disponíveis"""
        try:
            actions = self.action_executor.get_available_actions()
            self.send_success_response({'actions': actions})
        except Exception as e:
            self.send_error_response(500, f"Erro ao obter ações: {str(e)}")
    
    def send_success_response(self, data):
        """Enviar resposta de sucesso"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response.encode('utf-8'))
    
    def send_error_response(self, code, message):
        """Enviar resposta de erro"""
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        error_response = json.dumps({
            'error': True,
            'message': message,
            'code': code
        }, ensure_ascii=False, indent=2)
        
        self.wfile.write(error_response.encode('utf-8'))
    
    def do_OPTIONS(self):
        """Lidar com requisições OPTIONS (CORS)"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Customizar log das requisições"""
        print(f"[{self.address_string()}] {format % args}")

def start_server(host='localhost', port=8080):
    """Iniciar servidor HTTP"""
    server_address = (host, port)
    httpd = HTTPServer(server_address, OverlayRequestHandler)
    
    print(f"🚀 Servidor Overlay iniciado em http://{host}:{port}")
    print("📱 Endpoints disponíveis:")
    print(f"   GET  http://{host}:{port}/status - Status do servidor")
    print(f"   GET  http://{host}:{port}/actions - Lista de ações")
    print(f"   POST http://{host}:{port}/execute - Executar ação")
    print(f"   POST http://{host}:{port}/detect_game - Detectar jogo")
    print("\n🎮 Pronto para receber comandos do overlay!")
    print("Pressione Ctrl+C para parar o servidor\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado pelo usuário")
        httpd.shutdown()

if __name__ == '__main__':
    # Verificar se ADB está disponível
    try:
        subprocess.run(['adb', 'version'], capture_output=True, check=True)
        print("✅ ADB encontrado e funcionando")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ ADB não encontrado! Instale o Android SDK Platform Tools")
        sys.exit(1)
    
    # Iniciar servidor
    start_server()