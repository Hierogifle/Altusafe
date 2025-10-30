"""
Version améliorée de realtime.py avec pipeline NLP intégré
Combine reconnaissance vocale Vosk + correction NLP
"""

import sounddevice as sd
import numpy as np
from vosk import Model, KaldiRecognizer, SetLogLevel
import json
import queue
import os
from datetime import datetime
import sys

# Importer le pipeline NLP
from nlp_pipeline import MedicalNLPPipeline

# ============================================================================
# CONFIGURATION
# ============================================================================

# Désactiver les logs de Vosk pour une sortie plus propre
SetLogLevel(-1)

# Chemin du modèle
MODEL_PATH = "data/transcriptions_model/vosk-model-small-fr-0.22"

# Configuration NLP
NLP_MODE = "balanced"  # "fast", "balanced", ou "precise"
USE_SPELL_CHECKER = True

# Vérifier que le modèle existe
if not os.path.exists(MODEL_PATH):
    print(f"❌ Erreur: Le modèle {MODEL_PATH} n'existe pas")
    print("📥 Téléchargez-le depuis https://alphacephei.com/vosk/models")
    sys.exit(1)

# ============================================================================
# INITIALISATION
# ============================================================================

print("=" * 70)
print("🚀 Démarrage de la reconnaissance vocale avec NLP")
print("=" * 70)

# Charger le modèle Vosk
print("\n📦 Chargement du modèle Vosk...")
model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, 16000)
print("✅ Modèle Vosk chargé\n")

# Initialiser le pipeline NLP
print("🔧 Initialisation du pipeline NLP...")
nlp = MedicalNLPPipeline(use_spell_checker=USE_SPELL_CHECKER, mode=NLP_MODE)
print("✅ Pipeline NLP prêt\n")

# Queue pour gérer l'audio
audio_queue = queue.Queue()

# Variables de suivi
sentence_count = 0
total_text_original = ""  # Texte avant NLP
total_text_final = ""     # Texte après NLP
last_partial = ""
corrections_globales = []  # Toutes les corrections appliquées

# ============================================================================
# CALLBACKS ET FONCTIONS UTILITAIRES
# ============================================================================

def audio_callback(indata, frames, time_info, status):
    """
    Callback appelé quand de l'audio est capturé du microphone.
    Ajoute l'audio à la queue pour traitement asynchrone.
    """
    if status:
        print(f"⚠️  Avertissement audio: {status}")
    audio_queue.put(bytes(indata))

def format_timestamp():
    """Retourne l'heure actuelle au format HH:MM:SS"""
    return datetime.now().strftime("%H:%M:%S")

def print_correction_summary(corrections: list):
    """
    Affiche un résumé des corrections NLP appliquées.
    
    Args:
        corrections: Liste des corrections appliquées par le NLP
    """
    if not corrections:
        return
    
    print("\n   📊 Corrections NLP appliquées:")
    for corr in corrections:
        if corr['type'] == 'vosk_error':
            print(f"      • Erreur Vosk: '{corr['original']}' → '{corr['corrigé']}'")
        elif corr['type'] == 'orthographe':
            print(f"      • Orthographe: '{corr['original']}' → '{corr['corrigé']}'")

# ============================================================================
# BOUCLE PRINCIPALE
# ============================================================================

