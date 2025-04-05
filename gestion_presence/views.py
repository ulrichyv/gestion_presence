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
from django.db.models import F, ExpressionWrapper, fields
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from .models import User, Presence
from django.shortcuts import render
from datetime import datetime
from django.db.models import Count, Case, When, IntegerField
from django.db.models.functions import TruncDay
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model

import logging

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, time
from .models import User, Presence

@api_view(['POST'])
def scan_qr_code(request):
    try:
        # Récupérer les données JSON envoyées par le QR Code
        qr_data = request.data.get('qr_data')
        print(f"Données reçues : {qr_data}")  # Log des données reçues pour le débogage
        
        if not qr_data:
            return Response({'message': 'Données QR manquantes'}, status=status.HTTP_400_BAD_REQUEST)

        # Supposons que le QR Code contient des données JSON comme {"nom": "John", "matricule": "1234"}
        try:
            qr_info = json.loads(qr_data)  # Essayer de parser les données JSON
            nom = qr_info.get('nom')
            matricule = qr_info.get('matricule')

            if not nom or not matricule:
                return Response({'message': 'Données QR invalides'}, status=status.HTTP_400_BAD_REQUEST)
            
        except json.JSONDecodeError:
            return Response({'message': 'Le QR Code n\'est pas un JSON valide'}, status=status.HTTP_400_BAD_REQUEST)

        # Vérifier si l'utilisateur existe
        user = User.objects.get(matricule=matricule)

        # Récupérer l'heure actuelle
        now = datetime.now()
        current_time = now.time()

        # Vérifier s'il y a déjà une présence aujourd'hui
        today = now.date()
        presence, created = Presence.objects.get_or_create(
            user=user,
            date=today,
            defaults={'status': 'P'}
        )

        # Déterminer si c'est une heure d'arrivée ou de départ
        if current_time < time(14, 0):  # Avant 14h
            if not presence.heure_arrivee:
                presence.heure_arrivee = current_time
                presence.save()
                return Response({'message': f'{nom} est marqué comme présent à {presence.heure_arrivee}'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': f'{nom} est déjà marqué comme arrivé aujourd\'hui.'}, status=status.HTTP_200_OK)
        
        else:  # Après 14h (heure de départ)
            if not presence.heure_depart:
                presence.heure_depart = current_time
                presence.save()
                return Response({'message': f'{nom} est marqué comme parti à {presence.heure_depart}'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': f'{nom} est déjà marqué comme parti aujourd\'hui.'}, status=status.HTTP_200_OK)

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

  # Assure-toi que User est bien importé



logger = logging.getLogger(__name__)

import os
import random
import qrcode
import json
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

