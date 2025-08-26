from typing import List, Optional, Tuple
from dataclasses import dataclass
from app.domain.entities.item import Item
from app.domain.repositories.item_repository import SearchableRepository, PaginatedRepository, SortableRepository
from app.domain.core.exceptions import InvalidSearchCriteriaError


@dataclass
class SearchCriteria:
    """Criterios de búsqueda encapsulados."""
    query: str = ""
    limit: int = 10
    offset: int = 0
    sort_field: Optional[str] = None
    sort_direction: str = "asc"
    category_id: Optional[str] = None
    brand: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    available_only: bool = False
    
    def __post_init__(self):
        """Validaciones de criterios de búsqueda."""
        if self.limit <= 0:
            raise InvalidSearchCriteriaError("limit", str(self.limit), "Must be positive")
        
        if self.offset < 0:
            raise InvalidSearchCriteriaError("offset", str(self.offset), "Cannot be negative")
        
        if self.sort_direction not in ["asc", "desc"]:
            raise InvalidSearchCriteriaError("sort_direction", self.sort_direction, "Must be 'asc' or 'desc'")
        
        if self.min_price is not None and self.max_price is not None:
            if self.min_price > self.max_price:
                raise InvalidSearchCriteriaError("price_range", f"{self.min_price}-{self.max_price}", "Min price cannot be greater than max price")


