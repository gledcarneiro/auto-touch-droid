# Integração API AutoTouchDroid (Render)

Esta documentação descreve como integrar o Aplicativo React Native com a nova API backend hospedada no Render.

## Visão Geral

O sistema foi migrado de uma execução local (ADB) para uma arquitetura Cliente-Servidor.
- **Cliente (App RN)**: Captura a tela e executa toques.
- **Servidor (API Render)**: Processa a imagem e decide a ação.

## Endpoint Principal

**URL**: `https://<seu-app>.onrender.com/processar_acao`
**Método**: `POST`
**Content-Type**: `multipart/form-data`

### Parâmetros

| Nome        | Tipo   | Descrição                                      |
|-------------|--------|------------------------------------------------|
| `file`      | File   | Arquivo de imagem (screenshot) em formato PNG/JPG |
| `action_name`| String | Nome da ação a ser executada (ex: `pegar_bau`) |

### Resposta (JSON)

#### 1. Ação Encontrada
```json
{
    "found": true,
    "step_name": "Passo 1: Template 01_bau.png",
    "action": "click",
    "x": 42,
    "y": 44,
    "confidence": 0.99,
    "message": "Template 01_bau.png encontrado."
}
```

#### 2. Nenhuma Ação Encontrada
```json
{
    "found": false,
    "action": "none",
    "message": "Nenhum template da sequência foi encontrado na imagem."
}
```

## Guia de Implementação no React Native

### 1. Captura de Tela e Envio
Você precisará de uma biblioteca para capturar a tela (como `react-native-view-shot` ou módulo nativo) e `axios` ou `fetch` para enviar.

Exemplo conceitual:

```javascript
const processScreen = async () => {
    // 1. Capturar Tela (exemplo fictício)
    const uri = await captureScreen(); 
    
    // 2. Preparar Form Data
    const formData = new FormData();
    formData.append('file', {
        uri: uri,
        type: 'image/png',
        name: 'screenshot.png',
    });
    formData.append('action_name', 'pegar_bau');

    // 3. Enviar para API
    try {
        const response = await fetch('https://seu-app.onrender.com/processar_acao', {
            method: 'POST',
            body: formData,
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        
        const data = await response.json();
        
        // 4. Executar Ação
        if (data.found && data.action === 'click') {
            await AccessibilityService.click(data.x, data.y);
        }
        
    } catch (error) {
        console.error("Erro na API", error);
    }
};
```

## Como Testar Localmente

1. Certifique-se de que as dependências estão instaladas:
   ```bash
   pip install -r requirements.txt
   ```
2. Inicie o servidor:
   ```bash
   uvicorn backend.api.main:app --reload
   ```
3. Execute o script de teste (envia uma imagem local):
   ```bash
   python backend/api/test_client.py
   ```

## Deploy no Render

1. Crie uma conta no [Render](https://render.com).
2. Conecte seu repositório GitHub.
3. Crie um novo **Web Service**.
4. O Render deve detectar automaticamente o arquivo `render.yaml`.
5. Se não detectar, use as configurações:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.api.main:app --host 0.0.0.0 --port $PORT`
