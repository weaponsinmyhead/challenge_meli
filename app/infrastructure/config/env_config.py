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
    def get_api_keys(cls) -> set:
        """
        Obtiene las API keys válidas desde variables de entorno.
        
        Returns:
            set: Conjunto de API keys válidas
        """
        api_keys = set()
        
        # Cargar API key desde variable de entorno
        api_key = os.getenv("API_KEY", "")
        if api_key:
            api_keys.add(api_key)
        
        # Si no hay API key en .env, usar valor por defecto para desarrollo
        if not api_keys:
            api_keys.add("meli2024abc123xyz789")
        
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
