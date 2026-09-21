# workflow check script
# Check: Skill structure, frontmatter, YAML parseability, Markdown links, self-contained boundaries, knowledge entry metadata

param(
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"
$script:FailureCount = 0
$WorkflowRoot = Split-Path -Parent $PSScriptRoot

function Write-Check {
    param([string]$Message, [string]$Status = "INFO")
    $color = switch ($Status) {
        "PASS" { "Green" }
        "FAIL" { "Red" }
        "WARN" { "Yellow" }
        default { "White" }
    }
    Write-Host "[$Status] $Message" -ForegroundColor $color
    if ($Status -eq "FAIL") {
        $script:FailureCount++
    }
}

function Test-YamlParseable {
    param([string]$Path)
    try {
        $content = Get-Content $Path -Raw -Encoding UTF8
        if ($content -match '(?m)^[a-zA-Z_-]+:\s*.+$') {
            return $true
        }
        return $false
    } catch {
        return $false
    }
}

function Extract-FrontmatterFromMarkdown {
    param([string]$Path)
    $content = Get-Content $Path -Raw -Encoding UTF8
    if ($content -match '(?s)^---\s*\n(.*?)\n---') {
        return $Matches[1]
    }
    return $null
}

function Test-MarkdownLinks {
    param([string]$Path)
    $content = Get-Content $Path -Raw -Encoding UTF8
    $dir = Split-Path -Parent $Path

    # Remove fenced code blocks, then inline code spans: Python generics like
    # `def f[T](x: T)` would otherwise parse as Markdown links with an invalid
    # path target
    $contentWithoutCode = $content -replace '(?s)```.*?```', ''
    $contentWithoutCode = $contentWithoutCode -replace '`[^`\r\n]*`', ''

    # Extract Markdown links [text](path)
    $linkPattern = '\[([^\]]+)\]\(([^)]+)\)'
    $links = [regex]::Matches($contentWithoutCode, $linkPattern)

    $broken = @()
    foreach ($match in $links) {
        $linkPath = $match.Groups[2].Value

        # Skip URLs, anchors, absolute paths
        if ($linkPath -match '^(https?://|#|/)') {
            continue
        }

        # Remove anchor part
        $linkPath = $linkPath -replace '#.*$', ''
        if ([string]::IsNullOrWhiteSpace($linkPath)) {
            continue
        }

        # Resolve relative path
        $targetPath = Join-Path $dir $linkPath
        $targetPath = [System.IO.Path]::GetFullPath($targetPath)

        if (-not (Test-Path $targetPath)) {
            $broken += $linkPath
        }
    }

    return $broken
}

function Test-CrossComponentReference {
    param([string]$Path, [string]$SkillName)
    $content = Get-Content $Path -Raw -Encoding UTF8

    $hasInvalidReference = $false
    $issues = @()

    # Check ../ references resolving outside the Skill directory
    $skillRoot = (Join-Path $WorkflowRoot ("skills/" + $SkillName)).TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
    $fileDir = Split-Path -Parent $Path
    foreach ($match in [regex]::Matches($content, '\]\((\.\./[^)]+)\)')) {
        $linkPath = $match.Groups[1].Value -replace '#.*$', ''
        if ([string]::IsNullOrWhiteSpace($linkPath)) { continue }
        $targetPath = [System.IO.Path]::GetFullPath((Join-Path $fileDir $linkPath))
        if (-not $targetPath.StartsWith($skillRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
            $issues += "Reference outside Skill directory: $linkPath"
            $hasInvalidReference = $true
        }
    }

    # Check written instructions referencing other Skills
    $allSkills = (Get-ChildItem (Join-Path $WorkflowRoot "skills") -Directory).Name
    $otherSkills = $allSkills | Where-Object { $_ -ne $SkillName }

    foreach ($skill in $otherSkills) {
        if ($content -match "``$skill``") {
            $issues += "Written reference to other Skill: $skill"
            $hasInvalidReference = $true
        }
    }

    return @{
        HasIssue = $hasInvalidReference
        Issues = $issues
    }
}

Write-Host "`n=== Workflow Check ===`n" -ForegroundColor Cyan

# 1. Check Skill structure
Write-Host "1. Checking Skill structure..." -ForegroundColor Cyan
$skillsDir = Join-Path $WorkflowRoot "skills"
$skills = Get-ChildItem $skillsDir -Directory

foreach ($skill in $skills) {
    $skillName = $skill.Name
    $skillMd = Join-Path $skill.FullName "SKILL.md"

    if (-not (Test-Path $skillMd)) {
        Write-Check "Skill '$skillName' missing SKILL.md" "FAIL"
        continue
    }

    # Check frontmatter
    $frontmatter = Extract-FrontmatterFromMarkdown $skillMd
    if (-not $frontmatter) {
        Write-Check "Skill '$skillName' SKILL.md missing frontmatter" "FAIL"
        continue
    }

    if ($frontmatter -notmatch 'name:') {
        Write-Check "Skill '$skillName' frontmatter missing 'name'" "FAIL"
    }

    if ($frontmatter -notmatch 'description:') {
        Write-Check "Skill '$skillName' frontmatter missing 'description'" "FAIL"
    }

    # Check user-triggered Skills
    $isManualTrigger = $frontmatter -match 'disable-model-invocation:\s*true'
    if ($isManualTrigger) {
        $agentYaml = Join-Path $skill.FullName "agents/openai.yaml"
        if (-not (Test-Path $agentYaml)) {
            Write-Check "Skill '$skillName' is manual-trigger but missing agents/openai.yaml" "FAIL"
        } else {
            if (-not (Test-YamlParseable $agentYaml)) {
                Write-Check "Skill '$skillName' agents/openai.yaml format error" "FAIL"
            }
        }
    }

    if ($script:FailureCount -eq 0) {
        Write-Check "Skill '$skillName' structure complete" "PASS"
    }
}

# 2. Check Markdown links
Write-Host "`n2. Checking Markdown links..." -ForegroundColor Cyan
$allMarkdown = Get-ChildItem $WorkflowRoot -Recurse -Filter "*.md" | Where-Object {
    $_.FullName -notmatch '[\\/]_pipeline[\\/]' -and
    $_.FullName -notmatch '[\\/]node_modules[\\/]' -and
    $_.FullName -notmatch '[\\/]\.git[\\/]'
}

foreach ($md in $allMarkdown) {
    $relativePath = $md.FullName.Substring($WorkflowRoot.Length + 1)
    $brokenLinks = Test-MarkdownLinks $md.FullName

    if ($brokenLinks.Count -gt 0) {
        Write-Check "$relativePath has broken links: $($brokenLinks -join ', ')" "FAIL"
    } elseif ($Verbose) {
        Write-Check "$relativePath links OK" "PASS"
    }
}

if ($script:FailureCount -eq 0) {
    Write-Check "All Markdown links valid" "PASS"
}

# 3. Check self-contained boundaries
Write-Host "`n3. Checking self-contained boundaries..." -ForegroundColor Cyan
foreach ($skill in $skills) {
    $skillName = $skill.Name
    $skillFiles = Get-ChildItem $skill.FullName -Recurse -Filter "*.md"

    foreach ($file in $skillFiles) {
        $relativePath = $file.FullName.Substring($WorkflowRoot.Length + 1)
        $crossRefResult = Test-CrossComponentReference $file.FullName $skillName

        if ($crossRefResult.HasIssue) {
            Write-Check "$relativePath violates self-contained: $($crossRefResult.Issues -join '; ')" "FAIL"
        }
    }
}

if ($script:FailureCount -eq 0) {
    Write-Check "All Skills satisfy self-contained constraint" "PASS"
}

# 4. Check knowledge entry metadata
Write-Host "`n4. Checking knowledge entry metadata..." -ForegroundColor Cyan
$knowledgeDir = Join-Path $skillsDir "inference-ops/references/knowledge"
if (Test-Path $knowledgeDir) {
    $knowledgeEntries = Get-ChildItem $knowledgeDir -Recurse -Filter "*.md" | Where-Object {
        $_.Name -ne "README.md"
    }

    foreach ($entry in $knowledgeEntries) {
        $relativePath = $entry.FullName.Substring($WorkflowRoot.Length + 1)
        $frontmatter = Extract-FrontmatterFromMarkdown $entry.FullName

        if (-not $frontmatter) {
            Write-Check "$relativePath missing audit metadata" "FAIL"
            continue
        }

        $requiredFields = @('source', 'version', 'accessed', 'last_reviewed', 'status')
        foreach ($field in $requiredFields) {
            $pattern = "${field}:"
            if ($frontmatter -notmatch [regex]::Escape($pattern)) {
                Write-Check "$relativePath missing field: $field" "FAIL"
            }
        }
    }

    if ($knowledgeEntries.Count -eq 0) {
        Write-Check "knowledge base has no entries (as expected)" "PASS"
    } elseif ($script:FailureCount -eq 0) {
        Write-Check "knowledge base all entries metadata complete" "PASS"
    }
} else {
    Write-Check "inference-ops/references/knowledge directory not found" "WARN"
}

# Summary
Write-Host "`n=== Check Complete ===`n" -ForegroundColor Cyan
if ($script:FailureCount -eq 0) {
    Write-Host "OK All checks passed" -ForegroundColor Green
    exit 0
} else {
    Write-Host "FAIL Found $script:FailureCount issues" -ForegroundColor Red
    exit 1
}
