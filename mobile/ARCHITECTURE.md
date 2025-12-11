# AutoTouchDroid Mobile PoC

## Objetivo
- Validar recursos técnicos necessários para automação mobile executada diretamente no dispositivo.
- Separar completamente a nova arquitetura mobile do backend existente (apenas consulta).

## Estrutura
- `mobile_poc/api/main.py`: API FastAPI independente para validações de PoC (recursos, viabilidade, integração por consulta, performance).
- `mobile_poc/requirements.txt`: Dependências mínimas.

## Integração (Consulta)
- A API da PoC lista grupos e sequences em `backend/actions/templates` sem modificar nada no backend atual.

## Critérios de Sucesso
- Projeto mobile independente do backend existente.
- Nenhuma alteração no backend funcional atual.
- PoC valida recursos (FastAPI, OpenCV, NumPy), viabilidade técnica (matchTemplate), integração por consulta (sequence.json), e performance.
- Arquitetura documentada e separada.

## Execução Local
1. Criar venv e instalar: `pip install -r mobile_poc/requirements.txt`
2. Rodar: `uvicorn mobile_poc.api.main:app --reload`
3. Endpoints úteis:
   - `/health`
   - `/poc/resources`
   - `/poc/viability`
   - `/poc/integration/actions`
   - `/poc/performance`

