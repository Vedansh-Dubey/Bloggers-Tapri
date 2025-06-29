import os
from typing import Optional
from dotenv import load_dotenv
from loguru import logger

load_dotenv(override=True)

class Config:
    """Singleton configuration manager using properties."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance
    
    @property
    def GROQ_API_KEY(self) -> str:
        return self._get_required("GROQ_API_KEY")
    
    @property
    def DEV_TO_API_KEY(self) -> str:
        return self._get_required("DEV_TO_API_KEY")
    
    @property
    def GEMINI_API_KEY(self) -> str:
        return self._get_required("GEMINI_API_KEY")
    
    @property
    def UNSPLASH_ACCESS_KEY(self) -> str:
        return self._get_required("UNSPLASH_ACCESS_KEY")
    
    @property
    def UNSPLASH_SECRET_KEY(self) -> str:
        return self._get_required("UNSPLASH_SECRET_KEY")
    
    @property
    def LINKEDIN_CLIENT_ID(self) -> Optional[str]:
        return os.getenv("LINKEDIN_CLIENT_ID")
    
    @property
    def LINKEDIN_CLIENT_SECRET(self) -> Optional[str]:
        return os.getenv("LINKEDIN_CLIENT_SECRET")
    
    @property
    def CHROMA_DB_PATH(self) -> str:
        return os.getenv("CHROMA_DB_PATH", "./chroma_data")
    
    def _get_required(self, var_name: str) -> str:
        value = os.getenv(var_name)
        if not value:
            raise EnvironmentError(
                f"Missing required environment variable: {var_name}. "
                "Please check your .env file."
            )
        return value
    
    def validate(self) -> bool:
        """Validate configuration (call this explicitly in app startup)"""
        try:
            _ = self.GROQ_API_KEY
            _ = self.DEV_TO_API_KEY
            _ = self.GEMINI_API_KEY
            _ = self.UNSPLASH_ACCESS_KEY
            _ = self.UNSPLASH_SECRET_KEY
            
            if not self.LINKEDIN_CLIENT_ID or not self.LINKEDIN_CLIENT_SECRET:
                logger.warning(
                    "LinkedIn OAuth credentials not configured - "
                    "publishing to LinkedIn will be disabled"
                )
                
            return True
        except EnvironmentError as e:
            logger.critical(str(e))
            return False

config = Config()

# Validate immediately on import
if not config.validate():
    raise RuntimeError("Configuration validation failed")