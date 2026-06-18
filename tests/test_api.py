from fastapi . testclient import TestClient
from src . main import app

client = TestClient ( app )

def test_health () :
    """Vérifie que l'endpoint / health ré pond avec status 200. """
    r = client . get ("/ health ")
    assert r . status_code == 200

def test_predict_positive () :
    """Vérifie qu'une pré diction retourne la bonne structure de ré ponse ."""
    r = client . post ("/ predict ", json ={" text ": "Ce produit est excellent !"})
    assert r . status_code == 200
    data = r . json ()
    assert data [" label "] in [" POSITIVE ", " NEGATIVE ", " NEUTRAL "]

assert 0 <= data [" score "] <= 1
def test_predict_empty_fails () :
    """Vérifie que Pydantic rejette un texte vide avec une erreur 422. """
    r = client . post ("/ predict ", json ={" text ": ""})
    assert r . status_code == 422