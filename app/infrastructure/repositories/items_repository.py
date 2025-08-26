from __future__ import annotations
from typing import List, Dict, Tuple
from app.infrastructure.repositories.files_repository import load_items
from app.domain.entities.item import Item

class ItemsRepository:
    """Repository que usa files_repo.load_items() y provee una API de lectura en memoria con entidades DDD."""
    def __init__(self) -> None:
        self._reload()

    def _reload(self) -> None:
        self._index: List[Item] = load_items()  # Entidades DDD Item
        self._by_id: Dict[str, Item] = {item.id: item for item in self._index}

    def get_by_id(self, item_id: str) -> Item | None:
        return self._by_id.get(item_id)
    
    def find_by_id(self, item_id: str) -> Item | None:
        """Alias para compatibilidad con SearchService."""
        return self.get_by_id(item_id)
    
    def find_all(self) -> List[Item]:
        """Retorna todas las entidades Item."""
        return self._index

    def search_by_term(self, query: str) -> List[Item]:
        """Busca items por término usando lógica de dominio."""
        return [
            item for item in self._index
            if item.matches_search_term(query)
        ]
    
    def search_by_category(self, category_id: str) -> List[Item]:
        """Busca items por categoría."""
        return [item for item in self._index if item.category_id == category_id]
    
    def search_by_brand(self, brand: str) -> List[Item]:
        """Busca items por marca usando lógica de dominio."""
        brand_lower = brand.lower()
        return [
            item for item in self._index
            if item.get_brand() and brand_lower in item.get_brand().lower()
        ]
    
    def search(self, q: str, limit: int, offset: int, sort: str | None) -> Tuple[List[Dict], int]:
        """Método legacy para compatibilidad - convierte entidades a dicts."""
        items = self.search_by_term(q)
        
        if sort:
            try:
                field, direction = sort.split(":")
                if field == "price":
                    items.sort(key=lambda x: float(x.price.amount), reverse=(direction.lower() == "desc"))
                elif field == "title":
                    items.sort(key=lambda x: x.title.lower(), reverse=(direction.lower() == "desc"))
                elif field == "available_quantity":
                    items.sort(key=lambda x: x.available_quantity, reverse=(direction.lower() == "desc"))
            except Exception:
                pass
        
        total = len(items)
        paginated_items = items[offset:offset + limit]
        # Convertir a dicts para compatibilidad
        return [item.to_dict() for item in paginated_items], total

    def recommendations(self, item_id: str, k: int = 5) -> List[Dict]:
        """Método legacy para compatibilidad - convierte entidades a dicts."""
        item = self._by_id.get(item_id)
        if not item:
            return []
        
        candidates = [
            candidate for candidate in self._index 
            if candidate.category_id == item.category_id and candidate.id != item_id
        ]
        return [item.to_dict() for item in candidates[:k]]
