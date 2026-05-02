# time-anchor installer for Windows PowerShell.
# One-liner:
#   iwr -useb https://raw.githubusercontent.com/TroyJLorents-GH/time-anchor/main/install.ps1 | iex
#
# Downloads the latest main branch as a zip over HTTPS (no git, no SSH),
# extracts to ~/.claude/skills/time-anchor and ~/.claude/commands/.

$ErrorActionPreference = 'Stop'

$Repo = 'TroyJLorents-GH/time-anchor'
$Branch = 'main'
$ClaudeDir = Join-Path $env:USERPROFILE '.claude'
$SkillDir = Join-Path $ClaudeDir 'skills\time-anchor'
$CommandsDir = Join-Path $ClaudeDir 'commands'
$TmpDir = Join-Path $env:TEMP "time-anchor-install-$(Get-Random)"
$ZipPath = Join-Path $TmpDir 'src.zip'

try {
    New-Item -ItemType Directory -Force -Path $TmpDir | Out-Null

    Write-Host "-> Downloading time-anchor from github.com/$Repo..."
    $Url = "https://github.com/$Repo/archive/refs/heads/$Branch.zip"
    Invoke-WebRequest -Uri $Url -OutFile $ZipPath -UseBasicParsing

    Write-Host "-> Extracting..."
    Expand-Archive -Path $ZipPath -DestinationPath $TmpDir -Force
    $Extracted = Join-Path $TmpDir "time-anchor-$Branch"

    Write-Host "-> Installing skill to $SkillDir"
    if (Test-Path $SkillDir) { Remove-Item -Recurse -Force $SkillDir }
    New-Item -ItemType Directory -Force -Path (Split-Path $SkillDir) | Out-Null
    Copy-Item -Recurse (Join-Path $Extracted 'skills\time-anchor') $SkillDir

    Write-Host "-> Installing slash commands to $CommandsDir"
    New-Item -ItemType Directory -Force -Path $CommandsDir | Out-Null
    Copy-Item (Join-Path $Extracted 'commands\*.md') $CommandsDir -Force

    Write-Host ''
    Write-Host '+ time-anchor installed.' -ForegroundColor Green
    Write-Host ''
    Write-Host 'Restart Claude Code, then try:'
    Write-Host '  /current-time'
    Write-Host '  /set-timezone'
    Write-Host ''
    Write-Host "Memory file: $SkillDir\memory.json (created on first use)"
} finally {
    if (Test-Path $TmpDir) { Remove-Item -Recurse -Force $TmpDir -ErrorAction SilentlyContinue }
}
