# app/main.py

from fastapi import FastAPI, HTTPException, status
from typing import Dict, Any
import os

# Importer la fonction de chargement de modèles/scalers du nouveau module
from app.model_loader import load_model_and_scaler

# Importer les schémas définis pour les requêtes et les réponses
from app.schemas import PropertyFeatures, PredictionResponse, DynamicPredictionRequest

# Importer le routeur des routes de prédiction
from app.routes import router as prediction_router

current_app_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_app_dir, '..'))
models_folder = os.path.join(project_root, 'models')

# Initialisation de l'application FastAPI
app = FastAPI(
    title="ImmoPrice API - Prédiction du prix au m²",
    description="API pour estimer le prix au m² de biens immobiliers à Lille et Bordeaux (logements de 4 pièces).",
    version="1.0.0",
    docs_url="/docs",  # URL pour la documentation Swagger UI
    redoc_url="/redoc"  # URL pour la documentation ReDoc
)


# NOTE: La variable loaded_resources n'est plus déclarée ici comme une variable globale du module.
# Elle sera maintenant stockée directement dans app.state.loaded_resources au démarrage.

# Événement de démarrage de l'application FastAPI.
# Cette fonction est exécutée de manière asynchrone une seule fois lorsque le serveur Uvicorn démarre.
@app.on_event("startup")
async def load_resources_on_startup():
    print("Chargement des modèles et scalers au démarrage de l'API...")
    try:
        # Initialiser app.state.loaded_resources comme un dictionnaire vide au démarrage
        # C'est ici que les modèles et scalers seront stockés pour être accessibles via l'état de l'application.
        app.state.loaded_resources = {}

        # Charger le modèle et le scaler pour les appartements de Lille
        # Le chemin complet est construit en combinant models_folder et le nom du fichier.
        app.state.loaded_resources['lille_appartements_model'], app.state.loaded_resources[
            'lille_appartements_scaler'] = \
            load_model_and_scaler(
                os.path.join(models_folder, 'optimized_dt_appartements_lille.joblib'),
                os.path.join(models_folder, 'scaler_appartements_lille.joblib')
            )
        print("- Modèle et scaler pour les appartements de Lille chargés.")

        # Charger le modèle et le scaler pour les maisons de Lille
        app.state.loaded_resources['lille_maisons_model'], app.state.loaded_resources['lille_maisons_scaler'] = \
            load_model_and_scaler(
                os.path.join(models_folder, 'optimized_dt_maisons_lille.joblib'),
                os.path.join(models_folder, 'scaler_maisons_lille.joblib')
            )
        print("- Modèle et scaler pour les maisons de Lille chargés.")

        # Pour Bordeaux, nous utilisons actuellement les modèles et scalers de Lille comme placeholders.
        # Dans un scénario réel de déploiement multi-villes,
        # vous entraîneriez et enregistreriez des modèles distincts et optimisés pour Bordeaux.
        app.state.loaded_resources['bordeaux_appartements_model'], app.state.loaded_resources[
            'bordeaux_appartements_scaler'] = \
            load_model_and_scaler(
                os.path.join(models_folder, 'optimized_dt_appartements_lille.joblib'),  # Placeholder
                os.path.join(models_folder, 'scaler_appartements_lille.joblib')  # Placeholder
            )
        print("- Modèle et scaler pour les appartements de Bordeaux (actuellement ceux de Lille) chargés.")

        app.state.loaded_resources['bordeaux_maisons_model'], app.state.loaded_resources['bordeaux_maisons_scaler'] = \
            load_model_and_scaler(
                os.path.join(models_folder, 'optimized_dt_maisons_lille.joblib'),  # Placeholder
                os.path.join(models_folder, 'scaler_maisons_lille.joblib')  # Placeholder
            )
        print("- Modèle et scaler pour les maisons de Bordeaux (actuellement ceux de Lille) chargés.")

        print("Tous les modèles et scalers ont été chargés avec succès dans la mémoire de l'API.")

    except FileNotFoundError as e:
        print(f"Erreur fatale : Un fichier modèle ou scaler n'a pas été trouvé. Détails : {e}")
        print(
            "Veuillez vous assurer que tous les fichiers .joblib sont présents dans le dossier 'immoprice-api/models/'.")
        # En production, vous pourriez vouloir lever une exception ou arrêter l'application ici.
        # Pour le développement, on initialise une ressource vide pour éviter les erreurs subséquentes.
        app.state.loaded_resources = {}
    except Exception as e:
        print(f"Erreur fatale lors du chargement des ressources : {e}. L'API ne pourra pas fonctionner correctement.")
        app.state.loaded_resources = {}

    # Route racine de l'API pour un message de bienvenue.


@app.get("/", summary="Route de bienvenue", response_description="Message de bienvenue et lien vers la documentation.")
async def read_root():
    return {"message": "Bienvenue sur l'API ImmoPrice ! Pour explorer les endpoints, visitez /docs."}


# Inclure toutes les routes de prédiction définies dans app/routes/routes.py.
# Cela permet d'organiser les endpoints dans des fichiers séparés et de les ajouter à l'application principale.
app.include_router(prediction_router)
