# Quiz de sortie — Atelier 05

## 1. Quelle est la différence entre un job et une étape ?

Un **job** est un ensemble d'étapes exécuté sur une machine neuve (le runner).
Deux jobs sont indépendants par défaut et peuvent tourner en parallèle ; ils ne
partagent ni fichiers ni environnement. Une **étape** (`step`) est une commande
ou une action exécutée dans l'ordre à l'intérieur d'un job, sur la même machine :
si une étape échoue, le job s'arrête. Un job peut donc contenir plusieurs étapes,
mais une étape n'appartient qu'à un seul job.

## 2. Pourquoi exécuter les tests avant de construire l'image ?

Pour ne pas construire ni publier une image contenant du code cassé : le retour
d'information est plus rapide et moins coûteux, on économise les minutes de
construction, et surtout on évite de rendre disponible une version défectueuse.
C'est le rôle de la dépendance `needs: test` : si les tests échouent,
`docker-build` et `publish` ne démarrent pas.

## 3. À quoi sert la clé `needs` ?

Elle déclare une **dépendance entre jobs** : le job ne démarre que si le job
cité est terminé avec succès. Elle sert à ordonner les jobs (test → build →
publish) et à empêcher la construction d'une image quand les tests sont rouges.

## 4. Quelle est la différence entre livraison continue et déploiement continu ?

La **livraison continue** automatise la vérification et la production d'une
version prête à être mise en service, mais **un humain décide** du moment du
déploiement. Le **déploiement continu** va plus loin : la mise en service est
elle aussi automatique, sans décision humaine. Dans cet atelier, le pipeline
produit l'image et le tag (livraison continue), puis la mise en service en
staging est déclenchée volontairement.

## 5. Pourquoi une image de version ne doit-elle jamais être reconstruite ?

Parce qu'une reconstruction n'est pas reproductible : une image de base mise à
jour, une dépendance qui change de version ou un cache différent produisent un
contenu différent sous le même numéro. Le tag doit désigner un contenu **fixe et
déjà validé**, sinon on ne peut plus savoir ce qui tourne, ni revenir en arrière
en toute confiance. Si la version est mauvaise, on publie `v1.0.1` ; on ne
réécrit pas `v1.0.0`. Pendant un incident, on réutilise l'image existante : on
ne reconstruit jamais.

## 6. Pourquoi un contrôle de santé est-il nécessaire après une mise en service réussie ?

Parce qu'une commande de mise en service qui réussit prouve seulement que le
conteneur a démarré, pas que l'application répond. Un conteneur peut être `Up`
et le service inutilisable (mauvaise adresse d'écoute, variable manquante,
dépendance absente). Seul un appel réel à `/health` établit que le service est
disponible, et c'est ce contrôle qui doit décider d'un retour arrière — comme
démontré à l'étape 6.
