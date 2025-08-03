# 🚀 Guide de Démarrage Rapide - Globibat CRM

## ✅ Checklist de Mise en Production

### 1. Installation (15 minutes)

```bash
# 1. Cloner le projet
git clone [votre-repo]
cd Globibat_Badge_System

# 2. Créer l'environnement virtuel
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate # Linux/Mac

# 3. Installer les dépendances
pip install -r requirements_production.txt

# 4. Configurer l'environnement
cp .env.example .env
# Éditer .env avec vos paramètres
```

### 2. Configuration Base de Données (10 minutes)

```bash
# PostgreSQL recommandé pour la production
CREATE DATABASE globibat_crm;
CREATE USER globibat WITH ENCRYPTED PASSWORD 'votre_mot_de_passe';
GRANT ALL PRIVILEGES ON DATABASE globibat_crm TO globibat;

# Mettre à jour .env
DATABASE_URL=postgresql://globibat:password@localhost/globibat_crm

# Initialiser la base
flask db upgrade
flask init-data
```

### 3. Créer le Premier Admin (2 minutes)

```bash
flask create-admin
# Email: admin@globibat.ch
# Mot de passe: [choisir un mot de passe fort]
```

### 4. Lancer l'Application

#### Développement/Test
```bash
flask run --host=0.0.0.0 --port=5000
```

#### Production
```bash
# Avec Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"

# Ou avec superviseur
sudo supervisorctl start globibat
```

## 🎯 Configuration Initiale (30 minutes)

### 1. Se Connecter
- URL : `http://[votre-domaine]:8000`
- Email : admin@globibat.ch
- Mot de passe : celui créé précédemment

### 2. Paramètres de Base
1. **Entreprise** (`/admin/settings`)
   - Nom : Globibat SA
   - Adresse : Rie des Tattes d'Oie 93, 1260 Nyon
   - TVA : CHE-XXX.XXX.XXX

2. **Départements** (`/admin/departments`)
   - Créer : Direction, Chantier, Administration, etc.

3. **Politiques de Dépenses** (`/admin/expense-policies`)
   - Transport : 100 CHF/jour
   - Repas : 40 CHF/jour
   - Hébergement : 200 CHF/jour

### 3. Ajouter les Employés

#### Via Interface (`/admin/employees/new`)
1. Informations personnelles
2. Département et poste
3. Type de contrat et salaire
4. Générer badge et PIN

#### Import en Masse (Excel)
```
Préparer fichier Excel avec colonnes :
- Prénom, Nom, Email
- Département, Poste
- Salaire/Taux horaire
- Date d'embauche

Importer via : /admin/employees/import
```

### 4. Configurer les Badges

Pour chaque employé :
1. **Badge physique** : Programmer le numéro dans le lecteur
2. **QR Code** : Imprimer depuis `/employee/[id]/qr-code`
3. **PIN** : Communiquer le code initial (123456)
4. Demander de changer le PIN à la première connexion

## 📱 Utilisation Quotidienne

### Pour les Employés

#### Pointage
1. Arrivée : Badge/QR/PIN → "Bonjour [Prénom]!"
2. Pause midi : Badge → "Bon appétit!"
3. Retour : Badge → "Bon retour!"
4. Départ : Badge → "Bonne soirée! Total: Xh"

#### Congés
1. Menu → Mes Congés → Nouvelle Demande
2. Choisir dates et type
3. Ajouter justificatif si nécessaire
4. Soumettre → Email au manager

#### Dépenses
1. Menu → Mes Dépenses → Nouvelle
2. Photo du reçu
3. Catégorie et montant
4. Soumettre → Workflow automatique

### Pour les Managers

#### Dashboard Équipe (`/dashboard/team`)
- Présences en temps réel
- Congés à approuver (badge rouge)
- Dépenses en attente
- Statistiques équipe

#### Actions Quotidiennes
1. **Matin** : Vérifier présences
2. **Midi** : Approuver demandes urgentes
3. **Soir** : Valider heures supplémentaires

### Pour RH/Finance

#### Cycle Mensuel
- **25 du mois** : Lancer calcul paie
- **26-27** : Vérifier et ajuster
- **28** : Valider fiches de paie
- **29-30** : Distribution automatique

#### Rapports Clés
- `/reports/attendance` : Présences mensuelles
- `/reports/payroll` : Récap paie
- `/reports/expenses` : Dépenses par catégorie
- `/reports/compliance` : Conformité légale

## 🔧 Maintenance

### Sauvegardes Automatiques
```bash
# Ajouter au crontab
0 3 * * * /opt/globibat/backup.sh

# backup.sh contient :
#!/bin/bash
pg_dump globibat_crm > backup_$(date +%Y%m%d).sql
tar -czf uploads_$(date +%Y%m%d).tar.gz uploads/
# Copier vers stockage sécurisé
```

### Monitoring
- Logs : `/logs/globibat.log`
- Erreurs : `/logs/error.log`
- Performances : Intégrer New Relic/Datadog

### Mises à Jour
```bash
git pull origin main
pip install -r requirements.txt --upgrade
flask db upgrade
sudo supervisorctl restart globibat
```

## 🆘 Dépannage Rapide

### Problème de Connexion
```bash
# Réinitialiser mot de passe admin
flask shell
>>> from app.models import User
>>> admin = User.query.filter_by(email='admin@globibat.ch').first()
>>> admin.set_password('NouveauMotDePasse123!')
>>> db.session.commit()
```

### Badge Non Reconnu
1. Vérifier que l'employé est actif
2. Vérifier le numéro de badge dans `/admin/employees/[id]`
3. Tester avec le code PIN

### Erreur Calcul Paie
1. Vérifier les heures du mois
2. Vérifier les taux horaires/salaires
3. Relancer avec logs : `flask calculate-payroll --debug`

### Base de Données Lente
```sql
-- Optimiser les index
CREATE INDEX idx_attendance_date ON attendances(date);
CREATE INDEX idx_attendance_employee ON attendances(employee_id);
CREATE INDEX idx_expense_date ON expenses(expense_date);

-- Nettoyer anciennes données
DELETE FROM audit_logs WHERE timestamp < NOW() - INTERVAL '1 year';
VACUUM ANALYZE;
```

## 📞 Support

### Contacts Urgents
- **Hotline** : +41 21 505 00 62
- **Email** : support@globibat.ch
- **WhatsApp** : +41 79 XXX XX XX

### Ressources
- Documentation complète : `/docs`
- Vidéos tutoriels : `YouTube/GlobibatCRM`
- FAQ : `/help/faq`

---

**Prêt en 1 heure !** 🎉

Suivez ces étapes et votre système sera opérationnel pour demain matin.