def main():
    """
    Boucle principale de reconnaissance vocale avec NLP.
    """
    global sentence_count, total_text_original, total_text_final
    global last_partial, corrections_globales
    
    print("=" * 70)
    print("📋 COMMANDES:")
    print("=" * 70)
    print("  🎤 Parlez devant votre microphone")
    print("  ⏹️  Appuyez sur Ctrl+C pour ARRÊTER l'enregistrement")
    print("=" * 70)
    print()
    
    try:
        # Initialiser le flux audio
        print(f"⏺️  DÉBUT D'ENREGISTREMENT [{format_timestamp()}]")
        print("-" * 70)
        
        with sd.RawInputStream(
            samplerate=16000,           # Fréquence requise par Vosk
            blocksize=4096,             # Optimisé pour latence basse
            dtype='int16',
            channels=1,
            callback=audio_callback,
            latency='low'
        ):
            while True:
                try:
                    # Récupérer l'audio avec timeout court
                    data = audio_queue.get(timeout=0.5)
                    
                    # ================================================================
                    # ÉTAPE 1: RECONNAISSANCE VOSK
                    # ================================================================
                    
                    if recognizer.AcceptWaveform(data):
                        # Résultat FINAL de Vosk
                        result_vosk = json.loads(recognizer.Result())
                        text_vosk_raw = result_vosk.get('text', '')
                        
                        if text_vosk_raw:
                            # ================================================
                            # ÉTAPE 2: PIPELINE NLP
                            # ================================================
                            
                            # Appliquer le pipeline NLP
                            result_nlp = nlp.process(text_vosk_raw, verbose=False)
                            text_final = result_nlp['texte_final']
                            corrections = result_nlp['corrections_appliquées']
                            
                            # Mettre à jour les totaux
                            sentence_count += 1
                            timestamp = format_timestamp()
                            total_text_original += text_vosk_raw + " "
                            total_text_final += text_final + " "
                            corrections_globales.extend(corrections)
                            
                            # ================================================
                            # ÉTAPE 3: AFFICHAGE DU RÉSULTAT
                            # ================================================
                            
                            # Afficher le texte brut Vosk (optionnel)
                            print(f"\n   📝 Vosk (brut): {text_vosk_raw}")
                            
                            # Afficher le texte final NLP
                            print(f"✅ [{timestamp}] Phrase {sentence_count}: {text_final}")
                            
                            # Afficher les corrections appliquées
                            if corrections:
                                print_correction_summary(corrections)
                            
                            last_partial = ""  # Reset du partiel
                    
                    else:
                        # Résultat PARTIEL de Vosk
                        partial_vosk = json.loads(recognizer.PartialResult())
                        partial_text_vosk = partial_vosk.get('partial', '')
                        
                        if partial_text_vosk and partial_text_vosk != last_partial:
                            # Appliquer une normalisation légère au partiel
                            partial_normalized = nlp.normalize_text(partial_text_vosk)
                            print(f"  💬 {partial_normalized}", end='\r', flush=True)
                            last_partial = partial_text_vosk
                
                except queue.Empty:
                    # Timeout normal, continuer
                    continue
    
    except KeyboardInterrupt:
        # L'utilisateur a appuyé sur Ctrl+C
        print("\n")
        print("-" * 70)
        print(f"⏹️  FIN D'ENREGISTREMENT [{format_timestamp()}]")
        print("=" * 70)
        print()
        
        # ====================================================================
        # AFFICHAGE DU RÉSUMÉ FINAL
        # ====================================================================
        
        if sentence_count > 0:
            print("📊 RÉSUMÉ DE LA SESSION:")
            print(f"   • Nombre de phrases transcrites: {sentence_count}")
            print(f"   • Nombre de corrections NLP: {len(corrections_globales)}")
            
            # Afficher les statistiques par type de correction
            correction_types = {}
            for corr in corrections_globales:
                corr_type = corr.get('type', 'autre')
                correction_types[corr_type] = correction_types.get(corr_type, 0) + 1
            
            if correction_types:
                print("   • Détail des corrections:")
                for corr_type, count in correction_types.items():
                    print(f"      - {corr_type}: {count}")
            
            print("\n   📝 TEXTE BRUT (avant NLP):")
            print(f"      {total_text_original.strip()}")
            
            print("\n   ✨ TEXTE FINAL (après NLP):")
            print(f"      {total_text_final.strip()}")
        else:
            print("⚠️  Aucun texte transcrit")
        
        print("\n✨ Programme terminé.")

# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    main()
