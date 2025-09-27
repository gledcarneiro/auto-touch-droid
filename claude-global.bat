@echo off
REM ========================================
REM CLAUDE - ACESSO UNIVERSAL GLOBAL
REM Criado pela parceria Claude-Gled
REM ========================================

REM Detecta automaticamente onde está o partnership_core
set "PARTNERSHIP_ROOT="

REM Procura em locais comuns
if exist "C:\Users\Gled\TRAE\auto-touch-droid\partnership_core\universal_access.py" (
    set "PARTNERSHIP_ROOT=C:\Users\Gled\TRAE\auto-touch-droid\partnership_core"
    goto :found
)

if exist "%USERPROFILE%\TRAE\auto-touch-droid\partnership_core\universal_access.py" (
    set "PARTNERSHIP_ROOT=%USERPROFILE%\TRAE\auto-touch-droid\partnership_core"
    goto :found
)

REM Procura recursivamente a partir do diretório do usuário
for /r "%USERPROFILE%" %%i in (partnership_core) do (
    if exist "%%i\universal_access.py" (
        set "PARTNERSHIP_ROOT=%%i"
        goto :found
    )
)

REM Se não encontrou, mostra erro
echo ❌ ERRO: Não foi possível encontrar o partnership_core!
echo 📍 Procurei em:
echo    - C:\Users\Gled\TRAE\auto-touch-droid\partnership_core\
echo    - %USERPROFILE%\TRAE\auto-touch-droid\partnership_core\
echo    - Recursivamente em %USERPROFILE%
echo.
echo 💡 Certifique-se de que o sistema está instalado corretamente.
pause
exit /b 1

:found
echo.
echo 🤖 ================================
echo    CLAUDE ATIVADO GLOBALMENTE!
echo ================================
echo 📍 Usando: %PARTNERSHIP_ROOT%
echo 💬 Argumentos: %*
echo.

REM Executa o universal_access.py com os argumentos passados
python "%PARTNERSHIP_ROOT%\universal_access.py" %*

REM Se houve erro, mostra informação útil
if errorlevel 1 (
    echo.
    echo ❌ Erro ao executar Claude!
    echo 💡 Dicas:
    echo    - Verifique se Python está instalado: python --version
    echo    - Verifique se está no PATH
    echo    - Tente executar diretamente: python "%PARTNERSHIP_ROOT%\universal_access.py" chat
    echo.
    pause
)