"""
Dependencias para inyección de dependencias.
Centraliza la creación y configuración de servicios y repositorios.
"""

from functools import lru_cache
from app.infrastructure.repositories.json_item_repository import JsonItemRepository
from app.domain.services.item_service import ItemService
from app.domain.services.search_service import SearchService
from app.presentation.controllers.item_controller import ItemController


@lru_cache()
def get_item_repository() -> JsonItemRepository:
    """
    Obtiene una instancia del repositorio de items.
    
    
    Returns:
        Instancia del repositorio JSON
    """
    return JsonItemRepository()


@lru_cache()
def get_item_service() -> ItemService:
    """
    Obtiene una instancia del servicio de items
   
    
    Returns:
        Instancia del servicio de items
    """
    repository = get_item_repository()
    return ItemService(repository)


@lru_cache()
def get_search_service() -> SearchService:
    """
    Obtiene una instancia del servicio de búsqueda.
    
    
    Returns:
        Instancia del servicio de búsqueda
    """
    repository = get_item_repository()
    return SearchService(repository)


@lru_cache()
def get_item_controller() -> ItemController:
    """
    Obtiene una instancia del controlador de items.
    
    
    Returns:
        Instancia del controlador de items
    """
    item_service = get_item_service()
    search_service = get_search_service()
    return ItemController(item_service, search_service)
