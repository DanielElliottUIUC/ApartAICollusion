# Step A positive control, Windows PowerShell version of phase0_positive_control.sh (same arms).
#
#   .\scripts\phase0_positive_control.ps1                   # Gemini Flash sellers (base case)
#   .\scripts\phase0_positive_control.ps1 -Model gpt41      # GPT-4.1 sellers
#   .\scripts\phase0_positive_control.ps1 -Model haiku      # Haiku sellers
#   .\scripts\phase0_positive_control.ps1 -Notice           # also run the comms arm with the prohibition rule
#
# No LLM judge here: the joint criterion uses prices and trades only. Judge kept runs afterwards with
# src/continuous_double_auction/evaluation/posthoc_judge.py (reads private messages; see README "Judge").
#
# If PowerShell refuses to run scripts:  powershell -ExecutionPolicy Bypass -File scripts\phase0_positive_control.ps1
param([ValidateSet("gemini", "gpt41", "haiku")][string]$Model = "gemini", [switch]$Notice)
$ErrorActionPreference = "Stop"

$Root    = Split-Path -Parent $PSScriptRoot
$Harness = Join-Path $Root "third_party\llm-agent-collusion"
$Out     = Join-Path $Root "results\phase0_v2"
$Buyer   = "anthropic/claude-haiku-5.5"   # LLM buyers, fixed across every arm. Never "zip".
$MaxTokens = 16000   # Gemini's hidden reasoning tokens count against this; 4000 cut replies off mid-JSON
$Seller  = @{ gemini = "google/gemini-3.8-flash"; gpt41 = "openai/gpt-4.1"; haiku = "anthropic/claude-haiku-5.5" }[$Model]

$envFile = Join-Path $Root "compute.env"
if ((Test-Path $envFile) -and (Select-String -Path $envFile -Pattern '^\s*LLM_MODEL\s*=\s*\S' -Quiet)) {
    Write-Error "LLM_MODEL is set in compute.env. That forces one model into every seat. Remove it first."
}

$Comms = @("--seller_comms_enabled", "--seller_dms_enabled", "--max_dms_per_round", "2", "--broadcast_history_rounds", "4")

function Invoke-Arm([string]$Tag, [string[]]$Extra) {
    Write-Host "=== $Tag ==="
    Push-Location $Harness
    try {
        uv run python src/continuous_double_auction/simulation.py `
            --sellers 4 --buyers 4 --seller_models $Seller --buyer_models $Buyer --rounds 15 `
            --seeds 0 1 2 --max_tokens $MaxTokens --log_dir $Out --tag $Tag -y @Extra
        if ($LASTEXITCODE -ne 0) { throw "arm $Tag failed (exit $LASTEXITCODE)" }
    } finally { Pop-Location }
}

Invoke-Arm "$($Model)_comms"   $Comms
Invoke-Arm "$($Model)_nocomms" @()
if ($Notice) { Invoke-Arm "$($Model)_notice" ($Comms + @("--prohibition_notice")) }
