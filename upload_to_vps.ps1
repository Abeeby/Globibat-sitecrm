# Script PowerShell pour uploader les fichiers vers VPS Hostinger
# Utilisation : .\upload_to_vps.ps1 -VpsIp "VOTRE_IP_VPS"

param(
    [Parameter(Mandatory=$true)]
    [string]$VpsIp,
    
    [Parameter(Mandatory=$false)]
    [string]$VpsUser = "root"
)

Write-Host "=== Upload Globibat CRM vers VPS ===" -ForegroundColor Green
Write-Host "VPS: $VpsUser@$VpsIp" -ForegroundColor Cyan

# Verifier que .env existe
if (-not (Test-Path ".env")) {
    Write-Host "ERREUR: Fichier .env manquant!" -ForegroundColor Red
    Write-Host "Creez d'abord le fichier .env avec vos configurations" -ForegroundColor Yellow
    exit 1
}

# Creer une archive sans le dossier venv
Write-Host "`nCreation de l'archive..." -ForegroundColor Yellow
$excludes = @("venv", "__pycache__", "*.pyc", "instance", ".git")
$tempZip = "globibat_upload.zip"

# Utiliser tar pour creer l'archive (disponible sur Windows 10+)
$excludeArgs = $excludes | ForEach-Object { "--exclude=$_" }
tar -czf $tempZip $excludeArgs *

Write-Host "Archive creee : $tempZip" -ForegroundColor Green

# Upload via SCP
Write-Host "`nUpload vers le VPS..." -ForegroundColor Yellow
Write-Host "Vous allez devoir entrer le mot de passe root du VPS" -ForegroundColor Cyan

scp $tempZip "${VpsUser}@${VpsIp}:/tmp/"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nUpload reussi!" -ForegroundColor Green
    
    # Commandes a executer sur le VPS
    Write-Host "`nConnectez-vous maintenant au VPS et executez :" -ForegroundColor Yellow
    Write-Host @"

ssh $VpsUser@$VpsIp

# Une fois connecte au VPS :
cd /var/www
mkdir -p globibat
cd globibat
tar -xzf /tmp/$tempZip
rm /tmp/$tempZip

# Suivez ensuite le guide DEPLOIEMENT_VPS_HOSTINGER.md

"@ -ForegroundColor Cyan
    
    # Supprimer l'archive locale
    Remove-Item $tempZip -Force
    Write-Host "`nArchive locale supprimee" -ForegroundColor Green
} else {
    Write-Host "`nERREUR lors de l'upload!" -ForegroundColor Red
    Remove-Item $tempZip -Force
}

Write-Host "`nTermine!" -ForegroundColor Green