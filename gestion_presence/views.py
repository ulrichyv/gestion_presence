from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import User , Presence
from django.contrib import messages
from django.core.files.storage import default_storage
from html2image import Html2Image
from .services import BadgeService


def index(request):
    return render(request, 'index.html')

def report(request):
    return render(request, 'report.html')
def formulaire(request):
    return render(request, 'formulaire.html')

def generer_badge_view(request):
    if request.method == "POST":
        try:
            badge_service = BadgeService(
                nom=request.POST.get("nom", ""),
                prenom=request.POST.get("prenom", ""),
                fonction=request.POST.get("fonction", ""),
                matricule=request.POST.get("matricule", ""),
                cni=request.POST.get("cni", ""),
                photo_path=request.FILES.get("photo")
            )

            # Vérifier si tous les champs sont remplis
            if not all([badge_service.nom, badge_service.prenom, badge_service.fonction, 
                        badge_service.matricule, badge_service.cni, badge_service.photo_path]):
                messages.error(request, "Tous les champs et la photo doivent être remplis.")
                return render(request, 'formulaire.html')  # Renvoie à la page de formulaire

            # Générer le badge avec QR Code
            image_url = badge_service.generate_badge()
            photo_url = badge_service.save_photo()  # Enregistre la photo
            qr_code_url = badge_service.generate_qr_code()
            user = User.objects.create(
                username=request.POST.get("nom"),  # Utiliser le matricule comme nom d'utilisateur
                lastname=request.POST.get("prenom"),
                matricule=request.POST.get("matricule"),
                cni=request.POST.get("cni"),
                fonction=request.POST.get("fonction"),
                path_photo=photo_url,
                path_qr_code=qr_code_url,
                path_badge=image_url
            )

            messages.success(request, "Badge généré avec succès!")
            return redirect('')

        except Exception as e:
            messages.error(request, f"Erreur lors de la génération du badge: {str(e)}")
            return render(request, 'formulaire.html')  # Renvoie à la page de formulaire

    messages.error(request, "Méthode non autorisée.")
    return render(request, 'ton_template.html')