from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.item import Item


class ItemRepository(ABC):
    """
    Interfaz base para repositorios de items.
    Define operaciones básicas de CRUD.
    """
    
    @abstractmethod
    def find_by_id(self, item_id: str) -> Optional[Item]:
        """
        Busca un item por su ID.
        
        Args:
            item_id: Identificador único del item
            
        Returns:
            Item si se encuentra, None en caso contrario
        """
        pass
    
    @abstractmethod
    def find_all(self) -> List[Item]:
        """
        Obtiene todos los items.
        
        Returns:
            Lista de todos los items
        """
        pass
    
    @abstractmethod
    def exists(self, item_id: str) -> bool:
        """
        Verifica si existe un item con el ID especificado.
        
        Args:
            item_id: Identificador del item
            
        Returns:
            True si existe, False en caso contrario
        """
        pass


class SearchableRepository(ABC):
    """
    Interfaz para repositorios que soportan búsqueda.
    Segregación de interfaces para operaciones de búsqueda.
    """
    
    @abstractmethod
    def search_by_term(self, search_term: str) -> List[Item]:
        """
        Busca items por término de búsqueda.
        
        Args:
            search_term: Término a buscar en título, marca o modelo
            
        Returns:
            Lista de items que coinciden con el término
        """
        pass
    
    @abstractmethod
    def search_by_category(self, category_id: str) -> List[Item]:
        """
        Busca items por categoría.
        
        Args:
            category_id: ID de la categoría
            
        Returns:
            Lista de items de la categoría especificada
        """
        pass
    
    @abstractmethod
    def search_by_brand(self, brand: str) -> List[Item]:
        """
        Busca items por marca.
        
        Args:
            brand: Nombre de la marca
            
        Returns:
            Lista de items de la marca especificada
        """
        pass


class PaginatedRepository(ABC):
    """
    Interfaz para repositorios que soportan paginación.
    Segregación de interfaces para operaciones paginadas.
    """
    
    @abstractmethod
    def find_all_paginated(self, limit: int, offset: int) -> tuple[List[Item], int]:
        """
        Obtiene items con paginación.
        
        Args:
            limit: Número máximo de items a retornar
            offset: Número de items a saltar
            
        Returns:
            Tupla con (items, total_count)
        """
        pass
    
    @abstractmethod
    def search_paginated(
        self, 
        search_term: str, 
        limit: int, 
        offset: int
    ) -> tuple[List[Item], int]:
        """
        Busca items con paginación.
        
        Args:
            search_term: Término de búsqueda
            limit: Número máximo de items a retornar
            offset: Número de items a saltar
            
        Returns:
            Tupla con (items, total_count)
        """
        pass


class SortableRepository(ABC):
    """
    Interfaz para repositorios que soportan ordenamiento.
    Segregación de interfaces para operaciones de ordenamiento.
    """
    
    @abstractmethod
    def find_all_sorted(self, sort_field: str, sort_direction: str) -> List[Item]:
        """
        Obtiene todos los items ordenados.
        
        Args:
            sort_field: Campo por el cual ordenar
            sort_direction: Dirección del ordenamiento ('asc' o 'desc')
            
        Returns:
            Lista de items ordenados
        """
        pass
    
    @abstractmethod
    def search_sorted(
        self, 
        search_term: str, 
        sort_field: str, 
        sort_direction: str
    ) -> List[Item]:
        """
        Busca items y los ordena.
        
        Args:
            search_term: Término de búsqueda
            sort_field: Campo por el cual ordenar
            sort_direction: Dirección del ordenamiento ('asc' o 'desc')
            
        Returns:
            Lista de items que coinciden con la búsqueda, ordenados
        """
        pass



class ItemRepositoryInterface(ItemRepository, SearchableRepository, PaginatedRepository, SortableRepository):
    """
    Interfaz completa para repositorios de items.
    Combina todas las capacidades: CRUD, búsqueda, paginación y ordenamiento.
    """
    pass
