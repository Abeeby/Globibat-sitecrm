# Script de préparation pour upload VPS
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "PREPARATION UPLOAD VPS GLOBIBAT CRM" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Variables
$excludePatterns = @(
    "venv",
    ".git", 
    "__pycache__",
    "*.pyc",
    "*.pyo",
    ".env",
    "*.log",
    "instance/logs/*"
)

# Créer l'archive
Write-Host "`nCreation de l'archive pour upload..." -ForegroundColor Green

# Utiliser 7-Zip si disponible, sinon utiliser tar
if (Get-Command 7z -ErrorAction SilentlyContinue) {
    $excludeArgs = $excludePatterns | ForEach-Object { "-xr!$_" }
    7z a -ttar globibat_update.tar . $excludeArgs
    7z a -tgzip globibat_update.tar.gz globibat_update.tar
    Remove-Item globibat_update.tar
    Write-Host "Archive creee avec 7-Zip" -ForegroundColor Green
} else {
    Write-Host "7-Zip non trouve, utilisation de tar..." -ForegroundColor Yellow
    $excludeArgs = $excludePatterns | ForEach-Object { "--exclude='$_'" }
    $cmd = "tar -czf globibat_update.tar.gz $($excludeArgs -join ' ') ."
    Invoke-Expression $cmd
}

# Vérifier la taille
$fileInfo = Get-Item "globibat_update.tar.gz"
$sizeMB = [math]::Round($fileInfo.Length / 1MB, 2)
Write-Host "Archive creee: globibat_update.tar.gz ($sizeMB MB)" -ForegroundColor Green

# Instructions
Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "INSTRUCTIONS POUR LE DEPLOIEMENT" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. UPLOADER L'ARCHIVE SUR LE VPS:" -ForegroundColor White
Write-Host "   scp globibat_update.tar.gz root@VOTRE_IP_VPS:/tmp/" -ForegroundColor Gray
Write-Host ""
Write-Host "2. SE CONNECTER AU VPS:" -ForegroundColor White
Write-Host "   ssh root@VOTRE_IP_VPS" -ForegroundColor Gray
Write-Host ""
Write-Host "3. DEPLOYER:" -ForegroundColor White
Write-Host "   cd /tmp" -ForegroundColor Gray
Write-Host "   tar -xzf globibat_update.tar.gz" -ForegroundColor Gray
Write-Host "   chmod +x deploy_vps_complete.sh" -ForegroundColor Gray
Write-Host "   ./deploy_vps_complete.sh" -ForegroundColor Gray
Write-Host ""
Write-Host "4. VERIFIER:" -ForegroundColor White
Write-Host "   - Que votre .env contient les bonnes credentials" -ForegroundColor Gray
Write-Host "   - Que le site est accessible" -ForegroundColor Gray
Write-Host "   - Que tous les modules fonctionnent" -ForegroundColor Gray
Write-Host ""
Write-Host "Consultez DEPLOIEMENT_VPS_SIMPLE.md pour plus de details" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan