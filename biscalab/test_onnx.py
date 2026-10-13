"""Test du modèle de marche (ONNX) sans aucun matériel.

Usage, sur le Pi :
    python biscalab/test_onnx.py <chemin>/BEST_WALK_ONNX_2.onnx

Le script lit la taille d'entrée attendue par le modèle, fait 1000 calculs
avec des valeurs aléatoires et affiche le temps moyen par calcul.
La boucle de marche tourne à 50 Hz : un calcul doit prendre bien moins de 20 ms.
"""
import sys
import time

import numpy as np
import onnxruntime

if len(sys.argv) != 2:
    print(__doc__)
    sys.exit(1)

chemin = sys.argv[1]
session = onnxruntime.InferenceSession(chemin, providers=["CPUExecutionProvider"])
entree = session.get_inputs()[0]
sortie = session.get_outputs()[0]
taille = entree.shape[1]
print(f"Modèle : {chemin}")
print(f"Entrée '{entree.name}' : {taille} valeurs  |  Sortie '{sortie.name}' : {sortie.shape[1]} valeurs")

obs = np.random.uniform(-1, 1, size=(1, taille)).astype(np.float32)

# Quelques tours de chauffe, non comptés
for _ in range(20):
    session.run(None, {entree.name: obs})

n = 1000
debut = time.perf_counter()
for _ in range(n):
    actions = session.run(None, {entree.name: obs})[0]
duree_ms = (time.perf_counter() - debut) / n * 1000

print(f"Exemple de sortie : {np.round(actions[0], 3)}")
print(f"Temps moyen par calcul : {duree_ms:.3f} ms  (budget à 50 Hz : 20 ms)")
print("OK : largement dans le budget" if duree_ms < 5 else "ATTENTION : proche de la limite")
