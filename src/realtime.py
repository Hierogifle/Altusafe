"""
Programme de reconnaissance vocale en temps réel avec Vosk
Capture l'audio du microphone et transcrit en texte en direct
"""

import sounddevice as sd
import numpy as np
from vosk import Model, KaldiRecognizer, SetLogLevel
import json
import queue
import os
from datetime import datetime
import sys

# Désactiver les logs de Vosk pour une sortie plus propre
SetLogLevel(-1)

# Chemin du modèle (adapter selon votre installation)
MODEL_PATH = "data/transcriptions_model/vosk-model-small-fr-0.22"

# Vérifier que le modèle existe
if not os.path.exists(MODEL_PATH):
    print(f"❌ Erreur: Le modèle {MODEL_PATH} n'existe pas")
    print("📥 Téléchargez-le depuis https://alphacephei.com/vosk/models")
    sys.exit(1)

# Charger le modèle Vosk
print("=" * 60)
print("🚀 Démarrage de la reconnaissance vocale")
print("=" * 60)
print("\n📦 Chargement du modèle Vosk...")
model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, 16000)
print("✅ Modèle chargé avec succès\n")

# Queue pour gérer l'audio de manière asynchrone
audio_queue = queue.Queue()

# Variables de suivi
sentence_count = 0
total_text = ""
last_partial = ""  # Tracker le dernier partiel pour éviter les répétitions

def audio_callback(indata, frames, time_info, status):
    """
    Callback appelé quand de l'audio est capturé du microphone
    
    Args:
        indata: Les données audio brutes
        frames: Le nombre de frames audio
        time_info: Informations temporelles
        status: État de la capture (erreurs éventuelles)
    """
    if status:
        print(f"⚠️  Avertissement audio: {status}")
    # Ajouter l'audio à la queue pour traitement
    audio_queue.put(bytes(indata))

def format_timestamp():
    """Retourne l'heure actuelle formatée"""
    return datetime.now().strftime("%H:%M:%S")

def main():
    """
    Boucle principale de reconnaissance vocale en temps réel
    Capture l'audio du microphone et transcrit en direct
    """
    global sentence_count, total_text, last_partial
    
    print("=" * 60)
    print("📋 COMMANDES:")
    print("=" * 60)
    print("  🎤 Parlez devant votre microphone")
    print("  ⏹️  Appuyez sur Ctrl+C pour ARRÊTER l'enregistrement")
    print("=" * 60)
    print()
    
    try:
        # Initialiser le flux audio du microphone
        print(f"⏺️  DÉBUT D'ENREGISTREMENT [{format_timestamp()}]")
        print("-" * 60)
        
        with sd.RawInputStream(
            samplerate=16000,      # Fréquence d'échantillonnage requise par Vosk
            blocksize=4096,        # RÉDUIT pour meilleure latence (était 8000)
            dtype='int16',         # Format audio (16-bit integer)
            channels=1,            # Mono
            callback=audio_callback,  # Fonction appelée quand de l'audio arrive
            latency='low'          # AJOUTÉ: Priorité à la latence basse
        ):
            while True:
                try:
                    # Récupérer l'audio de la queue avec timeout court
                    data = audio_queue.get(timeout=0.5)  # Réduit de 1 à 0.5 pour réactivité
                    
                    # Envoyer à Vosk et vérifier si on a un résultat final
                    if recognizer.AcceptWaveform(data):
                        # Résultat final (après une pause de Vosk)
                        result = json.loads(recognizer.Result())
                        text = result.get('text', '')
                        
                        if text:
                            sentence_count += 1
                            timestamp = format_timestamp()
                            print(f"\n✅ [{timestamp}] Phrase {sentence_count}: {text}")
                            total_text += text + " "
                            last_partial = ""  # Reset du partiel
                    else:
                        # Résultat partiel (en cours de transcription)
                        partial = json.loads(recognizer.PartialResult())
                        partial_text = partial.get('partial', '')
                        
                        # Afficher SEULEMENT si c'est différent du dernier (évite flickering)
                        if partial_text and partial_text != last_partial:
                            print(f"  💬 {partial_text}", end='\r', flush=True)
                            last_partial = partial_text
                
                except queue.Empty:
                    # Timeout normal, continuer
                    continue
    
    except KeyboardInterrupt:
        # L'utilisateur a appuyé sur Ctrl+C
        print("\n")
        print("-" * 60)
        print(f"⏹️  FIN D'ENREGISTREMENT [{format_timestamp()}]")
        print("=" * 60)
        print()
        
        # Afficher le résumé
        if sentence_count > 0:
            print("📊 RÉSUMÉ DE LA SESSION:")
            print(f"  • Nombre de phrases transcrites: {sentence_count}")
            print(f"  • Texte complet: {total_text.strip()}")
        else:
            print("⚠️  Aucun texte transcrit")
        
        print("\n✨ Programme terminé.")

if __name__ == "__main__":
    main()
