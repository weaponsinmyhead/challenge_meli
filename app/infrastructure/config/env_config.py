"""
Configuración de variables de entorno para la aplicación.
"""

import os
from typing import Dict, Optional
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class EnvConfig:
    """Configuración centralizada de variables de entorno."""
    
    # Configuración de la aplicación
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    DATA_SOURCE: str = os.getenv("DATA_SOURCE", "json")
    DATA_DIR: str = os.getenv("DATA_DIR", "app/infrastructure/data")
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    
    # CORS
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    CORS_METHODS: list = os.getenv("CORS_METHODS", "GET,POST").split(",")
    CORS_HEADERS: list = os.getenv("CORS_HEADERS", "X-API-Key,Content-Type,Authorization").split(",")
    
    @classmethod
    def get_api_keys(cls) -> Dict[str, str]:
        """
        Obtiene las API keys desde variables de entorno.
        
        Returns:
            Dict[str, str]: Diccionario con API key -> rol
        """
        api_keys = {}
        
        # API Keys específicas
        admin_key = os.getenv("API_KEY_ADMIN", "")
        user_key = os.getenv("API_KEY_USER", "")
        readonly_key = os.getenv("API_KEY_READONLY", "")
        
        # Procesar API keys en formato "clave:rol"
        for env_key, default_role in [
            (admin_key, "admin"),
            (user_key, "user"), 
            (readonly_key, "readonly")
        ]:
            if env_key:
                if ":" in env_key:
                    key, role = env_key.split(":", 1)
                    api_keys[key] = role
                else:
                    api_keys[env_key] = default_role
        
        # API Key genérica para desarrollo
        generic_key = os.getenv("X_API_KEY", "")
        if generic_key:
            if ":" in generic_key:
                key, role = generic_key.split(":", 1)
                api_keys[key] = role
            else:
                api_keys[generic_key] = "user"
        
        # Si no hay API keys en .env, usar valores por defecto para desarrollo
        if not api_keys:
            api_keys = {
                "ml-api-key-admin": "admin",
                "ml-api-key-user": "user",
                "ml-api-key-readonly": "readonly"
            }
        
        return api_keys
    
    @classmethod
    def get_public_routes(cls) -> set:
        """
        Obtiene las rutas públicas que no requieren autenticación.
        
        Returns:
            set: Conjunto de rutas públicas
        """
        return {
            "/docs",
            "/redoc", 
            "/openapi.json",
            "/api/v1/health",
            "/",
            "/favicon.ico",
            "/static",
            "/test"
        }

# Instancia global de configuración
config = EnvConfig()
