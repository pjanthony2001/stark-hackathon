# Stark – Hackathon 

**Un prototype minimal de zk‑STARK développé à partir de zéro.**

---

## Présentation

Stark – Hackathon est une implémentation expérimentale d’un système de preuve zk‑STARK développée pendant la semaine de hackathon — sans aucune expérience préalable dans les STARKs. Nous avons implémenté à la main les structures algébriques fondamentales telles que les corps finis, les polynômes et le protocole FRI.

À l'origine, notre objectif était de créer une preuve STARK permettant de vérifier un terme d'une **suite de Fibonacci**, un projet que nous a été fourni par notre encadrant, https://github.com/starkware-industries/stark101. Nous avons ensuite voulu généraliser le problème : prouver qu’une **state_machine** avait correctement effectué un calcul à partir d’une entrée initiale et d’une matrice de transformation. Cependant, en raison de la complexité du protocole et du temps limité, cette généralisation n’a pas pu être finalisée.

---

## État actuel

- Réalisé : Opérations algébriques de base et sur les polynômes  
- Réalisé : Protocole FRI implémenté et fonctionnel  
- Non complété : Preuve STARK pour la machine à états généralisée 
- Version avec preuve de Fibonacci déjà disponible dans https://github.com/starkware-industries/stark101.

---

##  Contenu

- **Algèbre :** `Fields`, `FieldElement`, `Polynomial`, etc.
- **Protocole FRI :** Implémentation complète du protocole de test de faible degré
- **StateMachine :** Émulation d'une machine qui encode différentes étapes de calcul avec une entrée x_0 et le passage d'un état à l'autre par le produit de x_i et d'une matrice A. **À compléter**.

---

## Stack technique

- **Langage :** Python 3.10+
- **Structure du projet :**
`/utils/` - dossier comprenant toutes les classes nécessaires à l'implémentation du protocole STARK
   - `boundary/` - encoder conditions aux limites de la preuve (valeur initiale, valeur finale)
   - `field/` – opérations sur les corps finis 
   - `fri/` – protocole FRI 
   - `matrix/` - opérations sur les matrices, nécessaire pour manipuler des matrices à coefficients dans un corps fini
   - `merkle_tree/` - passer d'une computational trace à un merkle tree
   - `mutlivpolynomial/` - opérations sur les polynômes à plusieurs variables  
   - `poly/` – opérations sur les polynômes et racines de l’unité    
   - `proof_stream/` - rendre le protocole non interactif en simulant un vérifieur
   - `reed_solomon` - implémentation de la transformation de la trace en Reed - Solomon codeword 
   - `state_machine/` – début d'implémentation de la state_machine mentionnée plus haut **À finir**
   - `transition` - encoder les conditions de transition (la relation de récurrence dans les calculs)

---

## Prochaines étapes

- Finaliser la classe StateMachine pour pouvoir réaliser un premier essai
- Coder un verifier 
