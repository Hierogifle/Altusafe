# 📖 Guide Complet - Pipeline NLP Médical

## 📋 Table des matières

1. [Architecture générale](#architecture-générale)
2. [Installation](#installation)
3. [Utilisation](#utilisation)
4. [Comprendre chaque étape du NLP](#comprendre-chaque-étape-du-nlp)
5. [Paramètres de performance](#paramètres-de-performance)
6. [Customisation](#customisation)
7. [Dépannage](#dépannage)

---

## 🏗️ Architecture générale

```
Audio brut → VOSK (texte brut) → NLP Pipeline → Texte cohérent
                                  ├─ Normalisation
                                  ├─ Correction Vosk
                                  ├─ Correction orthographique
                                  ├─ Ponctuation
                                  └─ Segmentation
```

---

## 💾 Installation

### 1. Installer la dépendance NLP

```bash
pip install pyspellchecker
```

### 2. Mettre à jour requirements.txt

```bash
pip freeze > requirements.txt
```

---

## 🚀 Utilisation

### Lancer directement avec NLP

```bash
python realtime_nlp.py
```

Vous verrez :

```
⏺️  DÉBUT D'ENREGISTREMENT [14:32:15]
  💬 j ai fais
  💬 j ai fais une auscultation
   📝 Vosk (brut): jai fais une auscultation
✅ [14:32:18] Phrase 1: J'ai fait une auscultation.
   📊 Corrections NLP appliquées:
      • Orthographe: 'fais' → 'fait'
```

---

## 🔍 Les 5 étapes du NLP

### Étape 1: NORMALISATION

Nettoie le texte brut de Vosk :
- Supprime les espaces multiples
- Supprime les espaces en début/fin
- Convertit en minuscules

**Exemple** :
```
"  Bonjour  COMMENT  " → "bonjour comment"
```

---

### Étape 2: CORRECTION ERREURS VOSK

Corrige les erreurs spécifiques à Vosk en utilisant un dictionnaire.

**Ajouter une erreur** dans `nlp_pipeline.py` :

```python
VOSK_ERROR_MAPPINGS = {
    "votre_erreur": "correction",
    "osculter": "ausculter",
}
```

---

### Étape 3: CORRECTION ORTHOGRAPHIQUE

Corrige les fautes d'orthographe SAUF pour les termes médicaux protégés.

**Termes protégés** (ne sont jamais corrigés) :

```python
MEDICAL_WHITELIST = {
    "auscultation",
    "diabète",
    "hypertension",
    # À compléter
}
```

**Ajouter un terme** :

```python
MEDICAL_WHITELIST.add("votre_terme_médical")
```

**Exemple** :
```
"jai une febvre" → "j'ai une fièvre"
"jai une auscultation" → "j'ai une auscultation" (protégé!)
```

---

### Étape 4: PONCTUATION

Ajoute majuscule au début et point à la fin.

**Exemple** :
```
"bonjour comment ça va" → "Bonjour comment ça va."
```

---

### Étape 5: SEGMENTATION

Divise le texte en phrases individuelles.

**Exemple** :
```
"Bonjour. Comment ça va?" → ["Bonjour.", "Comment ça va?"]
```

---

## ⚡ Paramètres de performance

### POUR PLUS DE VITESSE (temps réel)

Dans `vosk_realtime_nlp.py` :

```python
NLP_MODE = "fast"              # Plus rapide
blocksize = 8192               # Plus grand = moins latent
timeout = 0.25                 # Moins d'attente
```

**Résultat** : +30% vitesse, -10% qualité

---

### POUR PLUS DE QUALITÉ (rapports médicaux)

Dans `vosk_realtime_nlp.py` :

```python
NLP_MODE = "precise"           # Plus prudent
blocksize = 2048               # Plus petit = plus stable
timeout = 1.0                  # Plus d'attente
```

**Résultat** : -30% vitesse, +20% qualité

---

### LES 3 MODES EXPLIQUÉS

| Mode | Comportement | Cas d'usage |
|------|-------------|-----------|
| `"fast"` | Prend première suggestion | Temps réel strict |
| `"balanced"` | Bon équilibre | **Recommandé** |
| `"precise"` | Valide à 100% avant correction | Rapports critiques |

---

## 🛠️ Customisation

### Ajouter un terme médical

Dans `nlp_pipeline.py`, section `MEDICAL_WHITELIST` :

```python
MEDICAL_WHITELIST = {
    # ... existants ...
    "thermo-ablation",
    "VNI",
    "RCP",
}
```

### Ajouter une erreur Vosk

Dans `nlp_pipeline.py`, section `VOSK_ERROR_MAPPINGS` :

```python
VOSK_ERROR_MAPPINGS = {
    # ... existants ...
    "ausculter": "ausculter",
    "palpable": "palpable",
}
```

### Charger un corpus de termes

Créez `medical_terms.json` :

```json
{
  "actes": ["auscultation", "palpation"],
  "pathologies": ["diabète", "hypertension"],
  "medicaments": ["aspirine", "ibuprofène"]
}
```

---

## 📊 Accéder aux corrections

```python
from nlp_pipeline import MedicalNLPPipeline

nlp = MedicalNLPPipeline(mode="balanced")
result = nlp.process("jai une toux")

# Voir les corrections
for correction in result['corrections_appliquées']:
    print(f"{correction['original']} → {correction['corrigé']}")
```

---

## 🐛 Dépannage

### "ModuleNotFoundError: No module named 'spellchecker'"

```bash
pip install pyspellchecker
```

### Les termes médicaux se font corriger

**Solution** : Les ajouter à `MEDICAL_WHITELIST`

```python
MEDICAL_WHITELIST.add("votre_terme")
```

### Trop lent

**Solution** : Mode "fast"

```python
NLP_MODE = "fast"
```

### Pas assez précis

**Solution** : Mode "precise"

```python
NLP_MODE = "precise"
```

---

## ✅ Checklist de démarrage

- [ ] `pip install pyspellchecker`
- [ ] Copier `nlp_pipeline.py` dans `Altusafe/`
- [ ] Copier `vosk_realtime_nlp.py` dans `Altusafe/`
- [ ] Lancer `python vosk_realtime_nlp.py`
- [ ] Noter les erreurs Vosk observées
- [ ] Ajouter les termes médicaux importants

---

**C'est prêt !** 🚀
