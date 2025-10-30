"""
Pipeline NLP pour normalisation et correction du texte issu de Vosk
Spécialisé pour le contexte médical français
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

# ============================================================================
# 1. DICTIONNAIRE MÉDICAL - WHITELIST
# ============================================================================
"""
Cette whitelist contient les termes médicaux importants à protéger.
Ils ne seront PAS corrigés ou modifiés par le correcteur orthographique.
À compléter avec votre vocabulaire spécifique selon le client.
"""

MEDICAL_WHITELIST = {
    # Actes et examens
    "auscultation", "palpation", "percussion", "ausculter",
    "auscultée", "ausculté", "palpée", "palpé",
    "échographie", "radiographie", "tomodensitométrie", "scanner",
    "IRM", "électrocardiogramme", "ECG", "EEG",
    
    # Pathologies courantes
    "hypertension", "diabète", "bronchite", "pneumonie",
    "arthrite", "arthrose", "angine", "rhinite",
    "gastro-entérite", "appendicite", "colique",
    
    # Termes génériques
    "consultation", "diagnostic", "traitement", "thérapie",
    "syndrome", "symptôme", "signe", "syndrome",
    "patient", "praticien", "médecin", "infirmier",
    "ordonnance", "prescription", "médicament",
    
    # Spécialités
    "cardiologie", "pneumologie", "gastro-entérologie",
    "neurologie", "rhumatologie", "ophtalmologie",
    
    # Procédures
    "intervention", "chirurgie", "anesthésie", "opération",
    "suture", "incision", "excision", "biopsie",
    
    # Signes vitaux
    "tension", "fréquence", "pression", "pouls",
    "température", "saturation", "glycémie",
    
    # Abréviations médicales (À COMPLETER)
    # "RCP", "VNI", "PEC", "HTA", "DM2",
}

# ============================================================================
# 2. DICTIONNAIRE DES ERREURS VOSK COURANTES
# ============================================================================
"""
Mappings des erreurs fréquemment commises par Vosk en français.
Format: "erreur_vosk" -> "correction"