def generer_badge(request):
    if request.method == "POST":
        nom = request.POST.get("nom")
        prenom = request.POST.get("prenom")
        fonction = request.POST.get("fonction")
        matricule = request.POST.get("matricule")
        cni = request.POST.get("cni")
        photo = request.FILES.get("photo")
        mail=request.POST.get("email")
        password=request.POST.get("password")
       

        # Validation des champs
        if not all([nom, prenom, fonction, matricule, cni, photo]):
            messages.error(request, "Tous les champs et la photo doivent être remplis.")
            return redirect("formulaire")

        # Sauvegarde de la photo
        fs = FileSystemStorage()
        photo_filename = f"photos/{nom}_{prenom}.jpg".replace(" ", "_")
        photo_path = fs.save(photo_filename, photo)
        photo_url = fs.url(photo_path)
        print(f"Photo sauvegardée : {photo_url}")

        # Génération du QR code
        qr_data = {
            "nom": nom,
            "prenom": prenom,
            "matricule": matricule,
            "fonction": fonction,
            "cni": cni
        }
        qr_json = json.dumps(qr_data)

        # Génération et sauvegarde du QR Code
        qr = qrcode.make(qr_json)
        qr_filename = f"qr_codes/qr_{nom}_{prenom}.png".replace(" ", "_")
        qr_path = os.path.join(settings.MEDIA_ROOT, qr_filename)
        os.makedirs(os.path.dirname(qr_path), exist_ok=True)
        qr.save(qr_path)
        qr_url = fs.url(qr_filename)
        print(f"QR code généré : {qr_url}")

        # Rendu du HTML
        badge_html = render_to_string(
            "badge.html",
            {
                "nom": nom,
                "prenom": prenom,
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
            user = User.objects.create_user(
                username=username,  # Ajout du username unique
                first_name=nom,
                last_name=prenom,
                cni=cni,
                matricule=matricule,
                fonction=fonction,
                email=mail,
                password=password,
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
        return redirect("accueil/")

    return render(request, "create_badge_form.html")



def presence(request):
    return render(request, 'presence.html')

def login(request):
    return render(request, 'auth.html')

from datetime import datetime
from django.utils import timezone
from django.db.models import Sum, Case, When, Value, F, ExpressionWrapper, DurationField
from django.db.models.functions import TruncDay
from django.shortcuts import render
from .models import Presence

from datetime import timedelta
from datetime import datetime, timedelta

def rapport(request):
    """ Génère un rapport pour tous les employés ou un employé spécifique. """

    # Récupération des données du formulaire
    nom = request.POST.get("nom", "").strip()
    date_debut = request.POST.get("Date_deb", None)
    date_fin = request.POST.get("Date_fin", None)

    # Si aucune date n'est fournie, on prend le mois en cours
    today = timezone.now()
    if not date_debut or not date_fin:
        date_debut = today.replace(day=1)  # Premier jour du mois
        date_fin = today  # Aujourd'hui
    else:
        date_debut = timezone.make_aware(datetime.strptime(date_debut, '%Y-%m-%d'))
        date_fin = timezone.make_aware(datetime.strptime(date_fin, '%Y-%m-%d'))

    # Heures standard de travail (7h30 à 17h30)
    heure_arrivee_standard = timedelta(hours=7, minutes=30)
    heure_depart_standard = timedelta(hours=17, minutes=30)
    
    # Récupérer toutes les présences
    presences = Presence.objects.filter(
        user__first_name__icontains=nom,
        date__range=[date_debut, date_fin]
    ).order_by('user__first_name', 'date')

    # Regrouper les données par employé
    employes = {}
    for presence in presences:
        employe = presence.user.first_name  # Utilisation de l'utilisateur plutôt que de 'user__first_name'
        
        if employe not in employes:
            employes[employe] = {'jours': [], 'totalP': 0, 'totalA': 0, 'total_heures': 0, 'total_heures_sup': 0, 'total_heures_absence': 0}

        # Vérifier si heure_arrivee et heure_depart ne sont pas None avant d'y accéder
        if presence.heure_arrivee and presence.heure_depart:
            # Convertir heure_arrivee et heure_depart en datetime pour effectuer des soustractions
            min_date = datetime.min  # Date fictive (date minimum)
            
            # Création de datetime à partir de l'heure pour les calculs
            heure_arrivee = datetime.combine(min_date, presence.heure_arrivee)
            heure_depart = datetime.combine(min_date, presence.heure_depart)

            # Calcul des heures d'absence et heures supplémentaires
            heures_absence = timedelta(0)
            heures_sup = timedelta(0)

            # Comparer l'heure d'arrivée et l'heure standard de départ
            if heure_arrivee > (datetime.combine(min_date, datetime.min.time()) + heure_arrivee_standard):  # Arrivée en retard
                heures_absence = heure_arrivee - (datetime.combine(min_date, datetime.min.time()) + heure_arrivee_standard)

            if heure_depart < (datetime.combine(min_date, datetime.min.time()) + heure_depart_standard):  # Départ avant l'heure normale
                heures_absence += (datetime.combine(min_date, datetime.min.time()) + heure_depart_standard) - heure_depart

            if heure_depart > (datetime.combine(min_date, datetime.min.time()) + heure_depart_standard):  # Heures supplémentaires si départ après 17h30
                heures_sup = heure_depart - (datetime.combine(min_date, datetime.min.time()) + heure_depart_standard)

            # Mise à jour des totaux
            employes[employe]['jours'].append({
                'date': presence.date.strftime('%Y-%m-%d'),
                'presences': 1 if presence.status == 'P' else 0,
                'absences': 1 if presence.status == 'A' else 0,
                'heures_absence': round(heures_absence.total_seconds() / 3600, 2),  # Convertir en heures
                'heures_sup': round(heures_sup.total_seconds() / 3600, 2)  # Convertir en heures supplémentaires
            })

            employes[employe]['totalP'] += 1 if presence.status == 'P' else 0
            employes[employe]['totalA'] += 1 if presence.status == 'A' else 0
            employes[employe]['total_heures'] += (heure_depart - heure_arrivee).total_seconds() / 3600  # Heures travaillées
            employes[employe]['total_heures_absence'] += heures_absence.total_seconds() / 3600
            employes[employe]['total_heures_sup'] += heures_sup.total_seconds() / 3600
        else:
            # Si heure_arrivee ou heure_depart sont None, on considère comme absence totale ou exempté
            employes[employe]['jours'].append({
                'date': presence.date.strftime('%Y-%m-%d'),
                'presences': 0,
                'absences': 1,
                'heures_absence': 8.0,  # On peut supposer une absence complète de 8 heures
                'heures_sup': 0
            })
            employes[employe]['totalA'] += 1
            employes[employe]['total_heures_absence'] += 8.0  # Absence totale

    context = {
        'date_debut': date_debut.strftime('%Y-%m-%d'),
        'date_fin': date_fin.strftime('%Y-%m-%d'),
        'employes': employes,
    }
    return render(request, 'rapport/rapport.html', context)



from django.contrib.auth import authenticate
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import get_backends

from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import redirect, render

def process_login(request):
    if request.method == "POST":
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '').strip()

        print(f"Tentative de connexion : {email} | {password}")

        # Vérifiez si l'utilisateur existe dans la base de données
        try:
            user = User.objects.get(email=email)
            print(f"Utilisateur trouvé : {user}")
            print(f"Mot de passe valide : {user.check_password(password)}")
        except User.DoesNotExist:
            print("Utilisateur non trouvé")
            messages.error(request, 'Identifiants invalides. Vérifiez votre adresse mail ou mot de passe.')
            return render(request, 'auth.html')

        # Authentifiez l'utilisateur
        user = authenticate(request, email=email, password=password)
        print(f"Utilisateur authentifié : {user}")

        if user is not None:
            auth_login(request, user)
            messages.success(request, f'Bienvenue, {user.get_full_name()}!')
            return redirect('accueil/')  # Redirigez vers la page d'accueil
        else:
            messages.error(request, 'Identifiants invalides. Vérifiez votre adresse mail ou mot de passe.')
            return render(request, 'auth.html')

    return redirect('/')

from django.contrib.auth import logout as auth_logout

def logout_user(request):
    auth_logout(request)
    messages.success(request, 'Vous avez été déconnecté.')
    return redirect('/')