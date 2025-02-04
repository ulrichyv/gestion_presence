import os
import qrcode
from django.template.loader import render_to_string
from django.conf import settings
from html2image import Html2Image

class BadgeService:
    def __init__(self, nom, prenom, fonction, matricule, cni, photo_path):
        self.nom = nom.strip()
        self.prenom = prenom.strip()
        self.fonction = fonction.strip()
        self.matricule = matricule.strip()
        self.cni = cni.strip()
        self.photo_path = photo_path

        # Définir les répertoires de sortie
        self.badge_output_path = os.path.join(settings.MEDIA_ROOT, "badges")
        self.qr_output_path = os.path.join(settings.MEDIA_ROOT, "qrcodes")
        os.makedirs(self.badge_output_path, exist_ok=True)
        os.makedirs(self.qr_output_path, exist_ok=True)

    def save_photo(self):
        """Enregistre la photo téléchargée"""
        photo_filename = f"{self.nom}_{self.prenom}.jpg".replace(" ", "_")
        self.photo_full_path = os.path.join(self.badge_output_path, photo_filename)

        with open(self.photo_full_path, "wb+") as destination:
            for chunk in self.photo_path.chunks():
                destination.write(chunk)

        return os.path.join(settings.MEDIA_URL, "badges", photo_filename)

    def generate_qr_code(self):
        """Génère un QR Code pour l'identification"""
        qr_filename = f"qr_{self.nom}_{self.prenom}.png".replace(" ", "_")
        qr_full_path = os.path.join(self.qr_output_path, qr_filename)

        # Contenu du QR Code (URL ou info d'identification)
        qr_data = f"Nom: {self.nom}, Prénom: {self.prenom}, Matricule: {self.matricule}"
        qr = qrcode.make(qr_data)
        qr.save(qr_full_path)

        return os.path.join(settings.MEDIA_URL, "qrcodes", qr_filename)

    def generate_html(self, photo_url, qr_code_url):
        """Génère le HTML du badge"""
        return render_to_string("badge.html", {
            "nom": self.nom,
            "prenom": self.prenom,
            "fonction": self.fonction,
            "matricule": self.matricule,
            "cni": self.cni,
            "photo_path": photo_url,
            "qr_code_path": qr_code_url,
            "local_path": os.path.join(settings.MEDIA_URL, "logos", "logo.png")  # Remplace par ton logo
        })

    def save_html(self, html_content):
        """Sauvegarde le HTML généré"""
        self.html_file_path = os.path.join(self.badge_output_path, "badge_temp.html")
        with open(self.html_file_path, "w", encoding="utf-8") as output_file:
            output_file.write(html_content)

    def generate_badge_image(self):
        """Génère l'image du badge avec html2image"""
        image_filename = f"badge_{self.nom}_{self.prenom}.png".replace(" ", "_")
        self.image_full_path = os.path.join(self.badge_output_path, image_filename)

        try:
            hti = Html2Image(output_path=self.badge_output_path)
            hti.screenshot(html_file=self.html_file_path, save_as=image_filename, size=(350, 540))

            if os.path.exists(self.image_full_path):
                return os.path.join(settings.MEDIA_URL, "badges", image_filename)
            else:
                raise Exception("Échec de la génération de l'image.")
        except Exception as e:
            raise Exception(f"Erreur lors de la génération de l'image : {str(e)}")

    def generate_badge(self):
        """Pipeline complet pour la génération du badge"""
        photo_url = self.save_photo()
        qr_code_url = self.generate_qr_code()
        html_content = self.generate_html(photo_url, qr_code_url)
        self.save_html(html_content)
        return self.generate_badge_image()
