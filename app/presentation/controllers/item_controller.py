"""
Controlador para manejar las operaciones de items.
Actúa como intermediario entre la capa de presentación y los servicios de dominio.
"""

from typing import Optional, List
from app.domain.services.item_service import ItemService
from app.domain.services.search_service import SearchService
from app.domain.entities.item import Item
from app.domain.core.exceptions import ItemNotFoundError


class ItemController:
    """
    Controlador que coordina las operaciones de items entre la capa de presentación
    y los servicios de dominio.
    """

    def __init__(self, item_service: ItemService, search_service: SearchService):
        """
        Inicializa el controlador con los servicios necesarios.
        
        Args:
            item_service: Servicio para operaciones de items individuales
            search_service: Servicio para operaciones de búsqueda y filtrado
        """
        self._item_service = item_service
        self._search_service = search_service

    def get_item_by_id(self, item_id: str) -> dict:
        """
        Obtiene un item por su ID y lo convierte a formato de respuesta.
        
        Args:
            item_id: Identificador único del item
            
        Returns:
            dict: Datos del item en formato de respuesta
            
        Raises:
            ItemNotFoundError: Si el item no existe
        """
        item = self._item_service.get_item_by_id(item_id)
        return self._convert_item_to_dict(item)

    def search_items(
        self,
        query: str = "",
        limit: int = 10,
        offset: int = 0,
        sort_field: Optional[str] = None,
        sort_direction: str = "asc",
        category_id: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        available_only: bool = False
    ) -> dict:
        """
        Busca items con criterios específicos y devuelve resultados paginados.
        
        Args:
            query: Término de búsqueda
            limit: Límite de resultados por página
            offset: Desplazamiento para paginación
            sort_field: Campo para ordenamiento
            sort_direction: Dirección del ordenamiento (asc/desc)
            category_id: ID de categoría para filtrar
            brand: Marca para filtrar
            min_price: Precio mínimo
            max_price: Precio máximo
            available_only: Solo items disponibles
            
        Returns:
            dict: Resultado de la búsqueda con datos y metadatos
        """
        search_result = self._search_service.search_items(
            query=query,
            limit=limit,
            offset=offset,
            sort_field=sort_field,
            sort_direction=sort_direction,
            category_id=category_id,
            brand=brand,
            min_price=min_price,
            max_price=max_price,
            available_only=available_only
        )
        
        # Convertir items a formato de respuesta
        items_data = [self._convert_item_to_dict(item) for item in search_result.items]
        
        return {
            "data": items_data,
            "meta": {
                "total": search_result.total_count,
                "limit": limit,
                "offset": offset,
                "has_more": search_result.has_more,
                "current_page": (offset // limit) + 1,
                "total_pages": (search_result.total_count + limit - 1) // limit
            }
        }

    def get_recommendations(self, item_id: str, k: int = 5) -> List[dict]:
        """
        Obtiene recomendaciones de items similares.
        
        Args:
            item_id: ID del item base para generar recomendaciones
            k: Número máximo de recomendaciones
            
        Returns:
            List[dict]: Lista de items recomendados
        """
        recommendations = self._search_service.get_recommendations(item_id, k)
        return [self._convert_item_to_dict(item) for item in recommendations]

    def get_popular_items(self, limit: int = 10) -> List[dict]:
        """
        Obtiene los items más populares basados en cantidad vendida.
        
        Args:
            limit: Número máximo de items a devolver
            
        Returns:
            List[dict]: Lista de items populares
        """
        popular_items = self._search_service.get_popular_items(limit)
        return [self._convert_item_to_dict(item) for item in popular_items]

    def get_available_items(self, limit: int = 10) -> List[dict]:
        """
        Obtiene items que están disponibles para compra.
        
        Args:
            limit: Número máximo de items a devolver
            
        Returns:
            List[dict]: Lista de items disponibles
        """
        available_items = self._search_service.get_available_items(limit)
        return [self._convert_item_to_dict(item) for item in available_items]

    def _convert_item_to_dict(self, item: Item) -> dict:
        """
        Convierte un item del dominio a formato de respuesta.
        
        Args:
            item: Item del dominio
            
        Returns:
            dict: Item en formato de respuesta
        """
        return item.to_dict()
