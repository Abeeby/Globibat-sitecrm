"""
Module de tâches programmées pour Globibat
À exécuter avec un scheduler (cron, celery, etc.)
"""

from datetime import datetime, date, time, timedelta
from app import app, db, Employe, Pointage
from notifications import send_notification_absence, send_rappel_badge, send_rapport_mensuel_rh
import threading
import time

def check_absences():
    """Vérifie les absences du jour (à exécuter à 10h par exemple)"""
    with app.app_context():
        aujourd_hui = date.today()
        
        # Si c'est le weekend, ne pas vérifier
        if aujourd_hui.weekday() >= 5:  # 5=samedi, 6=dimanche
            return
        
        # Récupérer tous les employés actifs
        employes_actifs = Employe.query.filter_by(actif=True).all()
        
        for employe in employes_actifs:
            # Vérifier s'il a un pointage aujourd'hui
            pointage = Pointage.query.filter_by(
                employe_id=employe.id,
                date_pointage=aujourd_hui
            ).first()
            
            # Si pas de pointage ou pas d'arrivée le matin
            if not pointage or not pointage.arrivee_matin:
                # Marquer comme absent
                if not pointage:
                    pointage = Pointage(
                        employe_id=employe.id,
                        date_pointage=aujourd_hui,
                        absence=True
                    )
                    db.session.add(pointage)
                else:
                    pointage.absence = True
                
                db.session.commit()
                
                # Envoyer notification
                send_notification_absence(employe)
                print(f"Absence détectée pour {employe.nom} {employe.prenom}")

def send_badge_reminders():
    """Envoie des rappels de badgeage"""
    with app.app_context():
        maintenant = datetime.now()
        aujourd_hui = date.today()
        
        # Si c'est le weekend, ne pas envoyer de rappels
        if aujourd_hui.weekday() >= 5:
            return
        
        # Définir les heures de rappel
        rappels = {
            'arrivee_matin': time(8, 45),      # Rappel à 8h45 si pas badgé
            'depart_midi': time(12, 15),       # Rappel à 12h15
            'arrivee_apres_midi': time(13, 45), # Rappel à 13h45
            'depart_soir': time(17, 30)        # Rappel à 17h30
        }
        
        heure_actuelle = maintenant.time()
        
        for type_badge, heure_rappel in rappels.items():
            # Vérifier si c'est l'heure du rappel (± 5 minutes)
            if abs((datetime.combine(date.today(), heure_actuelle) - 
                   datetime.combine(date.today(), heure_rappel)).total_seconds()) < 300:
                
                # Récupérer les employés qui n'ont pas badgé
                employes_actifs = Employe.query.filter_by(actif=True).all()
                
                for employe in employes_actifs:
                    pointage = Pointage.query.filter_by(
                        employe_id=employe.id,
                        date_pointage=aujourd_hui
                    ).first()
                    
                    # Vérifier selon le type de badge
                    envoyer_rappel = False
                    
                    if type_badge == 'arrivee_matin' and (not pointage or not pointage.arrivee_matin):
                        envoyer_rappel = True
                    elif type_badge == 'depart_midi' and pointage and pointage.arrivee_matin and not pointage.depart_midi:
                        envoyer_rappel = True
                    elif type_badge == 'arrivee_apres_midi' and pointage and not pointage.arrivee_apres_midi:
                        envoyer_rappel = True
                    elif type_badge == 'depart_soir' and pointage and (pointage.arrivee_matin or pointage.arrivee_apres_midi) and not pointage.depart_soir:
                        envoyer_rappel = True
                    
                    if envoyer_rappel:
                        send_rappel_badge(employe, type_badge)
                        print(f"Rappel {type_badge} envoyé à {employe.nom} {employe.prenom}")

def generate_monthly_report():
    """Génère et envoie le rapport mensuel (à exécuter le 1er de chaque mois)"""
    with app.app_context():
        # Obtenir le mois précédent
        aujourd_hui = date.today()
        premier_jour_mois = aujourd_hui.replace(day=1)
        dernier_jour_mois_precedent = premier_jour_mois - timedelta(days=1)
        mois = dernier_jour_mois_precedent.month
        annee = dernier_jour_mois_precedent.year
        
        # Collecter les statistiques par employé
        employes_stats = []
        employes = Employe.query.filter_by(actif=True).all()
        
        for employe in employes:
            pointages = Pointage.query.filter_by(employe_id=employe.id).filter(
                db.extract('month', Pointage.date_pointage) == mois,
                db.extract('year', Pointage.date_pointage) == annee
            ).all()
            
            stats = {
                'nom': f"{employe.nom} {employe.prenom}",
                'heures': sum(p.heures_travaillees for p in pointages),
                'retards': sum(1 for p in pointages if p.retard_matin or p.retard_apres_midi),
                'absences': sum(1 for p in pointages if p.absence)
            }
            employes_stats.append(stats)
        
        # Envoyer le rapport
        send_rapport_mensuel_rh(employes_stats, mois, annee)
        print(f"Rapport mensuel {mois}/{annee} envoyé")

def run_scheduler():
    """Lance le scheduler de tâches"""
    print("Scheduler démarré...")
    
    while True:
        maintenant = datetime.now()
        
        # Vérifier les absences à 10h00
        if maintenant.hour == 10 and maintenant.minute == 0:
            print("Vérification des absences...")
            check_absences()
            time.sleep(60)  # Attendre 1 minute pour éviter de relancer
        
        # Envoyer les rappels toutes les 15 minutes
        if maintenant.minute % 15 == 0:
            print("Envoi des rappels...")
            send_badge_reminders()
            time.sleep(60)
        
        # Générer le rapport mensuel le 1er du mois à 9h
        if maintenant.day == 1 and maintenant.hour == 9 and maintenant.minute == 0:
            print("Génération du rapport mensuel...")
            generate_monthly_report()
            time.sleep(60)
        
        # Attendre 30 secondes avant la prochaine vérification
        time.sleep(30)

# Pour lancer le scheduler dans un thread séparé
def start_scheduler():
    """Démarre le scheduler dans un thread séparé"""
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    print("Scheduler lancé en arrière-plan")

if __name__ == "__main__":
    # Test direct
    with app.app_context():
        print("Test des tâches...")
        # check_absences()
        # send_badge_reminders()
        # generate_monthly_report() 