"""
Sistema de Logging Estruturado
Fornece logging consistente e configurável para todo o backend
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional

try:
    from backend.config.settings import settings
except ImportError:
    # Fallback se settings não estiver disponível
    from pathlib import Path
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    
    class FallbackSettings:
        class Logging:
            level = 'INFO'
            format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            date_format = '%Y-%m-%d %H:%M:%S'
            max_file_size = 10 * 1024 * 1024
            backup_count = 5
            console_output = True
            file_output = True
        
        class Paths:
            logs_folder = BASE_DIR / 'logs'
            
            def __init__(self):
                self.logs_folder.mkdir(parents=True, exist_ok=True)
        
        logging = Logging()
        paths = Paths()
    
    settings = FallbackSettings()


class ColoredFormatter(logging.Formatter):
    """Formatter com cores para console"""
    
    # Códigos de cor ANSI
    COLORS = {
        'DEBUG': '\033[36m',      # Ciano
        'INFO': '\033[32m',       # Verde
        'WARNING': '\033[33m',    # Amarelo
        'ERROR': '\033[31m',      # Vermelho
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Adicionar cor ao nível de log
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


class AutoTouchLogger:
    """Gerenciador de logging para o projeto"""
    
    _loggers = {}
    _initialized = False
    
    @classmethod
    def setup(cls, force_reinit: bool = False):
        """Configura o sistema de logging"""
        if cls._initialized and not force_reinit:
            return
        
        # Criar pasta de logs se não existir
        settings.paths.logs_folder.mkdir(parents=True, exist_ok=True)
        
        # Configurar logger raiz
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, settings.logging.level.upper()))
        
        # Remover handlers existentes
        root_logger.handlers.clear()
        
        # Handler para console
        if settings.logging.console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.DEBUG)
            console_formatter = ColoredFormatter(
                settings.logging.format,
                datefmt=settings.logging.date_format
            )
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)
        
        # Handler para arquivo
        if settings.logging.file_output:
            log_file = settings.paths.logs_folder / f"auto_touch_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=settings.logging.max_file_size,
                backupCount=settings.logging.backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                settings.logging.format,
                datefmt=settings.logging.date_format
            )
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)
        
        cls._initialized = True
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Obtém um logger configurado
        
        Args:
            name: Nome do logger (geralmente __name__ do módulo)
        
        Returns:
            Logger configurado
        """
        if not cls._initialized:
            cls.setup()
        
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            cls._loggers[name] = logger
        
        return cls._loggers[name]
    
    @classmethod
    def log_action_start(cls, logger: logging.Logger, action_name: str, device_id: Optional[str] = None):
        """Log padronizado para início de ação"""
        device_info = f" (Device: {device_id})" if device_id else ""
        logger.info(f"{'='*60}")
        logger.info(f"🚀 Iniciando ação: {action_name}{device_info}")
        logger.info(f"{'='*60}")
    
    @classmethod
    def log_action_end(cls, logger: logging.Logger, action_name: str, success: bool, duration: float):
        """Log padronizado para fim de ação"""
        status = "✅ SUCESSO" if success else "❌ FALHA"
        logger.info(f"{'='*60}")
        logger.info(f"{status} - Ação: {action_name}")
        logger.info(f"Duração: {duration:.2f}s")
        logger.info(f"{'='*60}")
    
    @classmethod
    def log_step(cls, logger: logging.Logger, step_name: str, step_number: int, total_steps: int):
        """Log padronizado para passos de ação"""
        logger.info(f"📍 Passo {step_number}/{total_steps}: {step_name}")
    
    @classmethod
    def log_template_found(cls, logger: logging.Logger, template_name: str, position: tuple, confidence: float = None):
        """Log padronizado para template encontrado"""
        x, y, w, h = position
        conf_info = f" (Confiança: {confidence:.2%})" if confidence else ""
        logger.info(f"✓ Template encontrado: {template_name}")
        logger.info(f"  Posição: ({x}, {y}) | Tamanho: {w}x{h}{conf_info}")
    
    @classmethod
    def log_template_not_found(cls, logger: logging.Logger, template_name: str, attempt: int, max_attempts: int):
        """Log padronizado para template não encontrado"""
        logger.warning(f"✗ Template não encontrado: {template_name} (Tentativa {attempt}/{max_attempts})")
    
    @classmethod
    def log_error(cls, logger: logging.Logger, error: Exception, context: str = ""):
        """Log padronizado para erros"""
        context_info = f" - {context}" if context else ""
        logger.error(f"❌ Erro{context_info}: {type(error).__name__}: {str(error)}")
        logger.debug("Stack trace:", exc_info=True)
    
    @classmethod
    def log_performance(cls, logger: logging.Logger, operation: str, duration: float, threshold: float = 1.0):
        """Log de performance com alerta se ultrapassar threshold"""
        if duration > threshold:
            logger.warning(f"⚠️ Performance: {operation} levou {duration:.2f}s (threshold: {threshold}s)")
        else:
            logger.debug(f"⏱️ Performance: {operation} levou {duration:.2f}s")


# Configurar logging ao importar o módulo
AutoTouchLogger.setup()


def get_logger(name: str = None) -> logging.Logger:
    """
    Função helper para obter logger
    
    Args:
        name: Nome do logger (se None, usa o nome do módulo chamador)
    
    Returns:
        Logger configurado
    
    Exemplo:
        from backend.core.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Mensagem de log")
    """
    if name is None:
        # Tentar obter o nome do módulo chamador
        import inspect
        frame = inspect.currentframe().f_back
        name = frame.f_globals.get('__name__', 'auto_touch')
    
    return AutoTouchLogger.get_logger(name)


# Criar logger padrão para o módulo
logger = get_logger(__name__)


if __name__ == '__main__':
    # Teste do sistema de logging
    test_logger = get_logger('test')
    
    test_logger.debug("Mensagem de DEBUG")
    test_logger.info("Mensagem de INFO")
    test_logger.warning("Mensagem de WARNING")
    test_logger.error("Mensagem de ERROR")
    test_logger.critical("Mensagem de CRITICAL")
    
    # Testar logs padronizados
    AutoTouchLogger.log_action_start(test_logger, "fazer_login", "DEVICE123")
    AutoTouchLogger.log_step(test_logger, "Buscar botão Google", 1, 5)
    AutoTouchLogger.log_template_found(test_logger, "01_google.png", (100, 200, 50, 30), 0.95)
    AutoTouchLogger.log_template_not_found(test_logger, "02_login.png", 1, 5)
    
    try:
        raise ValueError("Erro de teste")
    except Exception as e:
        AutoTouchLogger.log_error(test_logger, e, "Teste de erro")
    
    AutoTouchLogger.log_performance(test_logger, "Detecção de template", 0.3)
    AutoTouchLogger.log_performance(test_logger, "Operação lenta", 2.5, threshold=1.0)
    AutoTouchLogger.log_action_end(test_logger, "fazer_login", True, 15.5)
    
    print("\n✅ Teste de logging concluído!")
    print(f"📁 Logs salvos em: {settings.paths.logs_folder}")
