<#
  run.ps1 - one-command runner for the AI Stock Decision project (Windows PowerShell 5.1)

  Usage:
    .\run.ps1 setup            Check that uv is installed, then `uv sync`.
    .\run.ps1 check            format-check -> lint -> mypy -> pytest (stops at first failure).
    .\run.ps1 fix              `ruff format .` then `ruff check --fix .`.
    .\run.ps1 test [args...]   `uv run pytest -v`, extra args are passed through to pytest.
    .\run.ps1 serve [-Port N]  Run uvicorn on 127.0.0.1:<N> (default 8000).
    .\run.ps1 help             Show this usage (also shown with no argument).

  Notes:
    - Always runs from the repo root (the directory this script lives in).
    - Never reads, prints, creates or modifies .env, and never sets
      TRADING_MODE or LIVE_CONFIRM. The app reads .env itself; paper mode
      is the default.
#>

param(
    [Parameter(Position = 0)]
    [string]$Command = "help",

    [int]$Port = 8000,

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Rest
)

Set-Location -Path $PSScriptRoot

function Show-Usage {
    Write-Host "Usage: .\run.ps1 <command> [args]"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  setup            Check uv is installed, then 'uv sync'."
    Write-Host "  check            ruff format --check, ruff check, mypy, pytest (stops at first failure)."
    Write-Host "  fix              ruff format . then ruff check --fix ."
    Write-Host "  test [args...]   uv run pytest -v [args...]"
    Write-Host "  serve [-Port N]  Run uvicorn on 127.0.0.1:N (default 8000)."
    Write-Host "  help             Show this usage."
}

function Invoke-Native {
    param(
        [string]$Exe,
        [string[]]$CmdArgs
    )
    & $Exe @CmdArgs
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

switch ($Command) {
    "help" {
        Show-Usage
        exit 0
    }

    "setup" {
        $uvCmd = Get-Command uv -ErrorAction SilentlyContinue
        if (-not $uvCmd) {
            Write-Host "ERROR: 'uv' was not found on PATH."
            Write-Host "Install it from https://docs.astral.sh/uv/getting-started/installation/"
            Write-Host "e.g. in PowerShell: irm https://astral.sh/uv/install.ps1 | iex"
            exit 1
        }
        Invoke-Native "uv" @("sync")
        exit 0
    }

    "check" {
        Write-Host "==> ruff format --check ."
        Invoke-Native "uv" @("run", "ruff", "format", "--check", ".")

        Write-Host "==> ruff check ."
        Invoke-Native "uv" @("run", "ruff", "check", ".")

        Write-Host "==> mypy backend/app"
        Invoke-Native "uv" @("run", "mypy", "backend/app")

        Write-Host "==> pytest -v"
        Invoke-Native "uv" @("run", "pytest", "-v")

        Write-Host "ALL CHECKS PASSED"
        exit 0
    }

    "fix" {
        Write-Host "==> ruff format ."
        Invoke-Native "uv" @("run", "ruff", "format", ".")

        Write-Host "==> ruff check --fix ."
        Invoke-Native "uv" @("run", "ruff", "check", "--fix", ".")

        exit 0
    }

    "test" {
        $pytestArgs = @("run", "pytest", "-v") + $Rest
        Invoke-Native "uv" $pytestArgs
        exit 0
    }

    "serve" {
        $url = "http://127.0.0.1:$Port/health"
        Write-Host "Serving at $url"
        Invoke-Native "uv" @("run", "uvicorn", "app.main:app", "--app-dir", "backend", "--host", "127.0.0.1", "--port", "$Port")
        exit 0
    }

    default {
        Write-Host "Unknown command: $Command"
        Write-Host ""
        Show-Usage
        exit 1
    }
}
