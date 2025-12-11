import os
import time
import json
import platform
import numpy as np
import cv2
from fastapi import FastAPI, HTTPException
from typing import Dict, Any

app = FastAPI()

def _measure_cv_operations() -> Dict[str, Any]:
    t0 = time.time()
    img = np.random.randint(0, 255, (256, 256), dtype=np.uint8)
    templ = img[64:128, 64:128]
    res = cv2.matchTemplate(img, templ, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    t1 = time.time()
    return {"max_val": float(max_val), "max_loc": list(max_loc), "elapsed_ms": int((t1 - t0) * 1000)}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/poc/resources")
def poc_resources():
    return {
        "python": platform.python_version(),
        "cv2": getattr(cv2, "__version__", "unknown"),
        "numpy": getattr(np, "__version__", "unknown"),
    }

@app.get("/poc/viability")
def poc_viability():
    try:
        metrics = _measure_cv_operations()
        return {"cv_matchTemplate": metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/poc/integration/actions")
def poc_integration_actions():
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend", "actions", "templates"))
    groups = []
    if os.path.isdir(base):
        for name in os.listdir(base):
            p = os.path.join(base, name)
            if os.path.isdir(p):
                seq_path = os.path.join(p, "sequence.json")
                has_seq = os.path.isfile(seq_path)
                item = {"group": name, "has_sequence": has_seq}
                if has_seq:
                    try:
                        with open(seq_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        item["sequence_len"] = len(data) if isinstance(data, list) else 0
                    except Exception:
                        item["sequence_len"] = 0
                groups.append(item)
    return {"templates_dir": base, "groups": groups}

@app.get("/poc/performance")
def poc_performance():
    samples = []
    for _ in range(3):
        samples.append(_measure_cv_operations())
    avg_ms = int(sum(s["elapsed_ms"] for s in samples) / len(samples))
    return {"samples": samples, "avg_elapsed_ms": avg_ms}

@app.get("/poc/devices")
def poc_devices():
    devices = [{"id": "poc-remote", "name": "Dispositivo Remoto"}]
    return {"devices": devices}

@app.get("/poc/actions/list")
def poc_actions_list():
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend", "actions", "templates"))
    actions = []
    if os.path.isdir(base):
        for name in os.listdir(base):
            p = os.path.join(base, name)
            seq_path = os.path.join(p, "sequence.json")
            if os.path.isfile(seq_path):
                try:
                    with open(seq_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    actions.append({"group": name, "steps": data})
                except Exception:
                    actions.append({"group": name, "steps": []})
    return {"actions": actions}

