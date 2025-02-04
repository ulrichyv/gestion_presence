from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    cni = models.CharField(max_length=20, unique=True)
    matricule = models.CharField(max_length=255, unique=True)
    fonction = models.CharField(max_length=255)
    path_qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    path_badge = models.ImageField(upload_to='badges/', blank=True, null=True)
    path_photo = models.ImageField(upload_to='photos/', blank=True, null=True)


class Presence(models.Model):
    STATUS_CHOICES = [
        ('P', 'Présent'),
        ('A', 'Absent'),
        ('R', 'Retard'),
        ('E', 'Exempté'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='presences')  # Ajout de related_name
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    heure_arrivee = models.TimeField(null=True, blank=True)
    heure_depart = models.TimeField(null=True, blank=True)
    commentaire = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-date']  # Trier par date décroissante

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.get_status_display()}"
