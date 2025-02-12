import cv2
import requests
import json
from pyzbar.pyzbar import decode
import tkinter as tk
from tkinter import messagebox
import numpy as np
import os
import sys
from datetime import datetime  # Import pour la date

# Suppress warnings from pyzbar
sys.stderr = open(os.devnull, 'w')

# URL de ton API Django
API_URL = "http://127.0.0.1:8000/api/scan_qr_code/"

def draw_fixed_frame(frame):
    """Dessine un cadre vert au centre pour guider l'utilisateur."""
    height, width, _ = frame.shape
    center_x, center_y = int(width / 2), int(height / 2)
    frame_height, frame_width = 200, 300  

    # Dessiner un rectangle autour du centre
    top_left = (center_x - frame_width // 2, center_y - frame_height // 2)
    bottom_right = (center_x + frame_width // 2, center_y + frame_height // 2)
    cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)

    # Ajouter un texte pour guider l'utilisateur
    cv2.putText(frame, "Positionnez le QR code dans le cadre", (50, height - 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

def update_ui(frame, qr_detected):
    """Met à jour l'affichage en fonction de la détection du QR Code."""
    height, width, _ = frame.shape
    if qr_detected:
        cv2.putText(frame, "QR Code détecté", (width // 4, height // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    else:
        cv2.putText(frame, "Positionnez le QR code dans le cadre", (width // 4, height // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

def save_photo(frame, employee_name):
    """Capture et enregistre la photo de l'employé avec son nom et la date."""
    folder = "photos_employes"
    if not os.path.exists(folder):
        os.makedirs(folder)  # Créer le dossier s'il n'existe pas
    
    today = datetime.today().strftime('%Y-%m-%d')  # Récupérer la date d'aujourd'hui
    filename = f"{employee_name}_{today}.jpg"  # Format du fichier
    file_path = os.path.join(folder, filename)
    
    cv2.imwrite(file_path, frame)  # Enregistrer l'image
    print(f"Photo enregistrée : {file_path}")
    return file_path

def send_data_to_api(qr_data):
    """Envoie les données du QR Code à l'API Django."""
    headers = {'Content-Type': 'application/json'}
    payload = json.dumps({"qr_data": qr_data})

    print(f"Envoi du payload : {payload}")

    try:
        response = requests.post(API_URL, headers=headers, data=payload)
        print(f"Réponse du serveur : {response.status_code} - {response.text}")

        response_data = response.json()
        if response.status_code == 201:
            messagebox.showinfo("Succès", response_data.get("message", "Présence enregistrée"))
        elif response.status_code == 200:
            messagebox.showinfo("Info", response_data.get("message", "Présence déjà enregistrée"))
        else:
            messagebox.showerror("Erreur", "Échec de l'envoi des données")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Erreur", f"Erreur de connexion : {e}")

def scan_qr_code():
    """Active la caméra, détecte un QR Code, envoie les données et enregistre une photo."""
    print("Démarrage du scanner QR Code...")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        messagebox.showerror("Erreur", "Impossible d'accéder à la webcam")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Erreur", "Impossible de lire la vidéo")
            break

        draw_fixed_frame(frame)
        qr_detected = False

        decoded_objects = decode(frame)
        for obj in decoded_objects:
            qr_data = obj.data.decode("utf-8")  # QR Code en texte brut

            try:
                qr_info = json.loads(qr_data)  # Convertir en JSON
                employee_name = qr_info.get("nom", "inconnu")  # Récupérer le nom
                print(f"QR Code détecté : {qr_info}")
            except json.JSONDecodeError:
                messagebox.showerror("Erreur", "Format du QR Code invalide")
                continue

            # 📸 Capture et enregistre la photo avec le nom et la date
            photo_path = save_photo(frame, employee_name)

            # 🔗 Envoi des données à l'API
            send_data_to_api(qr_data)

            qr_detected = True
            update_ui(frame, qr_detected)
            messagebox.showinfo("Succès", f"QR Code : {qr_info}\nPhoto enregistrée à {photo_path}")
            
            cap.release()
            break

        update_ui(frame, qr_detected)
        cv2.imshow("QR Code Scanner", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def launch_scanner():
    """Lance le scanner en cliquant sur un bouton Tkinter."""
    scan_qr_code()

# Interface graphique avec Tkinter
root = tk.Tk()
root.title("Scanner QR Code")

# Taille de la fenêtre
root.geometry("400x300")

# Label d'instructions
label = tk.Label(root, text="Cliquez sur le bouton pour scanner un QR Code", font=("Arial", 12))
label.pack(pady=20)

# Bouton pour lancer le scanner
scan_button = tk.Button(root, text="Scanner QR Code", command=launch_scanner, font=("Arial", 14), bg="green", fg="white")
scan_button.pack(pady=20)

# Bouton pour quitter
exit_button = tk.Button(root, text="Quitter", command=root.quit, font=("Arial", 14), bg="red", fg="white")
exit_button.pack(pady=10)

# Lancer l'interface Tkinter
root.mainloop()
