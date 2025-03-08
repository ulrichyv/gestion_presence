import random
from django.utils import timezone
from gestion_presence.models import User, Presence

# Vérifier si des utilisateurs existent
users = User.objects.all()
print(f"{users.count()} utilisateurs trouvés.")

# Définir les statuts possibles
STATUS_CHOICES = ['P', 'A', 'R', 'E']  # Présent, Absent, Retard, Exempté

# Générer les présences
for user in users:
    for day in range(1, 11):  # Générer des présences sur 10 jours
        date = timezone.now().date() - timezone.timedelta(days=day)

        # Vérifier si une présence existe déjà
        if not Presence.objects.filter(user=user, date=date).exists():
            Presence.objects.create(
                user=user,
                date=date,
                status=random.choice(STATUS_CHOICES),
                heure_arrivee=timezone.now().replace(
                    hour=random.randint(6, 10), 
                    minute=random.randint(0, 59)
                ).time() if random.choice([True, False]) else None,
                heure_depart=timezone.now().replace(
                    hour=random.randint(15, 19), 
                    minute=random.randint(0, 59)
                ).time() if random.choice([True, False]) else None
            )

print("Présences enregistrées avec succès.")
