"""
Générateur d'icônes pour la PWA Globibat
Crée des icônes de base avec le logo Globibat
"""

import os
from PIL import Image, ImageDraw, ImageFont
import io

def create_icon(size):
    """Crée une icône avec le logo Globibat"""
    # Créer une nouvelle image avec fond bleu
    img = Image.new('RGB', (size, size), color='#0d6efd')
    draw = ImageDraw.Draw(img)
    
    # Ajouter un cercle blanc au centre
    margin = size // 8
    circle_bbox = [margin, margin, size - margin, size - margin]
    draw.ellipse(circle_bbox, fill='white')
    
    # Ajouter le texte "G" au centre
    # Utiliser une police par défaut
    font_size = size // 3
    try:
        # Essayer de charger une police système
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        # Utiliser la police par défaut si arial n'est pas disponible
        font = ImageFont.load_default()
    
    # Centrer le texte
    text = "G"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (size - text_width) // 2
    text_y = (size - text_height) // 2 - bbox[1]
    
    draw.text((text_x, text_y), text, fill='#0d6efd', font=font)
    
    return img

def generate_all_icons():
    """Génère toutes les tailles d'icônes nécessaires"""
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    # Créer le dossier icons s'il n'existe pas
    icons_dir = "static/icons"
    os.makedirs(icons_dir, exist_ok=True)
    
    for size in sizes:
        icon = create_icon(size)
        icon.save(f"{icons_dir}/icon-{size}x{size}.png")
        print(f"✓ Icône {size}x{size} créée")
    
    # Créer aussi les icônes spéciales
    badge_icon = create_icon(96)
    badge_icon.save(f"{icons_dir}/badge.png")
    
    employe_icon = create_icon(96)
    employe_icon.save(f"{icons_dir}/employe.png")
    
    print("\n✅ Toutes les icônes ont été générées !")

if __name__ == "__main__":
    try:
        from PIL import Image
        generate_all_icons()
    except ImportError:
        print("⚠️ Pillow n'est pas installé. Installez-le avec : pip install Pillow")
        print("Les icônes par défaut seront utilisées.") 