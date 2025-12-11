from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import os
import json
import logging
from logging.handlers import RotatingFileHandler
import time
from typing import Dict, Any, List
import platform
import subprocess

# Importações de módulos locais
from ..core.adb_utils import capture_screen, simulate_touch
from ..core.action_executor import simulate_scroll
from ..core.image_detection import find_image_on_screen # Reutilizando se necessário, ou mantendo a lógica aqui

# Setup Logging
_BASE_DIR_FOR_LOG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(_BASE_DIR_FOR_LOG, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)
logger = logging.getLogger("autotouchdroid")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(fmt="%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    file_handler = RotatingFileHandler(os.path.join(LOGS_DIR, "automation.log"), maxBytes=2*1024*1024, backupCount=3, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

app = FastAPI(title="AutoTouchDroid API", description="API para processamento de automação de jogos", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # backend/
TEMPLATES_DIR = os.path.join(BASE_DIR, "actions", "templates")
SCREENSHOT_DIR = os.path.join(BASE_DIR, "temp_screenshots") # Novo diretório para screenshots temporárias
os.makedirs(SCREENSHOT_DIR, exist_ok=True) # Garante que o diretório exista

# Scroll config
UTILS_DIR = os.path.join(BASE_DIR, "utils")
SCROLL_CONFIG_PATH = os.path.join(UTILS_DIR, "scroll_config.json")
def load_scroll_config() -> Dict[str, Any]:
    try:
        with open(SCROLL_CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except Exception as e:
        logger.warning(f"Falha ao carregar scroll_config.json: {e}")
        return {"filas": {}}

SCROLL_CONFIG = load_scroll_config()

# Debug visual de clique
def _save_debug_click_overlay(img, click_x, click_y, rect=None, label=None):
    try:
        overlay = img.copy()
        if rect:
            (rx, ry, rw, rh) = rect
            cv2.rectangle(overlay, (int(rx), int(ry)), (int(rx + rw), int(ry + rh)), (0, 255, 0), 2)
        cv2.circle(overlay, (int(click_x), int(click_y)), 20, (0, 0, 255), -1)
        if label:
            cv2.putText(overlay, str(label), (int(click_x) + 30, int(click_y)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        debug_path = os.path.join(SCREENSHOT_DIR, f"debug_click_{int(time.time())}.png")
        cv2.imwrite(debug_path, overlay)
        return debug_path
    except Exception:
        return None

@app.get("/")
async def root():
    return {"status": "online", "service": "AutoTouchDroid API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/actions")
async def list_actions():
    actions = []
    try:
        for name in os.listdir(TEMPLATES_DIR):
            full = os.path.join(TEMPLATES_DIR, name)
            if os.path.isdir(full) and name != "_global":
                actions.append(name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"actions": actions}

@app.get("/devices")
async def list_devices():
    try:
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail="Falha ao executar adb devices")
        lines = result.stdout.strip().splitlines()
        devices = []
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) >= 2 and parts[1] == "device":
                devices.append(parts[0])
        return {"devices": devices}
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="ADB não encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/check_game_state")
async def check_game_state(package_name: str, device_id: str = None):
    """
    Verifica se o pacote informado está em execução e se está em primeiro plano.
    """
    def run(cmd):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode, result.stdout, result.stderr
        except FileNotFoundError:
            return 1, "", "ADB não encontrado"

    base_cmd = ["adb"]
    if device_id:
        base_cmd += ["-s", device_id]

    # Verifica se está em execução
    rc, out, _ = run(base_cmd + ["shell", "pidof", package_name])
    running = rc == 0 and out.strip() != ""

    # Verifica se está em primeiro plano (várias abordagens)
    foreground = False
    rc1, out1, _ = run(base_cmd + ["shell", "dumpsys", "window", "windows"])
    if rc1 == 0 and package_name in out1:
        foreground = True
    else:
        rc2, out2, _ = run(base_cmd + ["shell", "dumpsys", "activity", "activities"])
        if rc2 == 0 and ("mResumedActivity" in out2 and package_name in out2):
            foreground = True

    return {"running": running, "foreground": foreground}

@app.post("/debug_touch")
async def debug_touch(x: int = Form(...), y: int = Form(...), device_id: str = Form(None)):
    try:
        logger.info(f"Debug toque solicitado em ({x},{y}) no dispositivo {device_id or 'padrão'}")
        simulate_touch(x, y, device_id=device_id)
        return {"status": "ok", "message": f"Toque simulado em ({x},{y})"}
    except Exception as e:
        logger.error(f"Falha debug_touch: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug_detect")
async def debug_detect(action_name: str, template_file: str, device_id: str = None, threshold: float = 0.8):
    try:
        screenshot_path = os.path.join(SCREENSHOT_DIR, f"screenshot_{int(time.time())}.png")
        if not capture_screen(device_id=device_id, output_path=screenshot_path):
            raise HTTPException(status_code=500, detail="Falha ao capturar tela")
        img = cv2.imread(screenshot_path)
        try:
            os.remove(screenshot_path)
        except Exception:
            pass
        template_full_path = os.path.join(TEMPLATES_DIR, action_name, template_file)
        match = find_template_in_image(img, template_full_path, threshold=threshold)
        if match:
            return {"found": True, "x": match["x"], "y": match["y"], "confidence": match["confidence"]}
        return {"found": False}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Falha debug_detect: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def load_sequence(action_name: str) -> List[Dict[str, Any]]:
    """Carrega a sequência de ações baseada no nome da ação."""
    sequence_path = os.path.join(TEMPLATES_DIR, action_name, "sequence.json")
    if not os.path.exists(sequence_path):
        logger.error(f"Sequencia não encontrada: {sequence_path}")
        return []
    
    try:
        with open(sequence_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and "sequence" in data:
                return data["sequence"]
            return []
    except Exception as e:
        logger.error(f"Erro ao ler sequence.json: {e}")
        return []

def find_template_in_image(image, template_path, threshold=0.8):
    """Encontra o template na imagem fornecida (formato cv2/numpy)."""
    if not os.path.exists(template_path):
        logger.warning(f"Template não encontrado: {template_path}")
        return None

    template = cv2.imread(template_path)
    if template is None:
        logger.warning(f"Falha ao carregar template (cv2): {template_path}")
        return None

    # Grayscale
    img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    temp_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # Match
    result = cv2.matchTemplate(img_gray, temp_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        h, w = temp_gray.shape
        top_left = max_loc
        center_x = top_left[0] + w // 2
        center_y = top_left[1] + h // 2
        return {"x": center_x, "y": center_y, "confidence": float(max_val)}
    
    return None

@app.post("/processar_acao")
async def process_action(
    file: UploadFile = File(...), 
    action_name: str = Form(...)  # e.g., "pegar_bau"
):
    """
    Recebe uma imagem e o nome da ação (pasta de templates).
    Verifica qual passo da sequência está presente na imagem.
    Retorna a ação a ser executada (click) e as coordenadas.
    """
    # 1. Read Image
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Imagem inválida")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao processar imagem: {str(e)}")

    # 2. Load Sequence
    sequence = load_sequence(action_name)
    if not sequence:
        raise HTTPException(status_code=404, detail=f"Ação '{action_name}' não encontrada ou vazia.")

    # 3. Iterate Sequence to find match
    for step in sequence:
        template_filename = step.get("template_file")
        if not template_filename:
            continue
            
        template_full_path = os.path.join(TEMPLATES_DIR, action_name, template_filename)
        
        match = find_template_in_image(img, template_full_path)
        
        if match:
            # Encontrou um passo da sequência!
            return {
                "found": True,
                "step_name": step.get("name"),
                "action": "click", # Por enquanto assume click, poderia ler de step['action_on_found']
                "x": match["x"],
                "y": match["y"],
                "confidence": match["confidence"],
                "message": f"Template {template_filename} encontrado."
            }

    # Se nenhum template for encontrado
    return {
        "found": False,
        "action": "none",
        "message": "Nenhum template da sequência foi encontrado na imagem."
    }

@app.post("/start_action")
async def start_action(action_name: str = Form(...), device_id: str = Form(None), fila_atual: int = Form(None), use_scroll_config: bool = Form(False)):
    """
    Inicia um ciclo de automação: captura tela, detecta template e simula toque, respeitando
    delays e tentativas configurados por passo em sequence.json.
    """
    max_iterations = 50
    automation_logs = []

    start_ts = time.time()
    log_message = f"Iniciando ação '{action_name}' no dispositivo {device_id if device_id else 'padrão'}"
    logger.info(log_message)
    automation_logs.append(f"{time.strftime('%H:%M:%S')} | {log_message}")
    sys_info = {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "pid": os.getpid()
    }
    logger.debug(f"Sistema: {sys_info}")

    try:
        sequence = load_sequence(action_name)
        if not sequence:
            log_message = f"Ação '{action_name}' não encontrada ou vazia."
            logger.error(log_message)
            automation_logs.append(log_message)
            raise HTTPException(status_code=404, detail=log_message)

        current_step_index = 0

        for i in range(max_iterations):
            if current_step_index >= len(sequence):
                duration = time.time() - start_ts
                log_message = f"Ação '{action_name}' concluída com sucesso em {duration:.1f}s"
                logger.info(log_message)
                automation_logs.append(f"{time.strftime('%H:%M:%S')} | {log_message}")
                return {"status": "success", "message": log_message, "logs": automation_logs}

            current_step = sequence[current_step_index]
            template_filename = current_step.get("template_file")
            action_type = current_step.get("action")

            # Suporte a passos sem template: ações diretas (ex.: center_click, tap_absolute)
            if not template_filename and action_type:
                try:
                    screenshot_path = os.path.join(SCREENSHOT_DIR, f"screenshot_{int(time.time())}.png")
                    if not capture_screen(device_id=device_id, output_path=screenshot_path):
                        err = "Falha ao capturar a tela do dispositivo."
                        logger.error(err)
                        automation_logs.append(f"{time.strftime('%H:%M:%S')} | {err}")
                        raise HTTPException(status_code=500, detail=err)
                    img = cv2.imread(screenshot_path)
                    if img is None:
                        os.remove(screenshot_path)
                        err = "Falha ao carregar a imagem capturada."
                        logger.error(err)
                        automation_logs.append(f"{time.strftime('%H:%M:%S')} | {err}")
                        raise HTTPException(status_code=500, detail=err)

                    h, w = img.shape[:2]
                    click_x, click_y = None, None
                    if action_type == "center_click":
                        click_x, click_y = w // 2, h // 2
                    elif action_type == "tap_absolute":
                        click_x = int(current_step.get("x", w // 2))
                        click_y = int(current_step.get("y", h // 2))
                    else:
                        logger.warning(f"Ação desconhecida no passo {current_step_index + 1}: {action_type}. Pulando.")
                        automation_logs.append(f"{time.strftime('%H:%M:%S')} | Ação desconhecida: {action_type}")
                        current_step_index += 1
                        # Limpa screenshot
                        try:
                            os.remove(screenshot_path)
                        except Exception:
                            pass
                        continue

                    simulate_touch(click_x, click_y, device_id=device_id)
                    msg = f"Ação '{action_type}' executada em ({click_x}, {click_y})."
                    logger.info(msg)
                    automation_logs.append(f"{time.strftime('%H:%M:%S')} | {msg}")

                    if bool(current_step.get("debug_overlay", False)):
                        dbg = _save_debug_click_overlay(img, click_x, click_y, rect=None, label=action_type)
                        if dbg:
                            automation_logs.append(f"{time.strftime('%H:%M:%S')} | Debug salvo: {dbg}")

                    # Limpa screenshot
                    try:
                        os.remove(screenshot_path)
                    except Exception:
                        pass

                    post_detection_delay = float(current_step.get("post_detection_delay", 0) or 0)
                    if post_detection_delay > 0:
                        time.sleep(post_detection_delay)

                    current_step_index += 1
                    continue

                except Exception as e:
                    err = f"Erro ao executar ação direta '{action_type}': {e}"
                    logger.error(err)
                    automation_logs.append(f"{time.strftime('%H:%M:%S')} | {err}")
                    raise HTTPException(status_code=500, detail=err)

            if not template_filename:
                log_message = f"Passo {current_step_index + 1} sem 'template_file'. Pulando."
                logger.warning(log_message)
                automation_logs.append(log_message)
                current_step_index += 1
                continue

            # Configurações por passo
            initial_delay = float(current_step.get("initial_delay", 0) or 0)
            max_attempts = int(current_step.get("max_attempts", 3) or 3)
            attempt_delay = float(current_step.get("attempt_delay", 0.5) or 0.5)
            click_delay = float(current_step.get("click_delay", 0) or 0)
            post_detection_delay = float(current_step.get("post_detection_delay", 0) or 0)
            wait_for_template = bool(current_step.get("wait_for_template", False))
            wait_timeout = float(current_step.get("wait_timeout", 0) or 0)
            wait_interval = float(current_step.get("wait_interval", 0.2) or 0.2)
            threshold = float(current_step.get("threshold", 0.8) or 0.8)

            # Scroll settings
            requires_scroll = bool(current_step.get("requires_scroll", False))
            scroll_on_fail = current_step.get("scroll_on_fail")  # {mode: 'config_fila'|'custom', ...}
            delay_after_scroll = float(current_step.get("delay_after_scroll", 0.8) or 0.8)

            step_header = (
                f"Passo {current_step_index + 1}/{len(sequence)}: '{template_filename}' "
                f"(initial_delay={initial_delay}s, max_attempts={max_attempts}, attempt_delay={attempt_delay}s, "
                f"click_delay={click_delay}s, post_delay={post_detection_delay}s)"
            )
            logger.info(step_header)
            automation_logs.append(f"{time.strftime('%H:%M:%S')} | {step_header}")

            if initial_delay > 0:
                msg = f"Aguardando initial_delay de {initial_delay}s antes de procurar o template."
                logger.info(msg)
                automation_logs.append(msg)
                time.sleep(initial_delay)

            template_full_path = os.path.join(TEMPLATES_DIR, action_name, template_filename)

            # Pré-scroll configurado por passo (como no script de rally)
            if requires_scroll and use_scroll_config and fila_atual and isinstance(fila_atual, int) and fila_atual >= 4:
                filas_cfg = (SCROLL_CONFIG or {}).get("filas", {})
                cfg = filas_cfg.get(str(fila_atual), {})
                num_scrolls = int(cfg.get("num_scrolls", max(0, fila_atual - 3)))
                row_height = int(cfg.get("row_height", 230))
                start_y = int(cfg.get("start_y", 800))
                center_x = int(cfg.get("center_x", 1200))
                duration_ms = int(cfg.get("scroll_duration", 1000))
                end_y = start_y - row_height
                logger.info(f"Aplicando pré-scroll (fila {fila_atual}) {num_scrolls}x | ({center_x},{start_y})->({center_x},{end_y}) {duration_ms}ms")
                automation_logs.append(f"{time.strftime('%H:%M:%S')} | Pre-scroll fila {fila_atual}: {num_scrolls}x")
                try:
                    for _ in range(num_scrolls):
                        simulate_scroll(device_id=device_id, start_coords=[center_x, start_y], end_coords=[center_x, end_y], duration_ms=duration_ms)
                        time.sleep(delay_after_scroll)
                except Exception as e:
                    logger.error(f"Erro no pré-scroll: {e}")
                    automation_logs.append(f"{time.strftime('%H:%M:%S')} | Erro no pré-scroll: {e}")

            found = False

            # Laço de tentativas para o passo atual
            start_wait = time.time()
            for attempt in range(1, max_attempts + 1):
                msg = f"Tentativa {attempt}/{max_attempts} para o passo {current_step_index + 1}."
                logger.info(msg)
                automation_logs.append(f"{time.strftime('%H:%M:%S')} | {msg}")

                screenshot_path = os.path.join(SCREENSHOT_DIR, f"screenshot_{int(time.time())}.png")
                if not capture_screen(device_id=device_id, output_path=screenshot_path):
                    err = "Falha ao capturar a tela do dispositivo."
                    logger.error(err)
                    automation_logs.append(f"{time.strftime('%H:%M:%S')} | {err}")
                    raise HTTPException(status_code=500, detail=err)

                img = cv2.imread(screenshot_path)
                if img is None:
                    os.remove(screenshot_path)
                    err = "Falha ao carregar a imagem capturada."
                    logger.error(err)
                    automation_logs.append(f"{time.strftime('%H:%M:%S')} | {err}")
                    raise HTTPException(status_code=500, detail=err)

                match = find_template_in_image(img, template_full_path, threshold=threshold)

                # Limpa screenshot
                # Não remove ainda se vamos salvar debug
                will_debug = bool(current_step.get("debug_overlay", False))
                if not will_debug:
                    try:
                        os.remove(screenshot_path)
                    except Exception:
                        pass
                    automation_logs.append(f"{time.strftime('%H:%M:%S')} | Screenshot temporária removida.")

                if match:
                    found = True
                    msg = f"Template encontrado em ({match['x']}, {match['y']}) confiança {match['confidence']:.2f}"
                    logger.info(msg)
                    automation_logs.append(f"{time.strftime('%H:%M:%S')} | {msg}")

                    if click_delay > 0:
                        msg = f"Aguardando click_delay de {click_delay}s antes do toque."
                        logger.info(msg)
                        automation_logs.append(f"{time.strftime('%H:%M:%S')} | {msg}")
                        time.sleep(click_delay)

                    simulate_touch(match["x"], match["y"], device_id=device_id)
                    msg = f"Toque simulado em ({match['x']}, {match['y']})."
                    logger.info(msg)
                    automation_logs.append(f"{time.strftime('%H:%M:%S')} | {msg}")

                    if bool(current_step.get("debug_overlay", False)):
                        # Reconstrói o retângulo do template pelo centro
                        try:
                            temp_img = cv2.imread(template_full_path)
                            th, tw = temp_img.shape[:2] if temp_img is not None else (0, 0)
                            rx = int(match["x"] - tw // 2)
                            ry = int(match["y"] - th // 2)
                            dbg = _save_debug_click_overlay(img, match["x"], match["y"], rect=(rx, ry, tw, th), label=template_filename)
                            if dbg:
                                automation_logs.append(f"{time.strftime('%H:%M:%S')} | Debug salvo: {dbg}")
                        except Exception as e:
                            logger.warning(f"Falha ao salvar debug overlay: {e}")
                        # Limpa screenshot após debug
                        try:
                            os.remove(screenshot_path)
                        except Exception:
                            pass

                    if post_detection_delay > 0:
                        msg = f"Aguardando post_detection_delay de {post_detection_delay}s para estabilizar a UI."
                        logger.info(msg)
                        automation_logs.append(f"{time.strftime('%H:%M:%S')} | {msg}")
                        time.sleep(post_detection_delay)

                    current_step_index += 1
                    break
                else:
                    msg = f"Template '{template_filename}' não encontrado na tentativa {attempt}."
                    logger.info(msg)
                    automation_logs.append(f"{time.strftime('%H:%M:%S')} | {msg}")

                    # Scroll ao não encontrar (on_fail)
                    if scroll_on_fail:
                        try:
                            mode = scroll_on_fail.get("mode", "config_fila")
                            if mode == "config_fila" and use_scroll_config and fila_atual and isinstance(fila_atual, int) and fila_atual >= 4:
                                filas_cfg = (SCROLL_CONFIG or {}).get("filas", {})
                                cfg = filas_cfg.get(str(fila_atual), {})
                                row_height = int(cfg.get("row_height", 230))
                                start_y = int(cfg.get("start_y", 800))
                                center_x = int(cfg.get("center_x", 1200))
                                duration_ms = int(cfg.get("scroll_duration", 800))
                                end_y = start_y - row_height
                                simulate_scroll(device_id=device_id, start_coords=[center_x, start_y], end_coords=[center_x, end_y], duration_ms=duration_ms)
                                automation_logs.append(f"{time.strftime('%H:%M:%S')} | Scroll on_fail aplicado (fila {fila_atual})")
                                time.sleep(delay_after_scroll)
                            elif mode == "custom":
                                center_x = int(scroll_on_fail.get("center_x", 1200))
                                start_y = int(scroll_on_fail.get("start_y", 800))
                                row_height = int(scroll_on_fail.get("row_height", 230))
                                duration_ms = int(scroll_on_fail.get("duration_ms", 800))
                                end_y = start_y - row_height
                                simulate_scroll(device_id=device_id, start_coords=[center_x, start_y], end_coords=[center_x, end_y], duration_ms=duration_ms)
                                automation_logs.append(f"{time.strftime('%H:%M:%S')} | Scroll on_fail custom aplicado")
                                time.sleep(delay_after_scroll)
                        except Exception as e:
                            logger.error(f"Erro ao aplicar scroll_on_fail: {e}")
                            automation_logs.append(f"{time.strftime('%H:%M:%S')} | Erro scroll_on_fail: {e}")

                    if wait_for_template and wait_timeout > 0:
                        # Aguardar um pequeno intervalo entre tentativas dentro da janela de timeout
                        elapsed = time.time() - start_wait
                        if elapsed < wait_timeout:
                            wait_time = min(wait_interval, wait_timeout - elapsed)
                            msg = f"Aguardando {wait_time:.1f}s (wait_for_template) antes da próxima tentativa."
                            logger.info(msg)
                            automation_logs.append(msg)
                            time.sleep(wait_time)
                        else:
                            msg = "Tempo de espera (wait_timeout) excedido para este passo."
                            logger.info(msg)
                            automation_logs.append(msg)
                    else:
                        time.sleep(attempt_delay)

            if not found:
                msg = f"Passo {current_step_index + 1} não concluído após {max_attempts} tentativas. Repetindo ciclo."
                logger.info(msg)
                automation_logs.append(f"{time.strftime('%H:%M:%S')} | {msg}")

        log_message = f"Ação '{action_name}' não concluída após {max_iterations} ciclos."
        logger.info(log_message)
        automation_logs.append(f"{time.strftime('%H:%M:%S')} | {log_message}")
        return {"status": "failed", "message": log_message, "logs": automation_logs}

    except HTTPException as he:
        log_message = f"Erro HTTP na ação '{action_name}': {he.detail}"
        logger.error(log_message)
        automation_logs.append(f"{time.strftime('%H:%M:%S')} | {log_message}")
        raise HTTPException(status_code=he.status_code, detail=he.detail, headers={"X-Automation-Logs": json.dumps(automation_logs)})
    except Exception as e:
        log_message = f"Erro inesperado na ação '{action_name}': {str(e)}"
        logger.error(log_message, exc_info=True)
        automation_logs.append(f"{time.strftime('%H:%M:%S')} | {log_message}")
        raise HTTPException(status_code=500, detail=log_message, headers={"X-Automation-Logs": json.dumps(automation_logs)})

