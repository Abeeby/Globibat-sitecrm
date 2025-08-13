#!/usr/bin/env python
"""
Application CRM Globibat avec WebSockets
Support temps réel pour chat, notifications et badges
"""

import os
import sys
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room, send
from flask_cors import CORS
import json

# Ajouter le dossier app au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Configuration Flask
app = Flask(__name__, 
            template_folder='app/templates',
            static_folder='app/static')

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-globibat-websocket-2024')

# Chemin absolu pour la base de données
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'globibat.db')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f'sqlite:///{db_path}')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuration CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialisation SocketIO
socketio = SocketIO(app, 
                   cors_allowed_origins="*",
                   logger=True,
                   engineio_logger=True,
                   async_mode='eventlet')

# Import et initialisation de la base de données
try:
    from app.models import db, init_db, seed_demo_data
    db.init_app(app)
    
    with app.app_context():
        # Créer le dossier instance si nécessaire
        instance_path = os.path.join(os.path.dirname(__file__), 'instance')
        if not os.path.exists(instance_path):
            os.makedirs(instance_path)
        
        # Initialiser la base de données
        init_db(app)
        if not os.path.exists(db_path) or os.path.getsize(db_path) < 1000:
            seed_demo_data(app)
            print("✅ Données de démonstration créées!")
except ImportError as e:
    print(f"ℹ️ Modules de base de données non trouvés: {e}")
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy(app)

# Import des vues
try:
    from app.views.modern_views import modern_bp
    app.register_blueprint(modern_bp, url_prefix='/modern')
except ImportError as e:
    print(f"⚠️ Erreur d'import des vues modernes: {e}")

# Route principale
@app.route('/')
def index():
    return render_template('websocket_home.html')

# =============================================================================
# WEBSOCKET EVENTS - CHAT
# =============================================================================

# Stockage en mémoire des utilisateurs connectés et messages
connected_users = {}
chat_messages = {}  # {room: [messages]}
notifications_queue = []

@socketio.on('connect')
def handle_connect():
    """Gestion de la connexion d'un client"""
    print(f"✅ Client connecté: {request.sid}")
    emit('connected', {'sid': request.sid, 'time': datetime.now().isoformat()})

@socketio.on('disconnect')
def handle_disconnect():
    """Gestion de la déconnexion d'un client"""
    print(f"❌ Client déconnecté: {request.sid}")
    
    # Retirer l'utilisateur des salles
    if request.sid in connected_users:
        user_info = connected_users[request.sid]
        emit('user_left', {
            'user': user_info.get('username', 'Anonyme'),
            'time': datetime.now().isoformat()
        }, broadcast=True, skip_sid=request.sid)
        del connected_users[request.sid]

@socketio.on('register_user')
def handle_register_user(data):
    """Enregistrer un utilisateur"""
    username = data.get('username', 'Anonyme')
    user_id = data.get('user_id', request.sid)
    
    connected_users[request.sid] = {
        'username': username,
        'user_id': user_id,
        'connected_at': datetime.now().isoformat()
    }
    
    print(f"👤 Utilisateur enregistré: {username}")
    
    # Notifier tous les clients
    emit('user_joined', {
        'user': username,
        'total_users': len(connected_users),
        'time': datetime.now().isoformat()
    }, broadcast=True)

@socketio.on('join_chat')
def handle_join_chat(data):
    """Rejoindre une salle de chat (chantier)"""
    room = data.get('chantier_id', 'general')
    username = data.get('username', 'Anonyme')
    
    join_room(room)
    
    # Envoyer l'historique des messages
    if room in chat_messages:
        emit('chat_history', chat_messages[room][-50:])  # Derniers 50 messages
    
    # Notifier la salle
    emit('user_joined_room', {
        'user': username,
        'room': room,
        'time': datetime.now().isoformat()
    }, room=room, skip_sid=request.sid)
    
    print(f"💬 {username} a rejoint la salle {room}")

@socketio.on('leave_chat')
def handle_leave_chat(data):
    """Quitter une salle de chat"""
    room = data.get('chantier_id', 'general')
    username = data.get('username', 'Anonyme')
    
    leave_room(room)
    
    emit('user_left_room', {
        'user': username,
        'room': room,
        'time': datetime.now().isoformat()
    }, room=room, skip_sid=request.sid)

