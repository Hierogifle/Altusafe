# Interprétation des métriques STT

Ce document explique les métriques calculées pour chaque modèle de reconnaissance vocale (STT) et comment les interpréter pour analyser les performances.

---

## 1. Métriques de performance audio / système

- **latency_sec** : Temps total nécessaire pour transcrire un fichier audio (en secondes).  
  → Plus la valeur est faible, plus le modèle est rapide.

- **memory_mb** : Mémoire utilisée pour traiter le fichier audio (en Mo).  
  → Une consommation excessive peut indiquer que le modèle est lourd ou inefficace.

- **duration_sec** : Durée de l’audio en secondes.  

- **latency_per_sec** : Latence divisée par la durée de l’audio.  
  → Permet de comparer les performances indépendamment de la longueur de l’audio.

- **latency_per_token** : Latence divisée par le nombre de mots (tokens).  
  → Utile pour mesurer la vitesse de traitement par mot.

- **memory_per_sec / memory_per_token** : Mémoire normalisée par seconde ou par mot.  
  → Plus précis pour comparer l’efficacité de différents modèles.

---

## 2. Métriques de transcription

- **transcript** : Texte produit par le modèle.

- **reference_text** : Texte de référence, utilisé pour comparer la transcription.  

- **tokens** : Nombre de mots (tokens) dans la transcription.

- **tokens_per_sec** : Nombre de mots transcrits par seconde.  
  → Indique le débit du modèle en termes de mots.

---

## 3. Métriques de qualité de transcription

- **wer** (Word Error Rate) : Pourcentage de mots erronés (insertions, suppressions, substitutions).  
  → Plus bas est meilleur (0% = transcription parfaite).

- **wer_token** : WER calculé par token (mot).  

- **levenshtein** : Distance de Levenshtein (nombre minimal d’opérations pour transformer la référence en transcription).  
  → Plus faible est meilleur.

- **levenshtein_pct** : Distance de Levenshtein normalisée par la longueur du texte.  
  → Permet comparaison entre phrases de longueur différente.

- **accuracy** : Proportion de mots correctement transcrits.  
  → Plus élevé = meilleure précision.

- **bleu3** : Score BLEU basé sur des trigrammes (3-gram).  
  → Évalue la similarité entre la transcription et la référence. Plus proche de 1 = meilleur.

- **meteor** : Score METEOR (compare exactitude, synonymes, ordre des mots).  
  → Plus proche de 1 = meilleure correspondance.

- **chrf** : Score ChrF (n-grammes de caractères).  
  → Mesure la similarité au niveau des caractères. Utile pour les langues à mots composés ou flexion.

- **rougeL** : Score ROUGE-L basé sur la plus longue sous-séquence commune.  
  → Indique la similarité globale de la structure de la phrase.

---

## 4. Comment utiliser ces métriques

1. **Comparer la vitesse et la consommation**  
   - Utiliser `latency_sec`, `latency_per_token`, `memory_mb`, `memory_per_token`.

2. **Comparer la qualité de transcription**  
   - Utiliser WER, Levenshtein, Accuracy pour une mesure de base.  
   - Compléter avec BLEU3, METEOR, CHRF, ROUGE-L pour une évaluation plus fine.

3. **Évaluer les modèles pour différents types de fichiers**  
   - Regarder `tokens_per_sec` pour vérifier que la vitesse est constante même sur des fichiers longs.  
   - Vérifier `levenshtein_pct` pour les fichiers courts, où WER peut être moins significatif.

4. **Corréler vitesse et précision**  
   - Un modèle rapide mais avec un WER élevé peut être inadapté pour des usages critiques.  
   - Un modèle précis mais très lent peut être acceptable pour un usage batch ou hors ligne.

---

**Remarque :**  
Toutes les métriques sont calculées par fichier audio. Les statistiques descriptives (moyenne, médiane, écart-type, quartiles, skew, kurtosis) sont disponibles pour chaque modèle pour une analyse globale.
