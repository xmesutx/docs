# Desktop aufräumen
$desktop = "C:\Users\Student\OneDrive - GFN GmbH (EDU)\Desktop"

$regeln = @{
    "Bilder"          = @(".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico")
    "Dokumente"       = @(".pdf", ".doc", ".docx", ".txt", ".odt", ".rtf")
    "Tabellen"        = @(".xls", ".xlsx", ".csv", ".ods")
    "Präsentationen"  = @(".ppt", ".pptx", ".odp")
    "Videos"          = @(".mp4", ".avi", ".mov", ".mkv", ".wmv")
    "Audio"           = @(".mp3", ".wav", ".flac", ".aac", ".ogg")
    "Archive"         = @(".zip", ".rar", ".7z", ".tar", ".gz")
    "Verknüpfungen"   = @(".lnk", ".url")
}

foreach ($ordner in $regeln.Keys) {
    $pfad = Join-Path $desktop $ordner
    if (-not (Test-Path $pfad)) {
        New-Item -ItemType Directory -Path $pfad | Out-Null
    }
}

$dateien = Get-ChildItem -Path $desktop -File

foreach ($datei in $dateien) {
    if ($datei.Name -eq "desktop-aufraumen.ps1") { continue }

    $ziel = $null
    foreach ($ordner in $regeln.Keys) {
        if ($regeln[$ordner] -contains $datei.Extension.ToLower()) {
            $ziel = Join-Path $desktop $ordner
            break
        }
    }

    if (-not $ziel) {
        $ziel = Join-Path $desktop "Sonstiges"
        if (-not (Test-Path $ziel)) {
            New-Item -ItemType Directory -Path $ziel | Out-Null
        }
    }

    Move-Item -Path $datei.FullName -Destination $ziel -Force
    Write-Host "Verschoben: $($datei.Name) → $(Split-Path $ziel -Leaf)"
}

Write-Host "`nFertig! Dein Desktop ist aufgeräumt."
