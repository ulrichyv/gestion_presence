"""
URL configuration for gestion_presence project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from gestion_presence import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
   path('admin/', admin.site.urls),
    path('accueil/', views.index, name='index'),
    path('report', views.report, name='report'),
    path('formulaire', views.formulaire, name='formulaire'),
    path('generer_badge', views.generer_badge, name='generer_badge'),
    path('presence', views.presence, name='presence'),
    path('rapport', views.rapport, name='rapport'),
    path('', views.login, name='login'),
    path('api/scan_qr_code/', views.scan_qr_code, name='scan-qr-code'),
    path('process_login', views.process_login, name='process_login'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
