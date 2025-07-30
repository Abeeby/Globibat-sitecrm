# Script PowerShell pour initialiser et commiter sur GitHub
# Utilisation : .\git_commit.ps1

Write-Host "=== Initialisation Git pour Globibat CRM ===" -ForegroundColor Green

# Verifier si git est installe
try {
    git --version | Out-Null
} catch {
    Write-Host "ERREUR: Git n'est pas installe!" -ForegroundColor Red
    Write-Host "Installez Git depuis : https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

# Initialiser le repo git si necessaire
if (-not (Test-Path ".git")) {
    Write-Host "`nInitialisation du repository Git..." -ForegroundColor Yellow
    git init
}

# Ajouter tous les fichiers
Write-Host "`nAjout des fichiers..." -ForegroundColor Yellow
git add .

# Afficher le status
Write-Host "`nStatus Git:" -ForegroundColor Cyan
git status --short

# Commit initial
Write-Host "`nCreation du commit initial..." -ForegroundColor Yellow
git commit -m "Initial commit - Globibat CRM complet avec SEO optimise"

# Ajouter le remote origin
Write-Host "`nAjout du remote GitHub..." -ForegroundColor Yellow
git remote add origin https://github.com/Abeeby/Globibat-sitecrm.git

# Renommer la branche en main
Write-Host "`nRenommage de la branche principale en 'main'..." -ForegroundColor Yellow
git branch -M main

# Push vers GitHub
Write-Host "`nPush vers GitHub..." -ForegroundColor Yellow
Write-Host "Vous allez devoir entrer vos identifiants GitHub" -ForegroundColor Cyan
git push -u origin main

Write-Host "`n=== Termine! ===" -ForegroundColor Green
Write-Host "Votre code est maintenant sur GitHub : https://github.com/Abeeby/Globibat-sitecrm" -ForegroundColor Cyan
Write-Host "`nN'oubliez pas de :" -ForegroundColor Yellow
Write-Host "1. Verifier que le fichier .env n'est PAS sur GitHub" -ForegroundColor Red
Write-Host "2. Ajouter une description au repository sur GitHub"
Write-Host "3. Configurer les Settings > Pages pour activer GitHub Pages avec index.html"