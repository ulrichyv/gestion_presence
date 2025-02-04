from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.http import HttpResponse
from .models import User, Presence
import qrcode
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image

def index(request):
    return render(request, 'index.html')

def report(request):
    users = User.objects.all()  # Récupère tous les utilisateurs
    presence_data = []  # Liste pour stocker les données des présences

    for user in users:
        presences = user.presences.all()  # Récupère toutes les présences de chaque utilisateur
        presence_data.append({'user': user, 'presences': presences})

    return render(request, 'report.html', {'presence_data': presence_data})

def formulaire(request):
    return render(request, 'formulaire.html')

def generate_badge_from_html(badge_html, nom, prenom):
    """Génère une image du badge à partir du HTML en utilisant Selenium."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=800x600")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    temp_html_path = os.path.join(settings.MEDIA_ROOT, f"badge_{nom}_{prenom}.html")
    with open(temp_html_path, "w", encoding="utf-8") as file:
        file.write(badge_html)
    
    file_url = f"file://{temp_html_path}"
    driver.get(file_url)
    time.sleep(2)  # Attendre le chargement complet
    
    screenshot_path = os.path.join(settings.MEDIA_ROOT, f"badge_{nom}_{prenom}.png")
    driver.save_screenshot(screenshot_path)
    driver.quit()
    
    image = Image.open(screenshot_path)
    
    cropped_image = image.crop((0, 0, 510, 600))
    final_image_path = os.path.join(settings.MEDIA_ROOT, f"badge_final_{nom}_{prenom}.png")
    cropped_image.save(final_image_path)
    os.remove(temp_html_path)
    
    return final_image_path

def generer_badge(request):
    if request.method == "POST":
        nom = request.POST.get("nom")
        prenom = request.POST.get("prenom")
        fonction = request.POST.get("fonction")
        matricule = request.POST.get("matricule")
        cni = request.POST.get("cni")
        photo = request.FILES.get("photo")

        # Validation des champs
        if not all([nom, prenom, fonction, matricule, cni, photo]):
            messages.error(request, "Tous les champs et la photo doivent être remplis.")
            return redirect("formulaire")

        # Sauvegarde de la photo
        fs = FileSystemStorage()
        photo_filename = f"photos/{nom}_{prenom}.jpg".replace(" ", "_")
        photo_path = fs.save(photo_filename, photo)
        photo_url = fs.url(photo_path)

        # Génération du QR code
        qr_data = f"Nom: {nom}, Prénom: {prenom}, Matricule: {matricule}"
        qr = qrcode.make(qr_data)
        qr_filename = f"qr_codes/qr_{nom}_{prenom}.png".replace(" ", "_")
        qr_path = os.path.join(settings.MEDIA_ROOT, qr_filename)
        os.makedirs(os.path.dirname(qr_path), exist_ok=True)
        qr.save(qr_path)
        qr_url = fs.url(qr_filename)

        # Rendu du HTML
        badge_html = render_to_string(
            "badge.html",
            {
                "firstname": nom,
                "lastname": prenom,
                "fonction": fonction,
                "matricule": matricule,
                "cni": cni,
                "photo_path": request.build_absolute_uri(photo_url),  # URL complète
                "qr_code_path": request.build_absolute_uri(qr_url),   # URL complète
                "local_path": request.build_absolute_uri("/media/logos/logo.png"),
            },
        )

        # Génération du badge final
        badge_image = generate_badge_from_html(badge_html, nom, prenom)

        # Création de l'utilisateur
        try:
            user = User.objects.create(
                first_name=nom,
                last_name=prenom,
                cni=cni,
                matricule=matricule,
                fonction=fonction,
                path_qr_code=request.build_absolute_uri(qr_url),
                path_badge=request.build_absolute_uri(badge_image),  # Corrected here
                path_photo=request.build_absolute_uri(photo_url),
            )
            user.save()
        except Exception as e:
            messages.error(request, f"Une erreur est survenue : {e}")
            return redirect("formulaire")

        messages.success(request, "Badge généré avec succès!")
        return redirect("")

    return render(request, "create_badge_form.html")
