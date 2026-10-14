$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
    throw 'Create .venv and install requirements first. See DEMO.md.'
}
& .\.venv\Scripts\python.exe run_demo.py @args
exit $LASTEXITCODE
