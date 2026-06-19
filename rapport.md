# TP DevOps <!--par Aymeric Chassagne-->
### Par Aymeric Chassagne
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Jenkins](https://img.shields.io/badge/Jenkins-D24939?style=for-the-badge&logo=jenkins&logoColor=white)](https://www.jenkins.io/)
# 📚 Sommaire
| TP | Sujet | Statut |
|----|--------|---------|
| [TP1 : Git et Docker](#tp1--git-et-docker) | Versioning, Conteneurisation et Docker Compose | ✅ Done |
| [TP2 : Jenkins Pipeline](#tp2--jenkins-pipeline) | Installer Jenkins et créer un pipeline Groovy complet | ⏳ In Progress |
| [TP3 : SonarQube, TrivyQualité & Sécurité](#tp3) | À définir | ⏳ To Do |
| [TP4 : Terraform IaC, Docker provider](#tp4) | À définir | ⏳ To Do |
| [TP5 : Monitoring, Prometheus, Grafana](#tp5) | À définir | ⏳ To Do |
___

# TP1 : Git et Docker

## Contexte
Vous intégrez **StartupIA**, une entreprise qui développe une **plateforme SaaS** d'analyse de sentiments pour les avis clients (e-commerce, réseaux sociaux, CRM). Votre mission est de mettre en place l'infrastructure **DevOps** de **l'API SentimentAI** depuis le dépôt Git jusqu'à **l'image Docker**, en préparation du **pipeline CI/CD automatisé** construit dans les TPs suivants. **SentimentAI** est une **API REST** développée en **FastAPI/Python**. Elle reçoit un **texte en entrée**, l'analyse et **retourne un label** (POSITIF, NÉGATIF ou NEUTRE) accompagné d'un **score de confiance** entre 0 et 1.
___

### 📂 Structure du projet
```text
sentiment-ai/
├── .dockerignore
├── .github/
│   └── workflows/
├── .gitignore
├── Dockerfile
├── Makefile
├── docker-compose.yml
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── model.py
│   └── schemas.py
└── tests/
    ├── __init__.py
    └── test_api.py
```

### src/schemas.py - Modèles de données Pydantic
```python
from pydantic import BaseModel, Field
from typing import Literal

class PredictionRequest(BaseModel):
	text: str=Field(... , min_length=1 , max_length=5000)

class PredictionResponse(BaseModel):
	label: Literal["POSITIVE", "NEGATIVE", "NEUTRAL"]
	score: float
	text: str
```

### src/model.py - Modèle de sentiment simplifié
```python
class SentimentModel:
	def __init__(self):
		print ("[SentimentModel] Modèle chargé")

	def predict(self, text: str) -> dict:
		text_lower = text.lower()
		positive_words = ["bien", "super", "excellent", "parfait", "bon", "aime", "adore"]
		negative_words = ["mal", "nul", "horrible", "mauvais", "déteste", "pire"]
		pos = sum(1 for w in positive_words if w in text_lower)
		neg = sum(1 for w in negative_words if w in text_lower)
		if pos > neg:
			return {"label": "POSITIVE", "score": round(0.6 + 0.1*pos, 2), "text": text}
		elif neg > pos:
			return {"label": "NEGATIVE", "score": round(0.6 + 0.1*neg, 2), "text": text}
		return {"label": "NEUTRAL", "score": 0.5, "text": text}
```

### src/main.py - Application FastAPI
```python
from fastapi import FastAPI
from src.schemas import PredictionRequest, PredictionResponse
from src.model import SentimentModel

app = FastAPI(title="SentimentAI", version=" 0.1.0 ")

model = SentimentModel()

@app.get ("/health")
def health () :
	"""Endpoint de healthcheck utilisé par Docker et les load balancers."""
	return {"status": "ok"}

@app.post ("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
	"""Analyse le sentiment du texte fourni et retourne un label + score."""
	return model.predict(request.text)

```

### tests/test_api.py - Tests unitaires et d’intégration
```python
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health():
    """Vérifie que l'endpoint /health répond avec status 200."""
    r = client.get("/health")
    assert r.status_code == 200

def test_predict_positive():
    """Vérifie qu'une pré diction retourne la bonne structure de réponse."""
    r = client.post("/predict", json ={"text": "Ce produit est excellent !"})
    assert r.status_code == 200
    data = r.json()
    assert data["label"] in ["POSITIVE", "NEGATIVE", "NEUTRAL"]
    assert 0 <= data["score"] <= 1

def test_predict_empty_fails():
    """Vérifie que Pydantic rejette un texte vide avec une erreur 422."""
    r = client.post("/predict", json ={"text": ""})
    assert r.status_code == 422
```

### requirements.txt - Dépendances Python
```m
fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.5.3
pytest==7.4.4
pytest-cov==4.1.0
httpx==0.26.0
```
___

**Faites un screenshot de ```git log –oneline``` montrant votre premier commit.**<br>
![alt text](image.png)

**Expliquez en deux phrases le rôle du fichier ```.gitignore``` !**<br>
Le fichier .gitignore indique à Git quels fichiers ou dossiers doivent être ignorés et ne pas être suivis dans le dépôt.

**Pourquoi il est important de ne pas committer le dossier ```__pycache__/``` dans Git.**<br>
Il est important de ne pas committer le dossier __pycache__/ car il contient des fichiers Python compilés générés automatiquement, spécifiques à l'environnement d'exécution et inutiles au code source, ce qui encombre inutilement le dépôt.

**Question 1.2 : Quelle est la différence entre ```git add .``` et ```git add -p``` ?**<br>
```git add .``` ajoute toutes les modifications alors que ```git add -p``` permet de choisir précisément quelles modifications ajouter.

**Dans quel cas préférez-vous utiliser ```git add -p``` plutôt que ```git add .``` ?**<br>
Il est préférable d’utiliser ```git add -p``` lorsqu’on a plusieurs gros changements dans un même fichier.

**Faites un screenshot de docker build réussi (dernière ligne) et de la réponse JSON retournée par curl /predict. Identifiez dans la sortie du build les couches qui ont été mises en cache (CACHED) et celles qui ont été recalculées.**<br>
![alt text](image-1.png)

**Relancez docker build une deuxième fois sans rien modifier au projet. Que remarquez-vous dans la sortie ?**<br>
Gnagnagna

**Quelle instruction du Dockerfile ne bénéficie pas du cache si vous modifiez un seul fichier Python dans src/ ? Expliquez pourquoi en vous appuyant sur le principe des layers Docker.**<br>
Gnagnagna

**Question 3.1 :**
![alt text](image-2.png)

**Question 4.1 :**
![alt text](image-3.png)

**Question 4.2 :**
![alt text](image-4.png)

**git tag** est simplement un pointeur vers un commit, il ne contient pas de métadonnées supplémentaires. Pas d’auteur, pas de date, pas de message. Comparable à un signet rapide.

**git tag -a** est un objet git stocké dans la BDD git. Il contient le nom, l’auteur, la date et un message descriptif.

Pourquoi on préfère les tags annotés ? Car ils sont mieux traçables, plus sécurisé / sécurisant (historique plus fiable aussi), et pour la documentation.

## TP2 : Jenkins Pipeline
### Contexte du TP2
SentimentAI est désormais versionnée dans Git et conteneurisée avec Docker (TP1). L’étape suivante consiste à automatiser le cycle build/test/push : à chaque git push, Jenkins récupère le code, le lint, construit l’image Docker, lance les tests et pousse l’image vers le registry si on est sur la branche main. Jenkins est installé lui-même dans un conteneur Docker. Cette approche appelée Docker-out-of-Docker (DooD) - lui permet d’exécuter des commandes docker build en montant le socket Docker de l’hôte.

### 1.1 Lancer Jenkins
1. `docker volume create jenkins-data`<br>
2. `docker run -d --name jenkins -p 8080:8080 -p 50000:50000 -v jenkins-data:/var/jenkins_home -v /var/run/docker.sock:/var/run/docker.sock jenkins/jenkins:lts`<br>
3. `docker logs -f jenkins`<br>
4. `docker exec -u jenkins jenkins docker ps`
5. `docker exec -u root jenkins bash -c "apt-get update -q && apt-get install -y docker.io"`

### 1.2 Première configuration Jenkins
1. Ouvrez http://localhost:8080 dans votre navigateur.
2. Récupérez le mot de passe initial : `docker exec jenkins cat/var/jenkins_home/secrets/initialAdminPassword`
3. Choisissez "Install suggested plugins" et attendre la fin de l’installation.
4. Créez votre compte administrateur (notez login/mot de passe).
5. Cliquez "Save and Finish" → "Start using Jenkins".

![alt text](image-5.png)

**Quel est le rôle du volume jenkins-data monté sur /var/jenkins_home ?**<br>
Le rôle du volume jenkins-data monté sur /var/jenkins_home est de persister toutes les données Jenkins en dehors du conteneur afin qu'elles survivent aux redémarrages, mises à jour ou recréations du conteneur.


## TP3

Contenu du TP3...

## TP4 : Terraform IaC, Docker provider

Contenu du TP4...

## TP5

Contenu du TP5...
