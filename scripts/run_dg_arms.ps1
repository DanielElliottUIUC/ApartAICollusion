# D–G arm runner, Windows PowerShell version of run_dg_arms.sh (same arms, flags and output folders).
#
#   .\scripts\run_dg_arms.ps1 pilot                         # Base pilot: 5 LLM sellers, no scripted seat (seed 0; -Seeds 1 for another)
#   .\scripts\run_dg_arms.ps1 extract results\dg_pilot\<run_dir>   # -> configs\replay\base_pilot.json
#   .\scripts\run_dg_arms.ps1 must                          # 9 must-run arms, seeds 0-4, 2 at a time
#   .\scripts\run_dg_arms.ps1 all                           # + F-sham and Base-hb
#   .\scripts\run_dg_arms.ps1 D,E -Seeds 0,1,2 -Jobs 2
# Resumable (skips finished runs). Costs money (OpenRouter), about $1.5-2 per run. Check with Daniel before a sweep.
param(
    [Parameter(Mandatory = $true, Position = 0)][string[]]$What,
    [Parameter(Position = 1)][string]$RunDir = "",
    [int[]]$Seeds = @(0, 1, 2, 3, 4),
    [int]$Jobs = 2
)
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$Root = Split-Path -Parent $PSScriptRoot
$Harness = Join-Path $Root "third_party\llm-agent-collusion"
$Out = Join-Path $Root "results\dg"
$Replay = Join-Path $Root "configs\replay\base_pilot.json"
$Common = @("--sellers", "5", "--buyers", "5", "--seller_models", "google/gemini-3.8-flash", "--buyer_models", "openai/gpt-4.1-mini",
            "--rounds", "15", "--max_tokens", "16000", "--seller_comms_enabled", "--seller_dms_enabled", "--max_dms_per_round", "2",
            "--broadcast_history_rounds", "4", "--prohibition_notice", "--report_tool", "-y")
$Plea = @("--buyer_plea_hour", "3", "--buyer_plea_text", "buyer_plea_human")
$ArmFlags = @{
    "Base"    = @("--seat_mode", "placebo")
    "D"       = @("--seat_mode", "undercover")
    "D-hs"    = @("--seat_mode", "undercover_human")
    "D-hb"    = @("--seat_mode", "undercover") + $Plea
    "D-hsb"   = @("--seat_mode", "undercover_human") + $Plea
    "E"       = @("--seat_mode", "undercover", "--warning")
    "F"       = @("--seat_mode", "undercover", "--warning", "--precedent")
    "G-warn"  = @("--seat_mode", "placebo", "--warning")
    "G-prec"  = @("--seat_mode", "placebo", "--warning", "--precedent")
    "F-sham"  = @("--seat_mode", "undercover", "--warning", "--sham_history")
    "Base-hb" = @("--seat_mode", "placebo") + $Plea
}
$Must = @("Base", "D", "D-hs", "D-hb", "D-hsb", "E", "F", "G-warn", "G-prec")
$All = $Must + @("F-sham", "Base-hb")

$envFile = Join-Path $Root "compute.env"
if ((Test-Path $envFile) -and (Select-String -Path $envFile -Pattern '^\s*LLM_MODEL\s*=\s*\S' -Quiet)) {
    Write-Error "LLM_MODEL is set in compute.env. That forces one model into every seat. Remove it first."
}

if ($What[0] -eq "pilot") {
    $seed = $Seeds[0]
    $pilotDir = Join-Path $Root "results\dg_pilot"
    New-Item -ItemType Directory -Force (Join-Path $pilotDir "logs") | Out-Null
    Write-Host "Base pilot, seed $seed - 5 LLM sellers, no scripted seat -> results\dg_pilot"
    Push-Location $Harness
    try {
        uv run python src/continuous_double_auction/simulation.py @Common --seeds $seed --tag "pilot-seed$seed" --log_dir $pilotDir |
            Tee-Object -FilePath (Join-Path $pilotDir "logs\pilot-seed$seed.log")
    } finally { Pop-Location }
    Write-Host "next: .\scripts\run_dg_arms.ps1 extract results\dg_pilot\<run_dir>"
    exit 0
}
if ($What[0] -eq "extract") {
    if (-not $RunDir) { Write-Error "extract needs the pilot run directory" }
    python (Join-Path $Root "scripts\extract_replay_path.py") $RunDir --out $Replay
    exit $LASTEXITCODE
}

$Arms = switch ($What[0]) { "must" { $Must } "all" { $All } default { $What } }
foreach ($a in $Arms) { if (-not $ArmFlags.ContainsKey($a)) { Write-Error "unknown arm: $a" } }
if (-not (Test-Path $Replay)) { Write-Error "missing $Replay - run the pilot and extract first" }
New-Item -ItemType Directory -Force (Join-Path $Out "logs") | Out-Null

$procs = @()
Write-Host "arms: $($Arms -join ' ') | seeds: $($Seeds -join ' ') | $Jobs at a time"
foreach ($seed in $Seeds) {
    foreach ($arm in $Arms) {
        $tag = "$arm-seed$seed"
        $done = Get-ChildItem -Path $Out -Directory -Filter "*_$tag" -ErrorAction SilentlyContinue |
                Where-Object { Test-Path (Join-Path $_.FullName "collusion_metrics.json") }
        if ($done) { Write-Host "skip $tag (done)"; continue }
        while (@($procs | Where-Object { -not $_.HasExited }).Count -ge $Jobs) { Start-Sleep -Seconds 15 }
        $runArgs = @("run", "python", "src/continuous_double_auction/simulation.py") + $Common + $ArmFlags[$arm] +
                   @("--scripted_seat_path", $Replay, "--offer_hour", "3", "--offer_price", "96", "--arm", $arm,
                     "--seeds", "$seed", "--tag", $tag, "--log_dir", $Out)
        Write-Host "$(Get-Date -Format HH:mm) start $tag"
        $procs += Start-Process -FilePath "uv" -ArgumentList $runArgs -WorkingDirectory $Harness -NoNewWindow -PassThru `
                    -RedirectStandardOutput (Join-Path $Out "logs\$tag.log") -RedirectStandardError (Join-Path $Out "logs\$tag.err.log")
    }
}
$procs | ForEach-Object { $_.WaitForExit() }
Get-ChildItem (Join-Path $Out "logs\*.log") | ForEach-Object {
    Select-String -Path $_.FullName -Pattern "JOINT CRITERION|regulator reports:|failed turns" |
        ForEach-Object { "$($_.Filename): $($_.Line.Trim())" }
}
Write-Host "finished. Next: judge + analysis (README 'Analysis (D-G)')."
