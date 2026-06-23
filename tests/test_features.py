import pandas as pd

from api.features import FeatureContext, build_feature_frame, dept_to_float, get_tranche
from api.schemas import PredictionRequest


def test_dept_to_float_handles_corsica_and_regular_codes():
    assert dept_to_float("75") == 75.0
    assert dept_to_float("2A") == 201.0
    assert dept_to_float("abc") == 0.0


def test_segment_and_feature_frame_use_commune_defaults():
    communes = pd.DataFrame(
        [
            {
                "code_commune": "75056",
                "commune_prix_m2": 9500,
                "commune_prix_m2_appart": 10000,
                "dept_prix_m2_appart": 9000,
                "latitude": 48.85,
                "longitude": 2.35,
            }
        ]
    )
    context = FeatureContext(
        features=[
            "surface_reelle_bati",
            "surface_par_piece",
            "commune_prix_m2",
            "commune_prix_m2_appart",
            "dept_prix_m2_appart",
            "latitude",
            "longitude",
        ],
        q33=1800,
        q66=3100,
        communes=communes,
    )
    request = PredictionRequest(surface_reelle_bati=50, nombre_pieces_principales=2, code_commune="75056")

    frame, segment, fallback_price = build_feature_frame(request, context)

    assert segment == "haut_appart"
    assert fallback_price == 10000
    assert frame.loc[0, "surface_reelle_bati"] == 50
    assert frame.loc[0, "surface_par_piece"] == 25
    assert frame.loc[0, "commune_prix_m2"] == 9500


def test_get_tranche_boundaries():
    assert get_tranche(1000, 1800, 3100) == "bas"
    assert get_tranche(2500, 1800, 3100) == "milieu"
    assert get_tranche(5000, 1800, 3100) == "haut"
