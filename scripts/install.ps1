<#
.SYNOPSIS
  Install unity-skillforge into a Unity game repo (Windows).

.DESCRIPTION
  Copies the pack's skills into both tools' directories and places the
  read-by-path tier at a FIXED path, .unity-skillforge\, so every SKILL.md can
  cite PACK/references/... and have it resolve. Claude Code has
  ${CLAUDE_SKILL_DIR} for this; Codex documents no equivalent, so a fixed path
  is the only thing that works in both.

  Claude Code reads  .claude\skills\<name>\SKILL.md
  Codex reads        .agents\skills\<name>\SKILL.md   (NOT .codex\skills)
  Neither scans those directories recursively, which is why skills\ is flat.

.PARAMETER Target
  The game repo to install into. Defaults to the current directory.

.PARAMETER Symlink
  Create symlinks instead of copies. Needs Developer Mode or an elevated
  shell on Windows, which is why copying is the default.

.PARAMETER DryRun
  Print what would happen and change nothing.

.PARAMETER NoAgentsMd
  Skip writing AGENTS.md and CLAUDE.md.

.EXAMPLE
  .\scripts\install.ps1 C:\dev\MyGame
#>
[CmdletBinding()]
param(
  [string]$Target = (Get-Location).Path,
  [switch]$Symlink,
  [switch]$DryRun,
  [switch]$NoAgentsMd
)

$ErrorActionPreference = 'Stop'
$PackRoot = Split-Path -Parent $PSScriptRoot

if (-not (Test-Path -LiteralPath $Target -PathType Container)) {
  throw "target directory does not exist: $Target"
}
$Target = (Resolve-Path -LiteralPath $Target).Path
if ($Target -eq $PackRoot) {
  throw "target is the pack itself. Pass the game repo's path."
}

$Mode = if ($Symlink) { 'symlink' } else { 'copy' }
Write-Host "Installing unity-skillforge"
Write-Host "  pack:   $PackRoot"
Write-Host "  target: $Target"
Write-Host ("  mode:   $Mode" + $(if ($DryRun) { ' (dry run)' } else { '' }))
Write-Host ""

function New-Dir([string]$Path) {
  if ($DryRun) { Write-Host "  would: create $Path"; return }
  New-Item -ItemType Directory -Force -Path $Path | Out-Null
}

function Copy-Entry([string]$Source, [string]$Destination, [bool]$IsDirectory) {
  if (Test-Path -LiteralPath $Destination) {
    if ($DryRun) { Write-Host "  would: remove $Destination" }
    else { Remove-Item -LiteralPath $Destination -Recurse -Force }
  }
  if ($DryRun) { Write-Host "  would: $Mode $Source -> $Destination"; return }
  if ($Mode -eq 'symlink') {
    # Fails without Developer Mode or elevation; surface that clearly rather
    # than leaving a half-installed tree.
    try {
      New-Item -ItemType SymbolicLink -Path $Destination -Target $Source | Out-Null
    } catch {
      throw ("could not create a symlink at $Destination. Enable Developer Mode, " +
             "run as administrator, or re-run without -Symlink. Original error: $($_.Exception.Message)")
    }
  } else {
    if ($IsDirectory) { Copy-Item -LiteralPath $Source -Destination $Destination -Recurse -Force }
    else { Copy-Item -LiteralPath $Source -Destination $Destination -Force }
  }
}

# 1. Skills, into both tools' directories.
foreach ($dest in @((Join-Path $Target '.claude\skills'), (Join-Path $Target '.agents\skills'))) {
  New-Dir $dest
  $count = 0
  foreach ($skill in Get-ChildItem -Directory (Join-Path $PackRoot 'skills')) {
    Copy-Entry $skill.FullName (Join-Path $dest $skill.Name) $true
    $count++
  }
  Write-Host "  $dest  <- $count skills"
}

# 2. Subagents. A Claude Code concept; Codex has no equivalent directory, and
#    docs\CODEX.md ships the same six roles as copy-paste prompts instead.
$agentsDest = Join-Path $Target '.claude\agents'
New-Dir $agentsDest
$agentCount = 0
foreach ($agent in Get-ChildItem -File -Filter *.md (Join-Path $PackRoot 'agents')) {
  Copy-Entry $agent.FullName (Join-Path $agentsDest $agent.Name) $false
  $agentCount++
}
Write-Host "  $agentsDest  <- $agentCount agents"
Write-Host ""

