from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"
STREAMLIT_DATA_DIR = APP_DIR / "data" / "streamlit"
MODEL_DIR = PROJECT_ROOT / "notebooks" / "Models"

META_PATH = MODEL_DIR / "meta_6modeles.pkl"
COMMUNES_PATH = STREAMLIT_DATA_DIR / "communes_streamlit.csv"

