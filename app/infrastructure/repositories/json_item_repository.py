import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from app.domain.entities.item import Item
from app.domain.repositories.item_repository import ItemRepositoryInterface
from app.infrastructure.serializers.item_serializer import ItemSerializer
from app.domain.core.exceptions import FileNotFoundError, SerializationError
from app.infrastructure.config.config import get_settings


class JsonItemRepository(ItemRepositoryInterface):
    """
    Repositorio que implementa acceso a datos desde archivos JSON.
    Sigue el principio de inversión de dependencias.
    """
    
    def __init__(self, data_file_path: Optional[str] = None):
        """
        Inicializa el repositorio.
        
        Args:
            data_file_path: Ruta al archivo JSON (opcional)
        """
        settings = get_settings()
        self._data_file = Path(data_file_path or f"{settings.data_dir}/items.json")
        self._items: List[Item] = []
        self._items_by_id: Dict[str, Item] = {}
        self._load_data()
    
    def find_by_id(self, item_id: str) -> Optional[Item]:
        """Busca un item por su ID."""
        return self._items_by_id.get(item_id)
    
    def find_all(self) -> List[Item]:
        """Obtiene todos los items."""
        return self._items.copy()
    
    def exists(self, item_id: str) -> bool:
        """Verifica si existe un item con el ID especificado."""
        return item_id in self._items_by_id
    
    def search_by_term(self, search_term: str) -> List[Item]:
        """Busca items por término de búsqueda."""
        if not search_term:
            return self._items.copy()
        
        return [
            item for item in self._items
            if item.matches_search_term(search_term)
        ]
    
    def search_by_category(self, category_id: str) -> List[Item]:
        """Busca items por categoría."""
        return [
            item for item in self._items
            if item.category_id == category_id
        ]
    
    def search_by_brand(self, brand: str) -> List[Item]:
        """Busca items por marca."""
        return [
            item for item in self._items
            if item.get_brand() and item.get_brand().lower() == brand.lower()
        ]
    
    def find_all_paginated(self, limit: int, offset: int) -> tuple[List[Item], int]:
        """Obtiene items con paginación."""
        total = len(self._items)
        start = offset
        end = start + limit
        return self._items[start:end], total
    
    def search_paginated(self, search_term: str, limit: int, offset: int) -> tuple[List[Item], int]:
        """Busca items con paginación."""
        matching_items = self.search_by_term(search_term)
        total = len(matching_items)
        start = offset
        end = start + limit
        return matching_items[start:end], total
    
    def find_all_sorted(self, sort_field: str, sort_direction: str) -> List[Item]:
        """Obtiene todos los items ordenados."""
        reverse = sort_direction.lower() == "desc"
        return sorted(
            self._items,
            key=lambda item: self._get_sort_value(item, sort_field),
            reverse=reverse
        )
    
    def search_sorted(self, search_term: str, sort_field: str, sort_direction: str) -> List[Item]:
        """Busca items y los ordena."""
        matching_items = self.search_by_term(search_term)
        reverse = sort_direction.lower() == "desc"
        return sorted(
            matching_items,
            key=lambda item: self._get_sort_value(item, sort_field),
            reverse=reverse
        )
    
    def _load_data(self) -> None:
        """Carga los datos desde el archivo JSON."""
        try:
            print(f"Loading data from {self._data_file}")
            if not self._data_file.exists():
                raise FileNotFoundError(str(self._data_file))
            
            with open(self._data_file, 'r', encoding='utf-8') as file:
                raw_data = json.load(file)
            
            if not isinstance(raw_data, list):
                raise SerializationError("JSON", "Data must be a list of items")
            
            self._items = []
            self._items_by_id = {}
            
            for item_data in raw_data:
                try:
                    # Validar datos antes de crear entidad
                    ItemSerializer.validate_data(item_data)
                    item = ItemSerializer.from_dict(item_data)
                    self._items.append(item)
                    self._items_by_id[item.id] = item
                except Exception as e:
                    # Log error but continue loading other items
                    print(f"Error loading item {item_data.get('id', 'unknown')}: {e}")
                    continue
                    
        except json.JSONDecodeError as e:
            raise SerializationError("JSON", f"Invalid JSON format: {e}")
        except Exception as e:
            if isinstance(e, (FileNotFoundError, SerializationError)):
                raise
            raise SerializationError("JSON", f"Unexpected error loading data: {e}")
    
    def _get_sort_value(self, item: Item, sort_field: str) -> Any:
        """Obtiene el valor para ordenamiento de un item."""
        if sort_field == "price":
            return float(item.price.amount)
        elif sort_field == "title":
            return item.title.lower()
        elif sort_field == "available_quantity":
            return item.available_quantity
        elif sort_field == "sold_quantity":
            return item.sold_quantity
        elif sort_field == "brand":
            return item.get_brand() or ""
        elif sort_field == "category_id":
            return item.category_id
        else:
            # Valor por defecto para campos desconocidos
            return ""
    
    def reload_data(self) -> None:
        """Recarga los datos desde el archivo."""
        self._load_data()
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del repositorio."""
        return {
            "total_items": len(self._items),
            "available_items": len([item for item in self._items if item.is_available]),
            "categories": len(set(item.category_id for item in self._items)),
            "brands": len(set(item.get_brand() for item in self._items if item.get_brand())),
            "data_file": str(self._data_file),
            "last_loaded": "now"  # En una implementación real, esto sería un timestamp
        }