@socketio.on('send_message')
def handle_send_message(data):
    """Envoyer un message dans le chat"""
    room = data.get('chantier_id', 'general')
    message = data.get('message', '')
    username = data.get('username', 'Anonyme')
    user_id = data.get('user_id')
    
    if not message:
        return
    
    # Créer l'objet message
    msg_obj = {
        'id': f"msg_{datetime.now().timestamp()}",
        'user': username,
        'user_id': user_id,
        'message': message,
        'time': datetime.now().isoformat(),
        'room': room
    }
    
    # Stocker le message
    if room not in chat_messages:
        chat_messages[room] = []
    chat_messages[room].append(msg_obj)
    
    # Limiter à 100 messages par salle
    if len(chat_messages[room]) > 100:
        chat_messages[room] = chat_messages[room][-100:]
    
    # Envoyer à tous dans la salle
    emit('new_message', msg_obj, room=room)
    
    print(f"📨 Message de {username} dans {room}: {message[:50]}")

@socketio.on('typing')
def handle_typing(data):
    """Indiquer qu'un utilisateur est en train de taper"""
    room = data.get('chantier_id', 'general')
    username = data.get('username', 'Anonyme')
    is_typing = data.get('typing', False)
    
    emit('user_typing', {
        'user': username,
        'typing': is_typing,
        'room': room
    }, room=room, skip_sid=request.sid)

# =============================================================================
# WEBSOCKET EVENTS - NOTIFICATIONS
# =============================================================================

@socketio.on('subscribe_notifications')
def handle_subscribe_notifications(data):
    """S'abonner aux notifications"""
    user_id = data.get('user_id')
    
    # Envoyer les notifications en attente
    user_notifications = [n for n in notifications_queue if n.get('user_id') == user_id or n.get('broadcast')]
    
    if user_notifications:
        emit('pending_notifications', user_notifications)
    
    print(f"🔔 Utilisateur {user_id} abonné aux notifications")

def send_notification(notification_data):
    """Envoyer une notification à tous les clients ou à un utilisateur spécifique"""
    notification = {
        'id': f"notif_{datetime.now().timestamp()}",
        'title': notification_data.get('title', 'Notification'),
        'message': notification_data.get('message', ''),
        'type': notification_data.get('type', 'info'),  # info, success, warning, danger
        'time': datetime.now().isoformat(),
        'user_id': notification_data.get('user_id'),
        'broadcast': notification_data.get('broadcast', False),
        'data': notification_data.get('data', {})
    }
    
    # Ajouter à la queue
    notifications_queue.append(notification)
    
    # Limiter la queue à 100 notifications
    if len(notifications_queue) > 100:
        notifications_queue[:] = notifications_queue[-100:]
    
    # Envoyer la notification
    if notification['broadcast']:
        socketio.emit('notification', notification, broadcast=True)
    else:
        # Envoyer à un utilisateur spécifique
        for sid, user in connected_users.items():
            if user.get('user_id') == notification['user_id']:
                socketio.emit('notification', notification, room=sid)
                break

# =============================================================================
# WEBSOCKET EVENTS - BADGES TEMPS RÉEL
# =============================================================================

@socketio.on('subscribe_badges')
def handle_subscribe_badges(data):
    """S'abonner aux mises à jour des badges"""
    chantier_id = data.get('chantier_id')
    
    if chantier_id:
        join_room(f"badges_{chantier_id}")
    else:
        join_room("badges_all")
    
    print(f"🎫 Abonnement aux badges pour chantier {chantier_id or 'tous'}")

@socketio.on('new_badge')
def handle_new_badge(data):
    """Nouveau badge scanné"""
    badge_data = {
        'id': data.get('badge_id'),
        'employe': data.get('employe'),
        'type': data.get('type'),  # Entrée/Sortie
        'chantier_id': data.get('chantier_id'),
        'chantier': data.get('chantier_name'),
        'time': datetime.now().isoformat(),
        'location': data.get('location', {})
    }
    
    # Diffuser à tous
    socketio.emit('badge_update', badge_data, room='badges_all')
    
    # Diffuser au chantier spécifique
    if badge_data['chantier_id']:
        socketio.emit('badge_update', badge_data, room=f"badges_{badge_data['chantier_id']}")
    
    # Envoyer une notification
    send_notification({
        'title': 'Nouveau Badge',
        'message': f"{badge_data['employe']} - {badge_data['type']} à {badge_data['chantier']}",
        'type': 'info' if badge_data['type'] == 'Entrée' else 'warning',
        'broadcast': True,
        'data': badge_data
    })
    
    print(f"🎫 Badge: {badge_data['employe']} - {badge_data['type']}")

