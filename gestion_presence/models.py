from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    cni = models.CharField(max_length=20, unique=True)
    matricule = models.CharField(max_length=255, unique=True)
    fonction = models.CharField(max_length=255)
    path_qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True, max_length=255)
    path_badge = models.ImageField(upload_to='badges/', blank=True, null=True, max_length=255)
    path_photo = models.ImageField(upload_to='photos/', blank=True, null=True, max_length=255)
    qr_data = models.TextField(default='')  # Ajout d'une valeur par défaut
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, default='Null', blank=True, null=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        # Normalisation de l'email AVANT la sauvegarde
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)  # 📌 Ajout du super().save() pour sauvegarder l'utilisateur


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
