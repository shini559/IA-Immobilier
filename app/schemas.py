# app/schemas.py

from pydantic import BaseModel, Field
from typing import Optional


class PropertyFeatures(BaseModel):
    surface_bati: int = Field(..., gt=0, description="Surface réelle bâtie en m² (doit être > 0)")

    nombre_pieces: int = Field(4, gt=0, description="Nombre de pièces principales (doit être > 0)")

    type_local: str = Field(..., description="Type de local ('Appartement' ou 'Maison')")


    surface_terrain: Optional[int] = Field(None, ge=0, description="Surface du terrain en m² (optionnel, >= 0)")


    nombre_lots: Optional[int] = Field(None, ge=1, description="Nombre de lots (optionnel, >= 1)")



class DynamicPredictionRequest(BaseModel):

    ville: str = Field(..., description="Ville pour la prédiction ('Lille' ou 'Bordeaux')")

    features: PropertyFeatures

class PredictionResponse(BaseModel):
    prix_m2_estime: float = Field(..., description="Prix au m² estimé en Euros")

    ville_modele: str = Field(..., description="Ville utilisée par le modèle de prédiction")

    model_name: str = Field(..., description="Nom du modèle utilisé")