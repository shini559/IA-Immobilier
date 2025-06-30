# tests/test_predict_lille.py

from fastapi.testclient import TestClient
from app.main import app
import pytest

@pytest.fixture(scope="module")
def test_app():
    """
    Crée une instance de TestClient qui exécute les événements de startup/shutdown de l'application.
    Utilise le context manager de TestClient pour gérer le lifecycle.
    """
    with TestClient(app) as client:
        yield client



# Test 1: Prédiction réussie pour un appartement à Lille
def test_predict_lille_apartment_success(test_app):
    """
    Vérifie qu'une requête valide pour un appartement à Lille retourne un statut 200 OK
    et une structure de réponse correcte avec un prix estimé.
    """
    response = test_app.post(
        "/predict/lille",
        json={
            "surface_bati": 80,
            "nombre_pieces": 4,
            "type_local": "Appartement",
            "surface_terrain": 0,
            "nombre_lots": 1
        }
    )
    assert response.status_code == 200
    assert "prix_m2_estime" in response.json()
    assert "ville_modele" in response.json()
    assert "model_name" in response.json()
    assert response.json()["ville_modele"] == "Lille"
    assert isinstance(response.json()["prix_m2_estime"], (float, int))
    assert response.json()["prix_m2_estime"] > 0

# Test 2: Prédiction réussie pour une maison à Lille
def test_predict_lille_maison_success(test_app):
    """
    Vérifie qu'une requête valide pour une maison à Lille retourne un statut 200 OK
    et une structure de réponse correcte avec un prix estimé.
    """
    response = test_app.post(
        "/predict/lille",
        json={
            "surface_bati": 100,
            "nombre_pieces": 4,
            "type_local": "Maison",
            "surface_terrain": 300

        }
    )
    assert response.status_code == 200
    assert "prix_m2_estime" in response.json()
    assert response.json()["ville_modele"] == "Lille"
    assert isinstance(response.json()["prix_m2_estime"], (float, int))
    assert response.json()["prix_m2_estime"] > 0

# Test 3: Gestion d'erreur pour un type_local invalide
def test_predict_lille_invalid_type_local(test_app): # Utilise la fixture
    """
    Vérifie qu'une requête avec un 'type_local' invalide retourne un statut 400 Bad Request.
    """
    response = test_app.post( # Utilise test_app.post
        "/predict/lille",
        json={
            "surface_bati": 80,
            "nombre_pieces": 4,
            "type_local": "Bureau", # Type invalide
            "surface_terrain": 0,
            "nombre_lots": 1
        }
    )
    assert response.status_code == 400
    assert "detail" in response.json()
    assert response.json()["detail"] == "Le 'type_local' doit être 'Appartement' ou 'Maison'."

# Test 4: Gestion d'erreur pour nombre_pieces différent de 4
def test_predict_lille_invalid_nombre_pieces(test_app): # Utilise la fixture
    """
    Vérifie qu'une requête avec un 'nombre_pieces' différent de 4 retourne un statut 400 Bad Request.
    """
    response = test_app.post( # Utilise test_app.post
        "/predict/lille",
        json={
            "surface_bati": 80,
            "nombre_pieces": 3, # Nombre de pièces invalide
            "type_local": "Appartement",
            "surface_terrain": 0,
            "nombre_lots": 1
        }
    )
    assert response.status_code == 400
    assert "detail" in response.json()
    assert response.json()["detail"] == "Seuls les logements de 4 pièces sont pris en charge par ce modèle."

# Test 5: Gestion d'erreur pour une surface_bati invalide (<= 0)
def test_predict_lille_invalid_surface_bati(test_app): # Utilise la fixture
    """
    Vérifie qu'une requête avec une 'surface_bati' invalide (<= 0) retourne un statut 422 Unprocessable Entity
    (validation Pydantic).
    """
    response = test_app.post( # Utilise test_app.post
        "/predict/lille",
        json={
            "surface_bati": 0, # Invalide selon le schéma Pydantic (gt=0)
            "nombre_pieces": 4,
            "type_local": "Appartement",
            "surface_terrain": 0,
            "nombre_lots": 1
        }
    )
    assert response.status_code == 422
    assert "detail" in response.json()
    assert "greater than 0" in response.json()["detail"][0]["msg"]

# Test 6: Gestion d'erreur pour un champ optionnel fourni comme None (qui viole la validation Pydantic ou la logique)
def test_predict_lille_none_invalid_optional_feature_apartment(test_app): # Utilise la fixture
    """
    Vérifie qu'une requête avec 'nombre_lots: None' retourne un statut 400 Bad Request,
    car il est traité comme une donnée manquante requise par preprocess_input_data
    (même si Pydantic pourrait aussi lever une 422).
    """
    response = test_app.post( # Utilise test_app.post
        "/predict/lille",
        json={
            "surface_bati": 80,
            "nombre_pieces": 4,
            "type_local": "Appartement",
            "surface_terrain": 0,
            "nombre_lots": None # Envoyé comme None
        }
    )
    # --- CORRECTION DE L'ASSERTION ICI ---
    assert response.status_code == 400 # On attend 400, car c'est preprocess_input_data qui lève l'erreur pour None
    assert "detail" in response.json()
    assert response.json()["detail"] == "La caractéristique 'nombre_lots' (correspondant à 'Nombre de lots') est requise et manquante."
    # --- FIN CORRECTION ---


# Test 7: Gestion d'erreur pour une maison avec surface_terrain invalide (None si Pydantic l'autorisait)
def test_predict_lille_maison_invalid_surface_terrain_value(test_app): # Utilise la fixture
    """
    Vérifie qu'une requête pour une maison avec une 'surface_terrain' négative
    retourne un statut 422 Unprocessable Entity (validation Pydantic).
    """
    response = test_app.post( # Utilise test_app.post
        "/predict/lille",
        json={
            "surface_bati": 100,
            "nombre_pieces": 4,
            "type_local": "Maison",
            "surface_terrain": -10, # Valeur invalide selon le schéma Pydantic (ge=0)
            "nombre_lots": 0
        }
    )
    assert response.status_code == 422
    assert "detail" in response.json()
    assert "greater than or equal to 0" in response.json()["detail"][0]["msg"]

