from typing import List, Optional
from app.domain.entities.item import Item
from app.domain.repositories.item_repository import ItemRepository
from app.domain.core.exceptions import ItemNotFoundError


class ItemService:
    """
    Servicio de dominio para operaciones con items.
    Contiene la lógica de negocio y validaciones de dominio.
    """
    
    def __init__(self, repository: ItemRepository):
        """
        Inicializa el servicio con un repositorio.
        
        Args:
            repository: Repositorio que implementa ItemRepository
        """
        self._repository = repository
    
    def get_item_by_id(self, item_id: str) -> Item:
        """
        Obtiene un item por su ID.
        
        Args:
            item_id: Identificador único del item
            
        Returns:
            Item encontrado
            
        Raises:
            ItemNotFoundError: Si el item no existe
        """
        if not item_id:
            raise ValueError("Item ID cannot be empty")
        
        item = self._repository.find_by_id(item_id)
        if not item:
            raise ItemNotFoundError(item_id)
        
        return item
    
    def get_all_items(self) -> List[Item]:
        """
        Obtiene todos los items.
        
        Returns:
            Lista de todos los items
        """
        return self._repository.find_all()
    
    def item_exists(self, item_id: str) -> bool:
        """
        Verifica si un item existe.
        
        Args:
            item_id: Identificador del item
            
        Returns:
            True si existe, False en caso contrario
        """
        if not item_id:
            return False
        
        return self._repository.exists(item_id)
    
    def get_available_items(self) -> List[Item]:
        """
        Obtiene solo los items disponibles (con stock > 0).
        
        Returns:
            Lista de items disponibles
        """
        all_items = self._repository.find_all()
        return [item for item in all_items if item.is_available]
    
    def get_items_by_brand(self, brand: str) -> List[Item]:
        """
        Obtiene items de una marca específica.
        
        Args:
            brand: Nombre de la marca
            
        Returns:
            Lista de items de la marca especificada
        """
        if not brand:
            return []
        
        all_items = self._repository.find_all()
        return [
            item for item in all_items 
            if item.get_brand() and item.get_brand().lower() == brand.lower()
        ]
    
    def get_items_by_category(self, category_id: str) -> List[Item]:
        """
        Obtiene items de una categoría específica.
        
        Args:
            category_id: ID de la categoría
            
        Returns:
            Lista de items de la categoría especificada
        """
        if not category_id:
            return []
        
        all_items = self._repository.find_all()
        return [
            item for item in all_items 
            if item.category_id == category_id
        ]
    
    def get_items_by_price_range(self, min_price: float, max_price: float) -> List[Item]:
        """
        Obtiene items dentro de un rango de precios.
        
        Args:
            min_price: Precio mínimo
            max_price: Precio máximo
            
        Returns:
            Lista de items dentro del rango de precios
        """
        if min_price < 0 or max_price < 0:
            raise ValueError("Prices cannot be negative")
        
        if min_price > max_price:
            raise ValueError("Min price cannot be greater than max price")
        
        all_items = self._repository.find_all()
        return [
            item for item in all_items 
            if min_price <= float(item.price.amount) <= max_price
        ]
    
    def get_popular_items(self, limit: int = 10) -> List[Item]:
        """
        Obtiene los items más populares (por cantidad vendida).
        
        Args:
            limit: Número máximo de items a retornar
            
        Returns:
            Lista de items ordenados por popularidad
        """
        if limit <= 0:
            raise ValueError("Limit must be positive")
        
        all_items = self._repository.find_all()
        sorted_items = sorted(
            all_items, 
            key=lambda item: item.sold_quantity, 
            reverse=True
        )
        return sorted_items[:limit]
    
    def get_new_items(self, limit: int = 10) -> List[Item]:
        """
        Obtiene los items más nuevos (por cantidad disponible).
        
        Args:
            limit: Número máximo de items a retornar
            
        Returns:
            Lista de items ordenados por disponibilidad
        """
        if limit <= 0:
            raise ValueError("Limit must be positive")
        
        all_items = self._repository.find_all()
        sorted_items = sorted(
            all_items, 
            key=lambda item: item.available_quantity, 
            reverse=True
        )
        return sorted_items[:limit]
    
    def validate_item_data(self, item_data: dict) -> bool:
        """
        Valida los datos de un item antes de procesarlo.
        
        Args:
            item_data: Diccionario con los datos del item
            
        Returns:
            True si los datos son válidos
            
        Raises:
            ValueError: Si los datos son inválidos
        """
        required_fields = ['id', 'title', 'category_id', 'price', 'available_quantity']
        
        for field in required_fields:
            if field not in item_data or not item_data[field]:
                raise ValueError(f"Required field '{field}' is missing or empty")
        
        if item_data.get('available_quantity', 0) < 0:
            raise ValueError("Available quantity cannot be negative")
        
        if item_data.get('sold_quantity', 0) < 0:
            raise ValueError("Sold quantity cannot be negative")
        
        return True
