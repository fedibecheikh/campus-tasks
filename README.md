## Demarrage

Projet utilise dans les ateliers DevOps.

## Chaine CI/CD

Le workflow `.github/workflows/ci.yml` s'execute a chaque merge request, a
chaque push sur `main` et sur chaque tag `v*` :

| Job | Role | Condition |
| --- | --- | --- |
| `test` | `pytest` sur Python 3.11 et 3.12, rapport `report.xml` conserve en artefact | toujours |
| `docker-build` | construit l'image `campus-tasks:ci` et verifie que `/health` repond | apres `test` vert |
| `publish` | publie `ghcr.io/fedibecheikh/campus-tasks:<tag>` | tag `v*` uniquement |

Tests en local :

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
```

Publier une version immuable :

```bash
git tag -a v1.0.1 -m "Release 1.0.1"
git push origin v1.0.1
```

Mettre en service en staging et controler la sante :

```bash
printf 'IMAGE_TAG=v1.0.1\n' > .env.deploy
docker compose --env-file .env.deploy -f compose.staging.yaml pull
docker compose --env-file .env.deploy -f compose.staging.yaml up -d
./scripts/wait-healthy.sh
```

Retour arriere : remettre le precedent `IMAGE_TAG` dans `.env.deploy`, relancer
`up -d` puis `wait-healthy.sh`. On ne reconstruit jamais pendant un incident.

Documents associes : [quiz](docs/quiz-atelier-05.md),
[compte rendu d'incident](docs/incident-2026-11-16.md),
[preuves](docs/preuves-atelier-05.md).

## Support

Contact equipe A : equipe-a@example.invalid
Contact equipe B : equipe-b@example.invalid
