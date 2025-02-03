from django.db import models
from django.contrib.auth.models import User

class Presence(models.Model):
    STATUS_CHOICES = [
        ('P', 'Présent'),
        ('A', 'Absent'),
        ('R', 'Retard'),
        ('E', 'Exempté'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Employé
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    heure_arrivee = models.TimeField(null=True, blank=True)
    heure_depart = models.TimeField(null=True, blank=True)
    commentaire = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.get_status_display()}"
