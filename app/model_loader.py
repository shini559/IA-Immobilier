

import joblib
import os
from typing import Any, Tuple



def load_model_and_scaler(model_path: str, scaler_path: str) -> Tuple[Any, Any]:
    """
    Charge un modèle et son scaler associé depuis les chemins spécifiés.
    Args:
        model_path (str): Chemin complet vers le fichier du modèle (.joblib).
        scaler_path (str): Chemin complet vers le fichier du scaler (.joblib).
    Returns:
        tuple: (model, scaler)
    Raises:
        FileNotFoundError: Si un fichier n'est pas trouvé.
        Exception: Pour toute autre erreur de chargement.
    """
    try:
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        return model, scaler
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Fichier manquant. Assurez-vous que '{model_path}' et '{scaler_path}' existent. Erreur: {e}"
        )
    except Exception as e:
        raise Exception(f"Erreur lors du chargement des ressources: {e}")