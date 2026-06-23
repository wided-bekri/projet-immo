from pydantic import BaseModel, Field, field_validator


class PredictionRequest(BaseModel):
    surface_reelle_bati: float = Field(..., gt=0, le=1000)
    nombre_pieces_principales: int = Field(3, ge=1, le=30)
    type_bien: str = Field("appart", examples=["appart", "maison"])
    code_commune: str | None = Field(None, min_length=1, max_length=5)
    code_departement: str | None = Field(None, min_length=1, max_length=3)
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    surface_terrain: float = Field(0, ge=0, le=100000)
    annee: int = Field(2025, ge=2020, le=2035)
    mois: int = Field(6, ge=1, le=12)
    target_dpe_num: int = Field(4, ge=1, le=7)
    cout_total_5_usages: float = Field(0, ge=0)
    age_construction: float = Field(30, ge=0, le=500)

    @field_validator("type_bien")
    @classmethod
    def validate_type_bien(cls, value: str) -> str:
        normalized = value.strip().lower()
        aliases = {"appartement": "appart", "appart": "appart", "maison": "maison"}
        if normalized not in aliases:
            raise ValueError("type_bien doit etre 'appart', 'appartement' ou 'maison'")
        return aliases[normalized]


class PredictionResponse(BaseModel):
    prediction_eur_m2: float
    prediction_total_eur: float
    interval_low_eur: float
    interval_high_eur: float
    model_segment: str
    model_source: str
    features_used: int


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    communes_loaded: bool
    model_dir: str

