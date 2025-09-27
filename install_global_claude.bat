@echo off
REM ========================================
REM INSTALADOR GLOBAL DO CLAUDE
REM Adiciona Claude ao PATH do Windows
REM ========================================

echo 🤖 ================================
echo    INSTALADOR GLOBAL DO CLAUDE
echo ================================
echo.

REM Verifica se está executando como administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Executando como Administrador
) else (
    echo ❌ ERRO: Este script precisa ser executado como Administrador!
    echo.
    echo 💡 Como executar como Administrador:
    echo    1. Clique com botão direito no arquivo
    echo    2. Selecione "Executar como administrador"
    echo.
    pause
    exit /b 1
)

echo.
echo 📍 Diretório atual: %~dp0
echo 📁 Arquivo claude-global.bat: %~dp0claude-global.bat

REM Verifica se o arquivo existe
if not exist "%~dp0claude-global.bat" (
    echo ❌ ERRO: Arquivo claude-global.bat não encontrado!
    pause
    exit /b 1
)

echo.
echo 🔧 Copiando claude-global.bat para C:\Windows\System32\claude.bat...

REM Copia o arquivo para o System32 (que está no PATH)
copy "%~dp0claude-global.bat" "C:\Windows\System32\claude.bat" >nul

if %errorLevel% == 0 (
    echo ✅ Claude instalado com sucesso!
    echo.
    echo 🎉 AGORA VOCÊ PODE USAR 'claude' DE QUALQUER LUGAR!
    echo.
    echo 💬 Comandos disponíveis:
    echo    claude chat          - Conversar com Claude
    echo    claude status        - Ver status do sistema
    echo    claude help          - Ver ajuda
    echo    claude memory        - Ver memória
    echo    claude projects      - Ver projetos
    echo.
    echo 🧪 Testando instalação...
    echo.
    
    REM Testa o comando
    claude status
    
    echo.
    echo ✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!
    echo 🚀 Claude agora está disponível globalmente!
    
) else (
    echo ❌ ERRO: Falha ao copiar arquivo!
    echo 💡 Verifique as permissões e tente novamente.
)

echo.
pause