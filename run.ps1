$ErrorActionPreference = "Stop"
try {
    if (-not (Test-Path .venv)) { py -3 -m venv .venv }
    .\.venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    python main.py
}
catch {
    Write-Host ""
    Write-Host "[ERROR] Startup failed. $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to close"
    exit 1
}
