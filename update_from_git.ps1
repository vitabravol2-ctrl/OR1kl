$ErrorActionPreference = "Stop"
try {
    git pull
    if (-not (Test-Path .venv)) { py -3 -m venv .venv }
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    python main.py
}
catch {
    Write-Host ""
    Write-Host "[ERROR] Update/startup failed. $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to close"
    exit 1
}
