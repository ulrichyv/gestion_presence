from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.http import HttpResponse
from .models import User, Presence
import qrcode
import random
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from django.db.models.functions import TruncDay
from django.db.models import Count, Case, When, IntegerField

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from .models import User, Presence
from django.shortcuts import render
from datetime import datetime
from django.db.models import Count, Case, When, IntegerField
from django.db.models.functions import TruncDay

@api_view(['POST'])
def scan(request):
    qr_data = request.data.get('qr_data')
    
    if not qr_data:
        return Response({'message': 'QR data is missing'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Supposons que le QR code contient "Nom: John, Matricule: 1234"
        data = qr_data.split(",")  
        if len(data) < 2:
            return Response({'message': 'Format du QR Code invalide'}, status=status.HTTP_400_BAD_REQUEST)

        nom = data[0].split(":")[1].strip()
        matricule = data[1].split(":")[1].strip()

        # Vérifier si l'utilisateur existe
        user = User.objects.get(matricule=matricule)

        # Vérifier s'il y a déjà une présence aujourd'hui
        today = datetime.now().date()
        presence, created = Presence.objects.get_or_create(
            user=user,
            date=today,
            defaults={'status': 'P', 'heure_arrivee': datetime.now().time()}
        )

        if not created:
            return Response({'message': f"{nom} a déjà été marqué présent aujourd'hui."}, status=status.HTTP_200_OK)
        
        return Response({'message': f'{nom} est maintenant marqué comme présent'}, status=status.HTTP_201_CREATED)

    except User.DoesNotExist:
        return Response({'message': 'Utilisateur non trouvé'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def scan_qr_code(request):
    try:
        qr_data = request.data.get('qr_data')
        print(f"Données reçues : {request.data}")  # Log des données reçues pour le débogage
        if not qr_data:
            return Response({'message': 'Données QR manquantes'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Supposons que le QR code contient "Nom: John, Matricule: 1234"
        data = qr_data.split(",")  
        if len(data) < 2:
            return Response({'message': 'Format du QR Code invalide'}, status=status.HTTP_400_BAD_REQUEST)

        nom = data[0].split(":")[1].strip()
        matricule = data[1].split(":")[1].strip()

        # Vérifier si l'utilisateur existe
        user = User.objects.get(matricule=matricule)

        # Vérifier s'il y a déjà une présence aujourd'hui
        today = datetime.now().date()
        presence, created = Presence.objects.get_or_create(
            user=user,
            date=today,
            defaults={'status': 'P', 'heure_arrivee': datetime.now().time()}
        )

        if not created:
            return Response({'message': f"{nom} a déjà été marqué présent aujourd'hui."}, status=status.HTTP_200_OK)
        
        return Response({'message': f'{nom} est maintenant marqué comme présent'}, status=status.HTTP_201_CREATED)

    except User.DoesNotExist:
        return Response({'message': 'Utilisateur non trouvé'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

def index(request):
    users = User.objects.all()  # Récupère tous les utilisateurs
    total_user = users.count()  # Nombre total d'utilisateurs
    total_presence = 0  # Initialisation du compteur de présences

    # Calcul du total des présences pour tous les utilisateurs
    for user in users:
        total_presence += user.presences.filter(status='P').count()  # Filtrer uniquement les présences

    # Calcul du pourcentage de présence
    if total_user > 0:  # Éviter la division par zéro
        presence_percentage = (total_presence / (total_user * len(users))) * 100
    else:
        presence_percentage = 0

    # Retourner les données à la vue
    return render(request, 'index.html', {
        'total_user': total_user,
        'total_presence': total_presence,
        'presence_percentage': presence_percentage,
    })


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
                "photo_path": request.build_absolute_uri(photo_url),
                "qr_code_path": request.build_absolute_uri(qr_url),
                "local_path": request.build_absolute_uri("/media/logos/logo.png"),
            },
        )

        # Génération du badge final
        badge_image = generate_badge_from_html(badge_html, nom, prenom)

        # Création de l'utilisateur
        try:
            username = f"{nom.lower()}_{prenom.lower()}_{random.randint(1000, 9999)}"
            user = User.objects.create(
                username=username,  # Ajout du username unique
                first_name=nom,
                last_name=prenom,
                cni=cni,
                matricule=matricule,
                fonction=fonction,
                path_qr_code=request.build_absolute_uri(qr_url),
                path_badge=f"/media/badge_final_{nom}_{prenom}.png",
                path_photo=request.build_absolute_uri(photo_url),
                qr_data=qr_data,  # Stockage des données du QR code
            )
            print(user.qr_data)  # Vérification que les données du QR sont bien stockées
        except Exception as e:
            messages.error(request, f"Une erreur est survenue : {e}")
            return redirect("formulaire")

        messages.success(request, "Badge généré avec succès!")
        return redirect("/")

    return render(request, "create_badge_form.html")


def presence(request):
    return render(request, 'presence.html')




def rapport(request):
    """ Génère un rapport pour un employé ou pour le mois en cours. """
    
    # Récupération des données du formulaire, s'il y en a
    nom = request.POST.get("nom", "")  # Par défaut, vide si non renseigné
    date_debut = request.POST.get("Date_deb", None)
    date_fin = request.POST.get("Date_fin", None)
    
    # Si pas de données du formulaire, on prend les valeurs par défaut pour le mois en cours
    if not date_debut or not date_fin:
        today = datetime.now()
        date_debut = today.replace(day=1)  # Premier jour du mois
        date_fin = today  # Aujourd'hui
    
    else:
        # Convertir les dates en objets datetime si elles ont été soumises
        date_debut = datetime.strptime(date_debut, '%Y-%m-%d')
        date_fin = datetime.strptime(date_fin, '%Y-%m-%d')

    # Filtrer les présences par nom (si renseigné) et par date
    presences = Presence.objects.filter(
        user__first_name__icontains=nom,
        date__range=[date_debut, date_fin]
    ).annotate(
        day=TruncDay('date'),
        countP=Count(Case(When(status='P', then=1), output_field=IntegerField())),
        countA=Count(Case(When(status='A', then=1), output_field=IntegerField()))
    ).values('day', 'countP', 'countA').order_by('day')

    # Calcul des totaux
    total_presences = sum([p['countP'] for p in presences])
    total_absences = sum([p['countA'] for p in presences])

    context = {
        'nom': nom,
        'date_debut': date_debut.strftime('%Y-%m-%d'),
        'date_fin': date_fin.strftime('%Y-%m-%d'),
        'countP': total_presences,
        'countA': total_absences,
    }

    return render(request, 'rapport/rapport.html', context)
