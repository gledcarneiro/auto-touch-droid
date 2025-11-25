# 🧹 PLANO DE LIMPEZA DO PROJETO

## 📊 Situação Atual

### ✅ O Que Funciona (MANTER)
- **`backend/`** - Sistema completo funcional
  - Detecção de templates
  - Execução de ações
  - Ciclo completo de 10 contas
  - Login, pegar baús, pegar recursos, logout
  - Logs estruturados
  - Configurações via .env

### ❌ O Que NÃO Funciona (ARQUIVAR)
- **`mobile/`** - App React Native (incompleto)
- **`partnership_core/`** - Versão web (incompleta)

### 📚 Documentação (ORGANIZAR)
- Múltiplos arquivos MD na raiz
- Alguns duplicados ou obsoletos

---

## 🎯 Objetivos da Limpeza

1. **Remover código inativo** sem perder histórico
2. **Organizar documentação** em pastas lógicas
3. **Manter apenas o essencial** na raiz
4. **Facilitar manutenção futura**

---

## 📋 ETAPAS DE LIMPEZA

### Etapa 1: Criar Estrutura de Arquivamento

```
auto-touch-droid/
├── backend/              ← MANTER (funcional)
├── docs/                 ← CRIAR (organizar documentação)
│   ├── guias/
│   ├── implementacao/
│   └── arquivados/
├── archived_projects/    ← CRIAR (projetos inativos)
│   ├── mobile/          ← MOVER de raiz
│   └── web/             ← MOVER partnership_core
├── .env
├── .gitignore
├── README.md            ← ATUALIZAR
└── requirements.txt
```

### Etapa 2: Mover Projetos Inativos

**Criar pasta de arquivo:**
```bash
mkdir archived_projects
mkdir archived_projects/mobile
mkdir archived_projects/web
```

**Mover projetos:**
```bash
# Mover app mobile
mv mobile/* archived_projects/mobile/

# Mover versão web
mv partnership_core/* archived_projects/web/
```

**Adicionar README em cada:**
```markdown
# Projeto Arquivado

Este projeto foi arquivado em 25/11/2025.

**Motivo:** Incompleto e não funcional.

**Status:** Pode ser retomado no futuro se necessário.

**Alternativa Funcional:** Use o backend em `../../backend/`
```

### Etapa 3: Organizar Documentação

**Criar estrutura:**
```bash
mkdir docs
mkdir docs/guias
mkdir docs/implementacao
mkdir docs/arquivados
```

**Mover arquivos:**

**Para `docs/guias/`:**
- GUIA_CICLO_COMPLETO.md
- CONFIGURACAO_CELULAR.md
- INICIO_RAPIDO.md

**Para `docs/implementacao/`:**
- IMPLEMENTACAO_FASE1.md
- PLANO_DESENVOLVIMENTO_BACKEND.md
- ANALISE_COMPLETA_PROJETO.md

**Para `docs/arquivados/`:**
- SOLUCAO_SCROLL_ANTES_CLICK.md (obsoleto)
- SOLUCAO_FINAL_SWIPE.md (já implementado)
- AJUSTE_SCROLLS_LOGIN.md (já implementado)
- RESUMO_SESSAO.md (obsoleto)

**Manter na raiz:**
- README.md (atualizar)
- RESUMO_CICLO_COMPLETO.md (guia principal)

### Etapa 4: Atualizar .gitignore

Adicionar:
```gitignore
# Projetos arquivados
archived_projects/

# Documentação arquivada (opcional)
docs/arquivados/

# Logs e temporários
logs/
temp_screenshots/
*.log
```

### Etapa 5: Criar README.md Atualizado

```markdown
# 🤖 Auto Touch Droid

Sistema de automação para Android via ADB com detecção de templates.

## ✨ Funcionalidades

- ✅ Detecção de imagens na tela (template matching)
- ✅ Execução de ações automatizadas
- ✅ Ciclo completo para múltiplas contas
- ✅ Login, coleta de recursos, logout automático
- ✅ Configuração via .env
- ✅ Logs estruturados

## 🚀 Início Rápido

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar Dispositivo
Veja: [docs/guias/CONFIGURACAO_CELULAR.md](docs/guias/CONFIGURACAO_CELULAR.md)

### 3. Configurar .env
```bash
cp .env.example .env
# Edite DEFAULT_DEVICE_ID com seu device
```

### 4. Executar

**Testar uma conta:**
```bash
python backend/utils/teste_ciclo_uma_conta.py
```

**Executar todas as contas:**
```bash
python backend/utils/ciclo_completo_todas_contas.py
```

## 📚 Documentação

- **Guias:** [docs/guias/](docs/guias/)
- **Implementação:** [docs/implementacao/](docs/implementacao/)
- **Resumo Completo:** [RESUMO_CICLO_COMPLETO.md](RESUMO_CICLO_COMPLETO.md)

## 🏗️ Estrutura

```
auto-touch-droid/
├── backend/              # Sistema principal (Python)
│   ├── actions/         # Ações e templates
│   ├── config/          # Configurações
│   ├── core/            # Módulos principais
│   └── utils/           # Scripts utilitários
├── docs/                # Documentação
├── .env                 # Configurações locais
└── requirements.txt     # Dependências Python
```

## 🔧 Tecnologias

- Python 3.x
- OpenCV (detecção de imagens)
- ADB (Android Debug Bridge)
- NumPy, Pillow

## 📝 Licença

Projeto pessoal - Gled Carneiro

---

**Desenvolvido com ❤️ pela Claude-Gled Permanent Partnership**
```

---

## ⚠️ IMPORTANTE

### Antes de Executar:

1. **Commit atual** (salvar estado funcional):
```bash
git add .
git commit -m "✅ Sistema 100% funcional - antes da limpeza"
```

2. **Criar branch de backup**:
```bash
git checkout -b backup-pre-cleanup
git checkout main
```

3. **Executar limpeza**

4. **Testar** se tudo ainda funciona

5. **Commit da limpeza**:
```bash
git add .
git commit -m "🧹 Limpeza: arquivados mobile e web, organizada documentação"
```

---

## 📊 Resultado Esperado

### Antes:
```
auto-touch-droid/
├── 19 arquivos MD na raiz
├── mobile/ (não funcional)
├── partnership_core/ (não funcional)
└── backend/ (funcional)
```

### Depois:
```
auto-touch-droid/
├── README.md (atualizado)
├── RESUMO_CICLO_COMPLETO.md
├── backend/ (funcional)
├── docs/ (organizado)
└── archived_projects/ (arquivado)
```

**Redução:** ~70% menos arquivos na raiz
**Organização:** 100% melhor
**Funcionalidade:** 100% mantida

---

## 🎯 Próximos Passos Após Limpeza

1. **Novas Features:**
   - Sistema de agendamento (executar em horários específicos)
   - Notificações (Discord/Telegram quando terminar)
   - Dashboard web simples (só visualização de logs)
   - Backup automático de screenshots importantes

2. **Melhorias:**
   - Testes automatizados
   - CI/CD para validar mudanças
   - Documentação de API
   - Vídeo tutorial

---

**Quer que eu execute essa limpeza agora?** 🧹
