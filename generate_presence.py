from datetime import datetime, timedelta, time, date
import random
from gestion_presence.models import User, Presence  # Remplace 'core' par le nom de ton app

# Récupérer tous les utilisateurs
users = User.objects.all()

# Début du mois courant jusqu'à aujourd'hui
today = date.today()
first_day = date(today.year, today.month, 1)
days = [first_day + timedelta(days=i) for i in range((today - first_day).days + 1)]

# Nettoyage préalable (optionnel si tu veux régénérer)
# Presence.objects.filter(date__range=(first_day, today)).delete()

for user in users:
    for day in days:
        # Ne pas générer pour les week-ends
        if day.weekday() >= 5:  # 5 = samedi, 6 = dimanche
            continue
        
        status = random.choices(['P', 'R', 'A'], weights=[0.6, 0.3, 0.1])[0]  # P:60%, R:30%, A:10%
        
        if status == 'A':
            Presence.objects.create(user=user, date=day, status='A')
        else:
            # Générer heure d'arrivée et départ selon le statut
            heure_arrivee = (
                time(hour=random.randint(7, 8), minute=random.randint(0, 59)) if status == 'P'
                else time(hour=random.randint(8, 9), minute=random.randint(30, 59))
            )
            heure_depart = time(hour=random.randint(15, 17), minute=random.randint(0, 59))

            Presence.objects.create(
                user=user,
                date=day,
                status=status,
                heure_arrivee=heure_arrivee,
                heure_depart=heure_depart
            )

print("🎉 Données de présence générées avec succès !")