Ces corrections sont appliquées AVANT la vérification orthographique
car ce sont des erreurs spécifiques à Vosk.
"""

VOSK_ERROR_MAPPINGS = {
    # Erreurs phonétiques courantes
    "bonjour": "bonjour",           # Si Vosk dit "bon jour" au lieu de "bonjour"
    "bonsoir": "bonsoir",
    "comment": "comment",
    "merci": "merci",
    
    # Nombres et chiffres
    "un": "un",
    "deux": "deux",
    "trois": "trois",
    "quatre": "quatre",
    "cinq": "cinq",
    "six": "six",
    "sept": "sept",
    "huit": "huit",
    "neuf": "neuf",
    "dix": "dix",
    
    # Mots médicaux spécifiques (erreurs Vosk connues)
    # À compléter avec vos observations
    # "ausculter": "ausculter",
    # "palpable": "palpable",
    
    # Connecteurs courants
    "et": "et",
    "ou": "ou",
    "donc": "donc",
    "mais": "mais",
    "car": "car",
    "cependant": "cependant",
    "toutefois": "toutefois",
}

# ============================================================================
# 3. CLASSE PRINCIPALE DU PIPELINE NLP
# ============================================================================

class MedicalNLPPipeline:
    """
    Pipeline NLP pour traiter le texte issu de Vosk.
    Gère normalisation, correction et ponctuation.
    """
    
    def __init__(self, use_spell_checker: bool = True, mode: str = "balanced"):
        """
        Initialise le pipeline NLP.
        
        Args:
            use_spell_checker (bool): Activer la correction orthographique
            mode (str): "fast" = vitesse, "precise" = qualité, "balanced" = mix
        """
        self.use_spell_checker = use_spell_checker
        self.mode = mode
        self.correction_log = []  # Stocke les corrections pour analyse
        
        # Charger le dictionnaire orthographique si activé
        if use_spell_checker:
            try:
                from spellchecker import SpellChecker
                self.spell_checker = SpellChecker(language='fr')
                print("✅ Correcteur orthographique chargé")
            except ImportError:
                print("⚠️  spellchecker non installé. Installez avec: pip install pyspellchecker")
                self.spell_checker = None
        else:
            self.spell_checker = None
        
        print(f"🔧 Pipeline NLP initialisé en mode '{mode}'")
    
    # ========================================================================
    # ÉTAPE 1: NORMALISATION DE BASE
    # ========================================================================
    
    def normalize_text(self, text: str) -> str:
        """
        Normalise le texte brut de Vosk.
        Gère espaces, caractères spéciaux, casse.
        
        Args:
            text (str): Texte brut à normaliser
            
        Returns:
            str: Texte normalisé
        """
        # Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        
        # Supprimer les espaces en début/fin
        text = text.strip()
        
        # Remplacer les tirets multiples par un seul
        text = re.sub(r'-+', '-', text)
        
        # Remplacer les points multiples par un seul
        text = re.sub(r'\.+', '.', text)
        
        # Minuscules pour cohérence (majuscules seront réappliquées)
        text = text.lower()
        
        return text
    
    # ========================================================================
    # ÉTAPE 2: CORRECTION DES ERREURS VOSK CONNUES
    # ========================================================================
    
    def fix_vosk_errors(self, text: str) -> Tuple[str, List[Dict]]:
        """
        Corrige les erreurs spécifiques à Vosk.
        
        Args:
            text (str): Texte normalisé
            
        Returns:
            Tuple: (texte corrigé, liste des corrections appliquées)
        """
        corrections = []
        words = text.split()
        corrected_words = []
        
        for word in words:
            # Vérifier si le mot a une erreur Vosk connue
            if word in VOSK_ERROR_MAPPINGS:
                corrected = VOSK_ERROR_MAPPINGS[word]
                if corrected != word:
                    corrections.append({
                        "original": word,
                        "corrigé": corrected,
                        "type": "vosk_error"
                    })
                    corrected_words.append(corrected)
            else:
                corrected_words.append(word)
        
        text_corrected = " ".join(corrected_words)
        return text_corrected, corrections
    
    # ========================================================================
    # ÉTAPE 3: CORRECTION ORTHOGRAPHIQUE INTELLIGENTE
    # ========================================================================
    
    def correct_spelling(self, text: str) -> Tuple[str, List[Dict]]:
        """
        Corrige les erreurs orthographiques.
        Protège les termes médicaux importants.
        
        Args:
            text (str): Texte à corriger
            
        Returns:
            Tuple: (texte corrigé, liste des corrections appliquées)
        """
        corrections = []
        
        # Si pas de correcteur, retourner le texte inchangé
        if not self.spell_checker:
            return text, corrections
        
        words = text.split()
        corrected_words = []
        
        for word in words:
            # Protéger les termes médicaux whitelistés
            if word in MEDICAL_WHITELIST:
                corrected_words.append(word)
                continue
            
            # Vérifier l'orthographe
            misspelled = self.spell_checker.unknown([word])
            
            if misspelled:
                # Le mot n'existe pas dans le dictionnaire
                # Chercher les corrections possibles
                candidates = self.spell_checker.correction(word)
                
                if candidates and candidates != word:
                    # Mode "fast": prendre la première suggestion
                    if self.mode == "fast":
                        correction = list(candidates)[0] if candidates else word
                    # Mode "precise": ignorer si trop d'incertitude
                    elif self.mode == "precise":
                        # Ne corriger que si très confiant
                        correction = word  # Laisser le mot tel quel
                    # Mode "balanced": prendre la meilleure suggestion
                    else:
                        correction = list(candidates)[0] if candidates else word
                    
                    if correction != word:
                        corrections.append({
                            "original": word,
                            "corrigé": correction,
                            "type": "orthographe",
                            "suggestions": list(candidates)[:3] if candidates else []
                        })
                        corrected_words.append(correction)
                    else:
                        corrected_words.append(word)
                else:
                    corrected_words.append(word)
            else:
                # Le mot est correct
                corrected_words.append(word)
        
        text_corrected = " ".join(corrected_words)
        return text_corrected, corrections
    
    # ========================================================================
    # ÉTAPE 4: AJOUT DE PONCTUATION
    # ========================================================================
    
    def add_punctuation(self, text: str) -> str:
        """
        Ajoute une ponctuation cohérente au texte.
        Ajoute une majuscule en début et un point en fin.
        
        Args:
            text (str): Texte à ponctuer
            
        Returns:
            str: Texte ponctué
        """
        if not text:
            return text
        
        # Mettre en majuscule le premier caractère
        text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()
        
        # Ajouter un point à la fin s'il n'y a pas déjà de ponctuation
        if text and text[-1] not in '.!?,;:':
            text += '.'
        
        return text
    
    # ========================================================================
    # ÉTAPE 5: SEGMENTATION EN PHRASES
    # ========================================================================
    
    def segment_sentences(self, text: str) -> List[str]:
        """
        Segmente le texte en phrases individuelles.
        Utile pour traitement phrase par phrase.
        
        Args:
            text (str): Texte à segmenter
            
        Returns:
            List[str]: Liste de phrases
        """
        # Diviser par les ponctuation finales
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Nettoyer et filtrer les phrases vides
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    # ========================================================================
    # PIPELINE COMPLET
    # ========================================================================
    
    def process(self, text: str, verbose: bool = False) -> Dict:
        """
        Applique le pipeline complet de NLP.
        
        Args:
            text (str): Texte brut de Vosk
            verbose (bool): Afficher les étapes
            
        Returns:
            Dict: Résultat avec texte final et métadonnées
        """
        self.correction_log = []
        
        if verbose:
            print(f"\n📝 Texte brut Vosk: '{text}'")
        
        # ÉTAPE 1: Normalisation
        text = self.normalize_text(text)
        if verbose:
            print(f"✓ Après normalisation: '{text}'")
        
        # ÉTAPE 2: Correction erreurs Vosk
        text, vosk_corrections = self.fix_vosk_errors(text)
        if verbose and vosk_corrections:
            print(f"✓ Après correction Vosk: '{text}'")
            for corr in vosk_corrections:
                print(f"   - {corr['original']} → {corr['corrigé']}")
        
        self.correction_log.extend(vosk_corrections)
        
        # ÉTAPE 3: Correction orthographique
        text, spelling_corrections = self.correct_spelling(text)
        if verbose and spelling_corrections:
            print(f"✓ Après correction orthographique: '{text}'")
            for corr in spelling_corrections:
                print(f"   - {corr['original']} → {corr['corrigé']}")
        
        self.correction_log.extend(spelling_corrections)
        
        # ÉTAPE 4: Ponctuation
        text_punctuated = self.add_punctuation(text)
        if verbose:
            print(f"✓ Après ponctuation: '{text_punctuated}'")
        
        # ÉTAPE 5: Segmentation (optionnel)
        sentences = self.segment_sentences(text_punctuated)
        
        # Résultat final
        result = {
            "texte_original": text,  # Avant ponctuation pour flexibilité
            "texte_final": text_punctuated,
            "sentences": sentences,
            "corrections_appliquées": self.correction_log,
            "nombre_corrections": len(self.correction_log),
            "mode": self.mode
        }
        
        if verbose:
            print(f"\n✅ Résultat final: '{text_punctuated}'")
            print(f"   Corrections appliquées: {len(self.correction_log)}")
        
        return result

# ============================================================================
# 6. FONCTION DE TEST
# ============================================================================

def test_pipeline():
    """
    Teste le pipeline NLP avec des exemples.
    """
    print("=" * 70)
    print("🧪 TEST DU PIPELINE NLP MÉDICAL")
    print("=" * 70)
    
    # Créer le pipeline
    nlp = MedicalNLPPipeline(use_spell_checker=True, mode="balanced")
    
    # Exemples de test
    test_cases = [
        "bonjour je suis venu pour une consultation",
        "jai fait une auscultation et jai remarquer une anomalie",
        "la patiente a une tension de 140 sur 90",
        "diagnostic probable diabète type 2",
        "ordonnance antibiotique et repos complet",
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n📌 Test {i}:")
        result = nlp.process(text, verbose=True)
        print("-" * 70)


# ============================================================================
# 7. INTÉGRATION AVEC VOSK (à ajouter à votre main.py)
# ============================================================================

"""
EXEMPLE D'INTÉGRATION AVEC VOSK:

from nlp_pipeline import MedicalNLPPipeline

# Initialiser le pipeline au démarrage
nlp = MedicalNLPPipeline(use_spell_checker=True, mode="balanced")

# Dans la boucle de reconnaissance:
if recognizer.AcceptWaveform(data):
    result_vosk = json.loads(recognizer.Result())
    text_brut = result_vosk.get('text', '')
    
    # Appliquer le pipeline NLP
    result_nlp = nlp.process(text_brut, verbose=False)
    text_final = result_nlp['texte_final']
    
    # Afficher le résultat nettoyé
    print(f"✅ [{timestamp}] Phrase {sentence_count}: {text_final}")
"""


if __name__ == "__main__":
    test_pipeline()
