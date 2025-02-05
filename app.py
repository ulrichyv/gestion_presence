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

def draw_fixed_frame(frame):
    height, width, _ = frame.shape
    # Calculer les coordonnées du centre
    center_x, center_y = int(width / 2), int(height / 2)
    frame_height, frame_width = 200, 300  # Taille du cadre (ajustable)

    # Dessiner un rectangle autour du centre
    top_left = (center_x - frame_width // 2, center_y - frame_height // 2)
    bottom_right = (center_x + frame_width // 2, center_y + frame_height // 2)
    cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)

    # Ajouter un texte pour guider l'utilisateur
    cv2.putText(frame, "Positionnez le QR code dans le cadre", (50, height - 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

def update_ui(frame, qr_detected):
    height, width, _ = frame.shape
    if qr_detected:
        cv2.putText(frame, "QR Code détecté", (width // 4, height // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    else:
        cv2.putText(frame, "Positionnez le QR code dans le cadre", (width // 4, height // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

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

        draw_fixed_frame(frame)  # Afficher le cadre fixe
        qr_detected = False

        decoded_objects = decode(frame)
        for obj in decoded_objects:
            qr_data = obj.data.decode("utf-8")
            print(f"QR Code detected: {qr_data}")
            send_data_to_api(qr_data)
            qr_detected = True
            update_ui(frame, qr_detected)  # Afficher un message de succès
            messagebox.showinfo("QR Code Scanné", f"Contenu: {qr_data}")
            cap.release()
            break

        update_ui(frame, qr_detected)  # Si aucun QR code n'est détecté, afficher un message d'erreur
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