# =============================================================================
# WEBSOCKET EVENTS - ALERTES & ANOMALIES
# =============================================================================

@socketio.on('alert')
def handle_alert(data):
    """Gérer une alerte"""
    alert_data = {
        'id': f"alert_{datetime.now().timestamp()}",
        'type': data.get('type', 'warning'),  # warning, danger, info
        'title': data.get('title', 'Alerte'),
        'message': data.get('message', ''),
        'source': data.get('source', 'system'),
        'data': data.get('data', {}),
        'time': datetime.now().isoformat()
    }
    
    # Diffuser l'alerte
    socketio.emit('alert_broadcast', alert_data, broadcast=True)
    
    # Créer une notification
    send_notification({
        'title': alert_data['title'],
        'message': alert_data['message'],
        'type': alert_data['type'],
        'broadcast': True,
        'data': alert_data
    })
    
    print(f"⚠️ Alerte: {alert_data['title']} - {alert_data['message']}")

# =============================================================================
# WEBSOCKET EVENTS - PRÉSENCE TEMPS RÉEL
# =============================================================================

@socketio.on('update_presence')
def handle_update_presence(data):
    """Mettre à jour la présence d'un employé"""
    presence_data = {
        'employe_id': data.get('employe_id'),
        'employe_name': data.get('employe_name'),
        'status': data.get('status'),  # online, offline, away
        'last_seen': datetime.now().isoformat(),
        'location': data.get('location')
    }
    
    # Diffuser la mise à jour
    socketio.emit('presence_update', presence_data, broadcast=True)
    
    print(f"👁 Présence: {presence_data['employe_name']} - {presence_data['status']}")

# =============================================================================
# API ENDPOINTS POUR TESTS
# =============================================================================

@app.route('/api/websocket/test', methods=['POST'])
def test_websocket():
    """Endpoint de test pour déclencher des événements WebSocket"""
    data = request.get_json()
    event_type = data.get('type', 'notification')
    
    if event_type == 'notification':
        send_notification({
            'title': data.get('title', 'Test Notification'),
            'message': data.get('message', 'Ceci est une notification de test'),
            'type': data.get('level', 'info'),
            'broadcast': True
        })
    
    elif event_type == 'badge':
        socketio.emit('badge_update', {
            'employe': data.get('employe', 'Test Employee'),
            'type': data.get('badge_type', 'Entrée'),
            'chantier': data.get('chantier', 'Chantier Test'),
            'time': datetime.now().isoformat()
        }, broadcast=True)
    
    elif event_type == 'alert':
        socketio.emit('alert_broadcast', {
            'type': data.get('level', 'warning'),
            'title': data.get('title', 'Test Alert'),
            'message': data.get('message', 'Ceci est une alerte de test'),
            'time': datetime.now().isoformat()
        }, broadcast=True)
    
    return jsonify({'success': True, 'message': f'Événement {event_type} envoyé'})

@app.route('/api/websocket/stats')
def websocket_stats():
    """Statistiques des WebSockets"""
    return jsonify({
        'connected_users': len(connected_users),
        'users': [{'username': u['username'], 'connected_at': u['connected_at']} 
                 for u in connected_users.values()],
        'chat_rooms': list(chat_messages.keys()),
        'total_messages': sum(len(msgs) for msgs in chat_messages.values()),
        'pending_notifications': len(notifications_queue)
    })

# =============================================================================
# LANCEMENT DE L'APPLICATION
# =============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 CRM GLOBIBAT - WEBSOCKETS ACTIVÉS")
    print("="*60)
    print("📍 Accès local: http://localhost:5001")
    print("📍 Dashboard: http://localhost:5001/modern/dashboard")
    print("🔌 WebSocket: ws://localhost:5001/socket.io/")
    print("📊 Stats WebSocket: http://localhost:5001/api/websocket/stats")
    print("="*60)
    print("✨ Fonctionnalités temps réel:")
    print("  • Chat par chantier")
    print("  • Notifications instantanées")
    print("  • Badges en temps réel")
    print("  • Alertes et anomalies")
    print("  • Présence des employés")
    print("="*60 + "\n")
    
    # Lancer avec SocketIO (utilise eventlet automatiquement)
    socketio.run(app, 
                host='0.0.0.0',
                port=5001,
                debug=True,
                use_reloader=True)