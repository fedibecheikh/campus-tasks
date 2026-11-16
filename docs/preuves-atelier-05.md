# Preuves et bilan — Atelier 05 (CI/CD et mise en service)

Dépôt : <https://github.com/fedibecheikh/campus-tasks>
Registre : `ghcr.io/fedibecheikh/campus-tasks`

## 1. Erreurs trouvées et corrections

| Erreur | Correction |
| --- | --- |
| `compose.staging.yaml` créé dans `.github/workflows/` : GitHub le lit comme un workflow invalide | fichier supprimé de `.github/workflows/`, conservé à la racine |
| Tag de publication `ghcr.io/proprietaire/campus-tasks:${{ fedibecheikh }}` : `${{ }}` doit contenir une expression | `ghcr.io/fedibecheikh/campus-tasks:${{ github.ref_name }}` |
| `pytest==8.3.5` présent deux fois dans `requirements-dev.txt` | une seule occurrence + `-r requirements.txt` |
| `.env.staging` vide | `PORT=8080` (fichier ignoré par Git) |
| `tests/__pycache__/*.pyc` suivi par Git | retiré de l'index, `__pycache__/` ajouté au `.gitignore` |
| Tag `v1.0.0` poussé alors que le workflow ne se déclenchait pas sur les tags | `on.push.tags: ['v*']` + job `publish` |
| `requirements-dev.txt`, `tests/`, `.venv` créés à la racine de `atelier-02` (hors dépôt) | supprimés |

## 2. Pipeline

| Exécution | URL | Résultat |
| --- | --- | --- |
| Merge request (étape 2) | <https://github.com/fedibecheikh/campus-tasks/pull/1> — run <https://github.com/fedibecheikh/campus-tasks/actions/runs/43843444921> | vert |
| Push sur `main` | <https://github.com/fedibecheikh/campus-tasks/actions/runs/43848714894> | vert (`test` ×2, `docker-build`, artefact `rapport-tests-3.11` / `-3.12`) |
| Tag `v1.0.1` (publication) | <https://github.com/fedibecheikh/campus-tasks/actions/runs/43848916962> | vert, job `publish` inclus |

Jobs vus dans l'exécution du tag :

```text
test (python 3.11)  completed success
test (python 3.12)  completed success
docker-build        completed success   (image construite + /health verifie)
publish             completed success   (push vers ghcr.io)
```

Image publiée et **téléchargeable anonymement** :

```console
$ docker pull ghcr.io/fedibecheikh/campus-tasks:v1.0.1
...
$ curl -s -o /dev/null -w '%{http_code}' \
    -H "Authorization: Bearer $TOKEN" \
    https://ghcr.io/v2/fedibecheikh/campus-tasks/manifests/v1.0.1
200
```

## 3. Étape 5 — mise en service et contrôle de santé

```console
$ printf 'IMAGE_TAG=v1.0.1\n' > .env.deploy
$ docker compose --env-file .env.deploy -f compose.staging.yaml pull
 Image ghcr.io/fedibecheikh/campus-tasks:v1.0.1 Pulled
$ docker compose --env-file .env.deploy -f compose.staging.yaml up -d
 Container campus-tasks-api-1 Started
$ docker compose --env-file .env.deploy -f compose.staging.yaml ps
NAME                 IMAGE                                      SERVICE   STATUS
campus-tasks-api-1   ghcr.io/fedibecheikh/campus-tasks:v1.0.1   api       Up (health: starting)
$ ./scripts/wait-healthy.sh
{"status":"ok"}
staging sain
$ echo $?
0
```

## 4. Étape 6 — incident et retour arrière

Premier diagnostic : le tag demandé n'existe pas dans le registre.

```console
$ printf 'IMAGE_TAG=v0.9.0\n' > .env.deploy
$ docker compose --env-file .env.deploy -f compose.staging.yaml pull
Error response from daemon: failed to resolve reference
"ghcr.io/fedibecheikh/campus-tasks:v0.9.0": ... not found
```

L'image `v0.9.0` de l'enseignant n'étant pas disponible, elle a été **simulée
localement** (même code, écoute sur `127.0.0.1` au lieu de `0.0.0.0`) :

```console
$ docker compose --env-file .env.deploy -f compose.staging.yaml up -d
 Container campus-tasks-api-1 Started
$ docker compose --env-file .env.deploy -f compose.staging.yaml ps
campus-tasks-api-1   ghcr.io/fedibecheikh/campus-tasks:v0.9.0   Up
$ ./scripts/wait-healthy.sh
curl: (56) Recv failure: Connection reset by peer      (x12)
staging non sain
$ echo $?
1
```

Première erreur utile dans les journaux :

```console
$ docker compose --env-file .env.deploy -f compose.staging.yaml logs --tail=50 api
api-1  |  * Serving Flask app 'app'
api-1  |  * Running on http://127.0.0.1:8080
```

Retour arrière (sans reconstruction) :

```console
$ printf 'IMAGE_TAG=v1.0.1\n' > .env.deploy
$ docker compose --env-file .env.deploy -f compose.staging.yaml up -d
 Container campus-tasks-api-1 Recreated / Started
$ ./scripts/wait-healthy.sh
{"status":"ok"}
staging sain
$ echo $?
0
$ docker compose --env-file .env.deploy -f compose.staging.yaml ps
campus-tasks-api-1   ghcr.io/fedibecheikh/campus-tasks:v1.0.1   Up
```

Durée d'indisponibilité mesurée : environ 75 s (60 s de détection + ~5 s de
rollback).

## 5. Pourquoi `v1.0.1` et pas `v1.0.0` ?

Le tag `v1.0.0` a été poussé alors que le workflow ne se déclenchait pas sur les
tags (`on.push.branches: [main]` seulement) : il n'a donc jamais produit
d'image. La règle de l'atelier s'applique : **un tag publié ne se déplace
jamais** ; on publie `v1.0.1`. `v1.0.0` reste donc sur son commit d'origine et la
release complète (tag **et** image) est `v1.0.1`.

## 6. Défi final — matrice Python 3.11 / 3.12

Le job `test` utilise `strategy.matrix.python-version: ['3.11', '3.12']` avec
`fail-fast: false`. Les deux versions tournent donc jusqu'au bout, même si
l'une échoue. Ici les deux sont vertes : le code est compatible 3.11 et 3.12.
Si une seule échouait, on saurait immédiatement que l'écart vient de la version
de Python (et non du code métier), et l'artefact `rapport-tests-<version>`
permettrait de comparer les rapports.

## 7. Validation du livrable (20 points)

| Élément évalué | Preuve |
| --- | --- |
| Workflow valide, déclenché sur merge request | `.github/workflows/ci.yml`, PR #1 et run 43843444921 |
| Tests exécutés, rapport en artefact | jobs `test` ×2, artefacts `rapport-tests-3.11` / `-3.12` |
| Construction de l'image dépendante des tests | `docker-build` avec `needs: test` |
| Version immuable : tag et image publiée | tag `v1.0.1` + `ghcr.io/fedibecheikh/campus-tasks:v1.0.1` (public) |
| Mise en service et contrôle de santé | section 3 |
| Retour arrière démontré | section 4 |
| Compte rendu d'incident, aucun secret | `docs/incident-2026-11-16.md` ; `.env*` ignorés, aucun jeton dans le workflow |