# 3. The read-by-path tier, at the fixed path skills cite as PACK/.
$PackDir = Join-Path $Target '.unity-skillforge'
Write-Host "Tier 2 (read by path) -> $PackDir"
New-Dir $PackDir
# references/, rules/, templates/ and the skill-support scripts live inside the
# companion data skill so that `npx skills add` carries them.
$DataSkill = Join-Path $PackRoot 'skills\unity-skillforge-pack'
foreach ($dir in @('references', 'rules', 'templates', 'scripts')) {
  $source = Join-Path $DataSkill $dir
  if (Test-Path -LiteralPath $source) {
    Copy-Entry $source (Join-Path $PackDir $dir) $true
    Write-Host "  $dir"
  }
}
foreach ($dir in @('docs', 'agents')) {
  $source = Join-Path $PackRoot $dir
  if (Test-Path -LiteralPath $source) {
    Copy-Entry $source (Join-Path $PackDir $dir) $true
    Write-Host "  $dir"
  }
}
Copy-Entry (Join-Path $PackRoot 'AGENTS.md') (Join-Path $PackDir 'AGENTS.md') $false
Write-Host ""

# 4. Tier 0. AGENTS.md is canonical; CLAUDE.md only points at it. Never
#    overwrite an existing AGENTS.md — append a pointer so the game's own
#    rules survive.
if (-not $NoAgentsMd) {
  Write-Host "Tier 0 (always loaded)"
  $targetAgents = Join-Path $Target 'AGENTS.md'
  if (Test-Path -LiteralPath $targetAgents) {
    if (Select-String -LiteralPath $targetAgents -Pattern 'unity-skillforge' -Quiet) {
      Write-Host "  AGENTS.md already references unity-skillforge, leaving it alone"
    } elseif ($DryRun) {
      Write-Host "  would: append a unity-skillforge section to $targetAgents"
    } else {
      Write-Host "  AGENTS.md exists - appending a pointer rather than overwriting it"
      $block = @"

## Unity rules (unity-skillforge)

Read ``.unity-skillforge/AGENTS.md`` before any Unity work. It holds the hard rules and the routing
table that maps a task to the skill that handles it.
"@
      Add-Content -LiteralPath $targetAgents -Value $block
    }
  } else {
    Copy-Entry (Join-Path $PackRoot 'AGENTS.md') $targetAgents $false
    Write-Host "  AGENTS.md"
  }

  $targetClaude = Join-Path $Target 'CLAUDE.md'
  if (Test-Path -LiteralPath $targetClaude) {
    Write-Host "  CLAUDE.md exists, leaving it alone"
  } elseif ($DryRun) {
    Write-Host "  would: write $targetClaude containing '@AGENTS.md'"
  } else {
    Set-Content -LiteralPath $targetClaude -Value '@AGENTS.md'
    Write-Host "  CLAUDE.md"
  }
  Write-Host ""
}

# 5. The design/ contract, if the repo does not have one yet.
$designDir = Join-Path $Target 'design'
if (-not (Test-Path -LiteralPath $designDir)) {
  Write-Host "design\ (the game's own docs: what we are building)"
  New-Dir $designDir
  foreach ($template in @('STATE.md', 'INDEX.md')) {
    Copy-Entry (Join-Path $PackRoot "templates\game-design\$template") (Join-Path $designDir $template) $false
    Write-Host "  design\$template"
  }
  Write-Host "  Fill these in with the design-write-gdd skill. pitch.md, art-bible.md,"
  Write-Host "  mechanic.md and tech-decisions.md are copied by the skills that own them."
} else {
  Write-Host "design\ already exists, leaving it alone"
}
Write-Host ""

Write-Host @"
Next steps
  1. Install the Unity CLI and the Pipeline package:
       winget install Unity.CLI
       unity --version; unity auth login
       unity pipeline install        # with the project open in Unity 6.3 LTS or later
       unity status                  # confirm the CLI can reach the Editor
  2. Strongly recommended, and complementary rather than overlapping:
       /plugin marketplace add Unity-Technologies/unity-agent-plugin
       /plugin install unity@unity-agent-plugin
  3. Start with:  "Use the unity-game-router skill" or fill in design\STATE.md.

Docs: .unity-skillforge\docs\INSTALL.md and .unity-skillforge\docs\USAGE.md
"@
