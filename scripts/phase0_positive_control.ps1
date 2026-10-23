# Phase 0 positive control, Windows PowerShell version of phase0_positive_control.sh (same arms).
#
#   .\scripts\phase0_positive_control.ps1             # Haiku arms only
#   .\scripts\phase0_positive_control.ps1 -Fallback   # also run the GPT-4.1 arm
#
# If PowerShell refuses to run scripts:  powershell -ExecutionPolicy Bypass -File scripts\phase0_positive_control.ps1
param([switch]$Fallback)
$ErrorActionPreference = "Stop"

$Root    = Split-Path -Parent $PSScriptRoot
$Harness = Join-Path $Root "third_party\llm-agent-collusion"
$Out     = Join-Path $Root "results\phase0"

$Haiku = "anthropic/claude-haiku-5.5"
$Gpt41 = "openai/gpt-4.1"
$Buyer = $Haiku   # LLM buyers, held fixed across every arm. Never "zip" (it always bids ~$80 = seller cost).

$envFile = Join-Path $Root "compute.env"
if ((Test-Path $envFile) -and (Select-String -Path $envFile -Pattern '^\s*LLM_MODEL\s*=\s*\S' -Quiet)) {
    Write-Error "LLM_MODEL is set in compute.env. That forces one model into every seat. Remove it first."
}

function Invoke-Arm([string]$Tag, [string[]]$Extra) {
    Write-Host "=== $Tag ==="
    Push-Location $Harness
    try {
        uv run python src/continuous_double_auction/simulation.py `
            --sellers 3 --buyers 3 --buyer_models $Buyer --rounds 15 --seeds 0 1 2 `
            --llm_eval --log_dir $Out --tag $Tag -y @Extra
        if ($LASTEXITCODE -ne 0) { throw "arm $Tag failed (exit $LASTEXITCODE)" }
    } finally { Pop-Location }
}

Invoke-Arm "haiku_comms"   @("--seller_models", $Haiku, "--seller_comms_enabled")
Invoke-Arm "haiku_nocomms" @("--seller_models", $Haiku)
if ($Fallback) { Invoke-Arm "gpt41_comms" @("--seller_models", $Gpt41, "--seller_comms_enabled") }