@dataclass
class SearchResult:
    """Resultado de búsqueda encapsulado."""
    items: List[Item]
    total_count: int
    criteria: SearchCriteria
    
    @property
    def has_more(self) -> bool:
        """Verifica si hay más resultados disponibles."""
        return self.criteria.offset + len(self.items) < self.total_count
    
    @property
    def current_page(self) -> int:
        """Calcula la página actual."""
        return (self.criteria.offset // self.criteria.limit) + 1
    
    @property
    def total_pages(self) -> int:
        """Calcula el total de páginas."""
        return (self.total_count + self.criteria.limit - 1) // self.criteria.limit


class SearchService:
    """
    Servicio especializado en búsquedas y filtros.
    Contiene la lógica de negocio para operaciones de búsqueda.
    """
    
    def __init__(self, repository: SearchableRepository):
        """
        Inicializa el servicio con un repositorio de búsqueda.
        
        Args:
            repository: Repositorio que implementa SearchableRepository
        """
        self._repository = repository
    
    def search(self, criteria: SearchCriteria) -> SearchResult:
        """
        Realiza una búsqueda con los criterios especificados.
        
        Args:
            criteria: Criterios de búsqueda
            
        Returns:
            Resultado de la búsqueda
        """
        # Obtener items base según criterios
        items = self._get_base_items(criteria)
        
        # Aplicar filtros adicionales
        items = self._apply_filters(items, criteria)
        
        # Aplicar ordenamiento
        items = self._apply_sorting(items, criteria)
        
        # Aplicar paginación
        total_count = len(items)
        paginated_items = self._apply_pagination(items, criteria)
        
        return SearchResult(
            items=paginated_items,
            total_count=total_count,
            criteria=criteria
        )
    
    def search_by_term(self, query: str, limit: int = 10, offset: int = 0) -> SearchResult:
        """
        Búsqueda simple por término.
        
        Args:
            query: Término de búsqueda
            limit: Límite de resultados
            offset: Desplazamiento
            
        Returns:
            Resultado de la búsqueda
        """
        criteria = SearchCriteria(
            query=query,
            limit=limit,
            offset=offset
        )
        return self.search(criteria)
    
    def search_by_category(self, category_id: str, limit: int = 10, offset: int = 0) -> SearchResult:
        """
        Búsqueda por categoría.
        
        Args:
            category_id: ID de la categoría
            limit: Límite de resultados
            offset: Desplazamiento
            
        Returns:
            Resultado de la búsqueda
        """
        criteria = SearchCriteria(
            category_id=category_id,
            limit=limit,
            offset=offset
        )
        return self.search(criteria)
    
    def search_by_brand(self, brand: str, limit: int = 10, offset: int = 0) -> SearchResult:
        """
        Búsqueda por marca.
        
        Args:
            brand: Nombre de la marca
            limit: Límite de resultados
            offset: Desplazamiento
            
        Returns:
            Resultado de la búsqueda
        """
        criteria = SearchCriteria(
            brand=brand,
            limit=limit,
            offset=offset
        )
        return self.search(criteria)
    
    def search_by_price_range(
        self, 
        min_price: float, 
        max_price: float, 
        limit: int = 10, 
        offset: int = 0
    ) -> SearchResult:
        """
        Búsqueda por rango de precios.
        
        Args:
            min_price: Precio mínimo
            max_price: Precio máximo
            limit: Límite de resultados
            offset: Desplazamiento
            
        Returns:
            Resultado de la búsqueda
        """
        criteria = SearchCriteria(
            min_price=min_price,
            max_price=max_price,
            limit=limit,
            offset=offset
        )
        return self.search(criteria)
    
    def _get_base_items(self, criteria: SearchCriteria) -> List[Item]:
        """Obtiene los items base según los criterios principales."""
        if criteria.query:
            return self._repository.search_by_term(criteria.query)
        elif criteria.category_id:
            return self._repository.search_by_category(criteria.category_id)
        elif criteria.brand:
            return self._repository.search_by_brand(criteria.brand)
        else:
            # Si no hay criterios específicos, obtener todos
            if hasattr(self._repository, 'find_all'):
                return self._repository.find_all()
            return []
    
    def _apply_filters(self, items: List[Item], criteria: SearchCriteria) -> List[Item]:
        """Aplica filtros adicionales a los items.
        
        Utiliza la lógica de dominio encapsulada en las entidades.
        """
        filtered_items = items
        
        # Filtro por disponibilidad - usa propiedad de dominio
        if criteria.available_only:
            filtered_items = [item for item in filtered_items if item.is_available]
        
        # Filtro por rango de precios - usa método de dominio
        if criteria.min_price is not None or criteria.max_price is not None:
            filtered_items = [
                item for item in filtered_items
                if item.is_in_price_range(criteria.min_price, criteria.max_price)
            ]
        
        return filtered_items
    
    def _apply_sorting(self, items: List[Item], criteria: SearchCriteria) -> List[Item]:
        """Aplica ordenamiento a los items."""
        if not criteria.sort_field:
            return items
        
        reverse = criteria.sort_direction == "desc"
        
        try:
            return sorted(
                items,
                key=lambda item: self._get_sort_value(item, criteria.sort_field),
                reverse=reverse
            )
        except (KeyError, AttributeError):
            # Si el campo de ordenamiento no existe, retornar sin ordenar
            return items
    
    def _apply_pagination(self, items: List[Item], criteria: SearchCriteria) -> List[Item]:
        """Aplica paginación a los items."""
        start = criteria.offset
        end = start + criteria.limit
        return items[start:end]
    
    # Método removido - ahora usa item.is_in_price_range() de la entidad
    
    def _get_sort_value(self, item: Item, sort_field: str):
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
        else:
            # Intentar acceder al atributo directamente
            return getattr(item, sort_field, "")
    
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
    ) -> SearchResult:
        """
        Método principal de búsqueda con todos los criterios.
        
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
            SearchResult: Resultado de la búsqueda con datos y metadatos
        """
        criteria = SearchCriteria(
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
        return self.search(criteria)
    
    def get_recommendations(self, item_id: str, k: int = 5) -> List[Item]:
        """
        Obtiene recomendaciones de productos similares basados en un item específico.
        
        Args:
            item_id: ID del item base para generar recomendaciones
            k: Número máximo de recomendaciones
            
        Returns:
            Lista de items recomendados ordenados por similitud
        """
        # Obtener el item base
        base_item = None
        if hasattr(self._repository, 'find_by_id'):
            base_item = self._repository.find_by_id(item_id)
        
        if not base_item:
            return []
        
        # Obtener todos los items excepto el base
        all_items = []
        if hasattr(self._repository, 'find_all'):
            all_items = [item for item in self._repository.find_all() if item.id != item_id]
        
        # Calcular similitud y ordenar - usa lógica de dominio
        scored_items = []
        for item in all_items:
            score = base_item.calculate_similarity_with(item)
            if score > 0:  # Solo incluir items con alguna similitud
                scored_items.append((item, score))
        
        # Ordenar por score descendente, luego por popularidad
        scored_items.sort(key=lambda x: (x[1], x[0].sold_quantity), reverse=True)
        
        # Retornar los top k items
        return [item for item, score in scored_items[:k]]
    
    def get_popular_items(self, limit: int = 10) -> List[Item]:
        """
        Obtiene los items más populares basados en cantidad vendida.
        
        Args:
            limit: Número máximo de items a devolver
            
        Returns:
            Lista de items populares ordenados por cantidad vendida
        """
        all_items = []
        if hasattr(self._repository, 'find_all'):
            all_items = self._repository.find_all()
        
        # Ordenar por cantidad vendida descendente
        sorted_items = sorted(
            all_items, 
            key=lambda item: item.sold_quantity, 
            reverse=True
        )
        
        return sorted_items[:limit]
    
    def get_available_items(self, limit: int = 10) -> List[Item]:
        """
        Obtiene items que están disponibles para compra (stock > 0).
        
        Args:
            limit: Número máximo de items a devolver
            
        Returns:
            Lista de items disponibles ordenados por cantidad de stock
        """
        all_items = []
        if hasattr(self._repository, 'find_all'):
            all_items = self._repository.find_all()
        
        # Filtrar solo items disponibles
        available_items = [item for item in all_items if item.is_available]
        
        # Ordenar por cantidad disponible descendente
        sorted_items = sorted(
            available_items, 
            key=lambda item: item.available_quantity, 
            reverse=True
        )
        
        return sorted_items[:limit]
    
    def _calculate_similarity_score(self, base_item: Item, candidate_item: Item) -> float:
        """Calcula el score de similitud entre dos items.
        
        Delega a la lógica de dominio de la entidad Item.
        """
        return base_item.calculate_similarity_with(candidate_item)
