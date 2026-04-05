import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    PANDASCORE_TOKEN = os.getenv("PANDASCORE_TOKEN", "")
    BASE_URL = os.getenv("BASE_URL", "https://api.pandascore.co")
    SITE_NAME = os.getenv("SITE_NAME", "Esports Matches")
    SITE_URL = os.getenv("SITE_URL", "http://127.0.0.1:5000")
    ORG_NAME = os.getenv("ORG_NAME", "Esports Matches Portal")
    ORG_LOGO = os.getenv(
        "ORG_LOGO",
        "https://dummyimage.com/200x60/111827/ffffff&text=Esports+Matches"
    )