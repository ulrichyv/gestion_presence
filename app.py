import cv2
import requests
import json
from pyzbar.pyzbar import decode
import tkinter as tk
from tkinter import messagebox
import numpy as np
import os
import sys

# Suppress warnings from pyzbar
sys.stderr = open(os.devnull, 'w')

# URL de ton API Django
API_URL = "http://127.0.0.1:8000/api/scan_qr_code/"  # Mets l'URL correcte ici

def scan_qr_code():
    print("Starting QR code scan...")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        messagebox.showerror("Erreur", "Impossible d'accéder à la webcam")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Erreur", "Impossible de lire la vidéo")
            break

        decoded_objects = decode(frame)
        for obj in decoded_objects:
            qr_data = obj.data.decode("utf-8")
            print(f"QR Code detected: {qr_data}")
            send_data_to_api(qr_data)
            messagebox.showinfo("QR Code Scanné", f"Contenu: {qr_data}")
            cap.release()
            return

        cv2.imshow("QR Code Scanner", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def send_data_to_api(qr_data):
    headers = {'Content-Type': 'application/json'}
    payload = json.dumps({"qr_data": qr_data})  # Vérifie bien la clé "qr_data"
    
    print(f"Envoi du payload : {payload}")  # Log du payload pour le débogage
    
    try:
        response = requests.post(API_URL, headers=headers, data=payload)
        print(f"Réponse du serveur : {response.status_code} - {response.text}")  # Log de la réponse du serveur
        response_data = response.json()
        if response.status_code == 201:
            messagebox.showinfo("Succès", response_data.get("message", "Présence enregistrée"))
        elif response.status_code == 200:
            messagebox.showinfo("Info", response_data.get("message", "Présence déjà enregistrée"))
        else:
            messagebox.showerror("Erreur", "Échec de l'envoi des données")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Erreur", f"Erreur de connexion : {e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Cacher la fenêtre principale de Tkinter
    scan_qr_code()
