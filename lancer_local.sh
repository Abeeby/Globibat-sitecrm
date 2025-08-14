#!/bin/bash

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

clear

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}         GLOBIBAT CRM - LANCEMENT LOCAL${NC}"
echo -e "${BLUE}============================================================${NC}"
echo

# Vérifier Python
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✅ Python3 détecté${NC}"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    echo -e "${GREEN}✅ Python détecté${NC}"
    PYTHON_CMD="python"
else
    echo -e "${RED}❌ Python n'est pas installé!${NC}"
    echo -e "${YELLOW}   Installez Python avec: sudo apt install python3${NC}"
    exit 1
fi

echo
echo -e "${YELLOW}🚀 Démarrage de l'application...${NC}"
echo
echo -e "${PURPLE}============================================================${NC}"
echo -e "${GREEN}   IDENTIFIANTS DE CONNEXION:${NC}"
echo -e "${BLUE}   Email: info@globibat.com${NC}"
echo -e "${BLUE}   Mot de passe: Miser1597532684\$${NC}"
echo -e "${PURPLE}============================================================${NC}"
echo

# Lancer l'application
$PYTHON_CMD lancer_local.py