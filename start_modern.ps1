# Script de lancement du CRM Globibat - Design Moderne (Windows)
# ==============================================================

Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        🚀 CRM GLOBIBAT - DESIGN MODERNE 🚀          ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Vérifier Python
Write-Host "🔧 Vérification de l'environnement..." -ForegroundColor Yellow
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python n'est pas installé ou n'est pas dans le PATH" -ForegroundColor Red
    Write-Host "Veuillez installer Python depuis python.org" -ForegroundColor Yellow
    pause
    exit 1
}
Write-Host "✅ Python détecté" -ForegroundColor Green

# Installer les dépendances si nécessaire
Write-Host "📚 Vérification des dépendances..." -ForegroundColor Yellow
pip install -q flask flask-sqlalchemy flask-login 2>$null

# Variables d'environnement
$env:FLASK_APP = "app_modern.py"
$env:FLASK_ENV = "development"
$env:SECRET_KEY = "dev-secret-key-globibat-2024"

Clear-Host

Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        🎨 CRM GLOBIBAT - INTERFACE MODERNE 🎨        ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "📌 INFORMATIONS DE CONNEXION" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host ""
Write-Host "🌐 URL d'accès : " -NoNewline -ForegroundColor White
Write-Host "http://localhost:5000" -ForegroundColor Green
Write-Host ""
Write-Host "📍 PAGES PRINCIPALES :" -ForegroundColor Yellow
Write-Host "   • Dashboard    : " -NoNewline -ForegroundColor White
Write-Host "http://localhost:5000/modern/dashboard" -ForegroundColor Cyan
Write-Host "   • Chantiers    : " -NoNewline -ForegroundColor White
Write-Host "http://localhost:5000/modern/chantiers" -ForegroundColor Cyan
Write-Host "   • Factures     : " -NoNewline -ForegroundColor White
Write-Host "http://localhost:5000/modern/factures" -ForegroundColor Cyan
Write-Host ""
Write-Host "🎯 FONCTIONNALITÉS CLÉS :" -ForegroundColor Yellow
Write-Host "   • Mode clair/sombre (switch dans le header)" -ForegroundColor White
Write-Host "   • Planning Gantt interactif" -ForegroundColor White
Write-Host "   • Carte des chantiers" -ForegroundColor White
Write-Host "   • Timeline avec photos" -ForegroundColor White
Write-Host "   • Suivi budgétaire en temps réel" -ForegroundColor White
Write-Host ""
Write-Host "⌨️  RACCOURCIS :" -ForegroundColor Yellow
Write-Host "   • Ctrl+C : Arrêter le serveur" -ForegroundColor White
Write-Host "   • F5     : Rafraîchir la page" -ForegroundColor White
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor DarkGray
Write-Host "🚀 Démarrage du serveur..." -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor DarkGray
Write-Host ""

# Lancer l'application
python app_modern.py