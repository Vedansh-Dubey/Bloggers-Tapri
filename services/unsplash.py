import os
import requests
import logging
from urllib.parse import quote
from utils import Config, config

logger = logging.getLogger(__name__)

UNSPLASH_ACCESS_KEY = config.UNSPLASH_ACCESS_KEY
UNSPLASH_URL = "https://api.unsplash.com/photos/random"

SAVE_DIR = os.path.join("outputs", "images")
os.makedirs(SAVE_DIR, exist_ok=True)

def fetch_banner(topic: str) -> str:
    headers = {
        "Accept-Version": "v1",
        "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
    }

    params = {
        "query": topic,
        "orientation": "landscape"
    }

    try:
        logger.info(f"🔍 Searching Unsplash for: {topic}")
        response = requests.get(UNSPLASH_URL, headers=headers, params=params)
        response.raise_for_status()

        data = response.json()
        image_url = data["urls"]["regular"]
        author = data["user"]["name"]

        image_data = requests.get(image_url).content
        filename = f"{quote(topic)}.jpg"
        save_path = os.path.join(SAVE_DIR, filename)

        with open(save_path, "wb") as f:
            f.write(image_data)

        logger.info(f"✅ Banner saved: {save_path} (by {author})")
        return save_path

    except Exception as e:
        logger.error(f"❌ Failed to fetch banner: {e}")
        return os.path.join("assets", "default_banner.png")
