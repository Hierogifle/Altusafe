# Documentation du Dossier `src`

## Vue d'ensemble

Ce dossier contient le cœur du projet Altusafe, une application de transcription médicale en temps réel. Il combine la reconnaissance vocale pour convertir la parole en texte, et un pipeline de traitement du langage naturel (NLP) pour nettoyer, corriger et formater ce texte pour un usage médical.

---

## Description des Fichiers

### 1. `nlp_pipeline.py`

*   **Quoi ?**
    Ce fichier est un module Python qui définit un pipeline de traitement (NLP) spécialisé pour le nettoyage et la correction de texte médical en français.

*   **Comment ?**
    Il définit la classe `MedicalNLPPipeline` qui applique une série d'étapes séquentielles :
    1.  **Normalisation** : Nettoyage des espaces et de la casse.
    2.  **Correction d'erreurs Vosk** : Corrige les fautes récurrentes spécifiques au modèle de reconnaissance vocale à l'aide d'un dictionnaire.
    3.  **Correction Orthographique** : Utilise un correcteur orthographique tout en protégeant une liste blanche de termes médicaux pour éviter les corrections erronées (ex: "auscultation").
    4.  **Ponctuation** : Ajoute une majuscule en début de phrase et un point final.
    Le pipeline peut être configuré selon trois modes : `fast`, `balanced`, ou `precise` pour privilégier la vitesse ou la qualité.

*   **Pourquoi ?**
    L'objectif est de transformer le texte brut et souvent imparfait généré par la reconnaissance vocale en un texte propre, cohérent et professionnel, directement utilisable pour la rédaction de rapports médicaux.

### 2. `realtime.py`

*   **Quoi ?**
    Un script Python pour effectuer une transcription audio en temps réel simple, sans correction.

*   **Comment ?**
    Il capture l'audio du microphone, le transmet au moteur de reconnaissance vocale Vosk et affiche le texte transcrit en direct dans la console.

*   **Pourquoi ?**
    Ce script sert d'outil de base pour tester les performances brutes du modèle Vosk sans aucun post-traitement. Il est utile pour évaluer la qualité de la transcription à la source.

### 3. `vosk_realtime_nlp.py`

*   **Quoi ?**
    Le script principal de l'application, qui intègre la reconnaissance vocale en temps réel avec le pipeline de correction NLP.

*   **Comment ?**
    Il fonctionne comme `realtime.py` pour la capture audio, mais chaque fois qu'une phrase est finalisée par Vosk, il la transmet immédiatement au `MedicalNLPPipeline` (défini dans `nlp_pipeline.py`). Il affiche ensuite le texte brut de Vosk, le texte final corrigé, ainsi qu'un résumé des corrections appliquées.

*   **Pourquoi ?**
    C'est le point d'entrée de la solution complète. Il fournit une dictée médicale corrigée et formatée en temps réel, combinant la vitesse de la reconnaissance vocale et la précision du traitement NLP.

### 4. `NLP_GUIDE.md`

*   **Quoi ?**
    Un guide technique et une documentation détaillée sur le fonctionnement du pipeline NLP.

*   **Comment ?**
    C'est un fichier Markdown qui explique l'architecture du pipeline, les instructions d'installation, les options de personnalisation (comment ajouter des termes médicaux, corriger de nouvelles erreurs Vosk) et le dépannage.

*   **Pourquoi ?**
    Pour permettre aux développeurs de comprendre, maintenir et étendre facilement le système de correction NLP. C'est la documentation de référence du projet.

---

## Comment Lancer l'Application

Pour utiliser l'application complète, exécutez le script `vosk_realtime_nlp.py`. Assurez-vous d'avoir installé toutes les dépendances listées dans `requirements.txt`.

```bash
# Assurez-vous que votre modèle Vosk est dans data/transcriptions_model/
python vosk_realtime_nlp.py
```
