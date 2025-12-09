from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import os
import json
import logging
from typing import Dict, Any, List

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

@app.get("/")
async def root():
    return {"status": "online", "service": "AutoTouchDroid API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

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
