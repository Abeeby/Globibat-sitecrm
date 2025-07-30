from app import app, db, Admin

# Script pour réinitialiser le compte admin
with app.app_context():
    # Supprimer tous les admins existants
    Admin.query.delete()
    db.session.commit()
    
    # Créer le nouveau compte admin
    admin = Admin(username='Globibat')
    admin.set_password('Miser1597532684$')
    db.session.add(admin)
    db.session.commit()
    
    print("✅ Compte admin créé avec succès !")
    print("Utilisateur : Globibat")
    print("Mot de passe : Miser1597532684$") 