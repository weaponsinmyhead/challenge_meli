from pydantic import BaseModel
from typing import Optional
import os
import logging

class Settings(BaseModel):
    """Configuración de la aplicación."""
    
    # Configuración de datos
    data_source: str = "json"  # "json" o "csv"
    data_dir: str = "app/infrastructure/data"
    
    # Configuración de la API
    api_title: str = "MercadoLibre Items API"
    api_description: str = "API para consultar información de productos"
    api_version: str = "1.0.0"
    
    # Configuración de logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configuración de performance
    cache_ttl: int = 300  # 5 minutos
    max_search_results: int = 100
    
# Instancia global de configuración
settings = Settings(
    data_source=os.getenv("DATA_SOURCE", "json"),
    data_dir=os.getenv("DATA_DIR", "app/infrastructure/data"),
    log_level=os.getenv("LOG_LEVEL", "INFO")
)

# Configurar logging global
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format=settings.log_format,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

# Logger principal de la aplicación
app_logger = logging.getLogger("mercadolibre_api")

def get_settings() -> Settings:
    """Función para obtener la configuración global."""
    return settings
