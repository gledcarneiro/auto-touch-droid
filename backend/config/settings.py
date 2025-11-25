"""
Sistema de Configuração Centralizado
Gerencia todas as configurações do backend com suporte a variáveis de ambiente
"""
import os
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent.parent


@dataclass
class ADBSettings:
    """Configurações relacionadas ao ADB"""
    adb_path: str = field(default_factory=lambda: os.getenv('ADB_PATH', 'adb'))
    default_device_id: Optional[str] = field(default_factory=lambda: os.getenv('DEFAULT_DEVICE_ID'))
    connection_timeout: int = field(default_factory=lambda: int(os.getenv('ADB_TIMEOUT', '30')))
    screenshot_format: str = 'png'
    screenshot_quality: int = 100


@dataclass
class DetectionSettings:
    """Configurações de detecção de imagem"""
    threshold: float = field(default_factory=lambda: float(os.getenv('DETECTION_THRESHOLD', '0.8')))
    max_attempts: int = field(default_factory=lambda: int(os.getenv('MAX_ATTEMPTS', '5')))
    attempt_delay: float = field(default_factory=lambda: float(os.getenv('ATTEMPT_DELAY', '1.0')))
    initial_delay: float = field(default_factory=lambda: float(os.getenv('INITIAL_DELAY', '2.0')))
    use_grayscale: bool = True
    template_cache_size: int = 100
    enable_multiscale: bool = False
    scales: list = field(default_factory=lambda: [0.8, 1.0, 1.2])


@dataclass
class PathSettings:
    """Configurações de caminhos"""
    base_dir: Path = BASE_DIR
    backend_dir: Path = field(default_factory=lambda: BASE_DIR / 'backend')
    actions_folder: Path = field(default_factory=lambda: BASE_DIR / 'backend' / 'actions' / 'templates')
    screenshots_folder: Path = field(default_factory=lambda: BASE_DIR / 'temp_screenshots')
    logs_folder: Path = field(default_factory=lambda: BASE_DIR / 'logs')
    
    def __post_init__(self):
        """Cria pastas necessárias se não existirem"""
        self.screenshots_folder.mkdir(parents=True, exist_ok=True)
        self.logs_folder.mkdir(parents=True, exist_ok=True)


@dataclass
class LoggingSettings:
    """Configurações de logging"""
    level: str = field(default_factory=lambda: os.getenv('LOG_LEVEL', 'INFO'))
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format: str = '%Y-%m-%d %H:%M:%S'
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    console_output: bool = True
    file_output: bool = True


@dataclass
class PerformanceSettings:
    """Configurações de performance"""
    enable_cache: bool = True
    cache_duration: float = 1.0  # segundos
    max_parallel_workers: int = field(default_factory=lambda: int(os.getenv('MAX_WORKERS', '3')))
    screenshot_cache_enabled: bool = True
    template_cache_enabled: bool = True


@dataclass
class ActionSettings:
    """Configurações de execução de ações"""
    default_click_delay: float = 0.5
    default_scroll_duration: int = 500
    enable_action_logging: bool = True
    enable_screenshots_on_error: bool = True
    retry_on_failure: bool = True
    max_retries: int = 3


@dataclass
class Settings:
    """Configurações principais do sistema"""
    adb: ADBSettings = field(default_factory=ADBSettings)
    detection: DetectionSettings = field(default_factory=DetectionSettings)
    paths: PathSettings = field(default_factory=PathSettings)
    logging: LoggingSettings = field(default_factory=LoggingSettings)
    performance: PerformanceSettings = field(default_factory=PerformanceSettings)
    actions: ActionSettings = field(default_factory=ActionSettings)
    
    # Configurações gerais
    debug_mode: bool = field(default_factory=lambda: os.getenv('DEBUG', 'False').lower() == 'true')
    environment: str = field(default_factory=lambda: os.getenv('ENVIRONMENT', 'development'))
    
    @classmethod
    def load_from_env(cls):
        """Carrega configurações de variáveis de ambiente"""
        return cls()
    
    def validate(self) -> bool:
        """Valida configurações"""
        errors = []
        
        # Validar threshold
        if not 0.0 <= self.detection.threshold <= 1.0:
            errors.append("detection.threshold deve estar entre 0.0 e 1.0")
        
        # Validar max_attempts
        if self.detection.max_attempts < 1:
            errors.append("detection.max_attempts deve ser >= 1")
        
        # Validar delays
        if self.detection.attempt_delay < 0:
            errors.append("detection.attempt_delay deve ser >= 0")
        
        if self.detection.initial_delay < 0:
            errors.append("detection.initial_delay deve ser >= 0")
        
        # Validar workers
        if self.performance.max_parallel_workers < 1:
            errors.append("performance.max_parallel_workers deve ser >= 1")
        
        if errors:
            raise ValueError(f"Erros de validação: {', '.join(errors)}")
        
        return True
    
    def get_action_path(self, action_name: str) -> Path:
        """Retorna o caminho completo para uma ação"""
        return self.paths.actions_folder / action_name
    
    def get_template_path(self, action_name: str, template_file: str) -> Path:
        """Retorna o caminho completo para um template"""
        return self.get_action_path(action_name) / template_file
    
    def get_sequence_path(self, action_name: str) -> Path:
        """Retorna o caminho para o arquivo sequence.json de uma ação"""
        return self.get_action_path(action_name) / 'sequence.json'
    
    def print_config(self):
        """Imprime configurações atuais (útil para debug)"""
        print("=" * 60)
        print("CONFIGURAÇÕES DO SISTEMA")
        print("=" * 60)
        print(f"Ambiente: {self.environment}")
        print(f"Debug Mode: {self.debug_mode}")
        print()
        print("ADB:")
        print(f"  - Path: {self.adb.adb_path}")
        print(f"  - Device ID: {self.adb.default_device_id or 'Auto-detect'}")
        print(f"  - Timeout: {self.adb.connection_timeout}s")
        print()
        print("Detecção:")
        print(f"  - Threshold: {self.detection.threshold}")
        print(f"  - Max Attempts: {self.detection.max_attempts}")
        print(f"  - Attempt Delay: {self.detection.attempt_delay}s")
        print(f"  - Template Cache: {self.detection.template_cache_size}")
        print()
        print("Caminhos:")
        print(f"  - Base: {self.paths.base_dir}")
        print(f"  - Actions: {self.paths.actions_folder}")
        print(f"  - Screenshots: {self.paths.screenshots_folder}")
        print(f"  - Logs: {self.paths.logs_folder}")
        print()
        print("Performance:")
        print(f"  - Cache Enabled: {self.performance.enable_cache}")
        print(f"  - Max Workers: {self.performance.max_parallel_workers}")
        print(f"  - Screenshot Cache: {self.performance.screenshot_cache_enabled}")
        print("=" * 60)


# Instância global de configurações
settings = Settings.load_from_env()

# Validar configurações ao carregar
try:
    settings.validate()
except ValueError as e:
    print(f"⚠️ Aviso: {e}")


if __name__ == '__main__':
    # Teste de configurações
    settings.print_config()
