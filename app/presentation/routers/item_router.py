"""
Router para endpoints de items.
Define las rutas HTTP y delega la lógica al controlador.
"""

from fastapi import APIRouter, Query, Path, Depends
from typing import Optional
from app.presentation.controllers.item_controller import ItemController
from app.domain.core.api_response import ItemResponse, SearchResponse, ItemsResponse
from app.domain.core.dependencies import get_item_controller

router = APIRouter(prefix="/api/v1")


@router.get(
    "/health",
    tags=["health"],
    summary="Verificar el estado del servicio",
    description="Endpoint de monitoreo que verifica el estado del servicio. Útil para balanceadores de carga y sistemas de monitoreo.",
    responses={
        200: {
            "description": "Servicio funcionando correctamente",
            "content": {
                "application/json": {
                    "example": {
                        "status": "ok"
                    }
                }
            }
        }
    }
)
def health():
    """
    Endpoint de salud del servicio.
    
    Returns:
        dict: Estado del servicio
    """
    return {"status": "ok"}


@router.get(
    "/items/popular",
    response_model=ItemsResponse,
    tags=["items"],
    summary="Obtener productos más populares",
    description="Devuelve los productos más populares ordenados por cantidad vendida. Útil para mostrar productos destacados y análisis de tendencias.",
    responses={
        200: {
            "description": "Lista de productos más populares ordenados por cantidad vendida",
            "content": {
                "application/json": {
                    "example": {
                        "data": [
                            {
                                "id": "MLA777888999",
                                "title": "Smartphone Samsung Galaxy A34 128GB",
                                "category_id": "MLA1055",
                                "price": 299999.0,
                                "currency_id": "ARS",
                                "available_quantity": 25,
                                "sold_quantity": 980,
                                "condition": "new"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def get_popular_items(
    limit: int = Query(
        10, 
        ge=1, 
        le=50, 
        description="Número máximo de productos populares a devolver (1-50)",
        examples=[10]
    ),
    controller: ItemController = Depends(get_item_controller)
) -> ItemsResponse:
    """
    Obtiene los productos más populares basados en cantidad vendida.
    
    Args:
        limit: Número máximo de productos populares (1-50)
        controller: Controlador de items inyectado
        
    Returns:
        ItemsResponse: Lista de productos populares ordenados por cantidad vendida
        
    Raises:
        500: Error interno del servidor
    """
    return {"data": controller.get_popular_items(limit)}


@router.get(
    "/items/available",
    response_model=ItemsResponse,
    tags=["items"],
    summary="Obtener productos disponibles",
    description="Devuelve productos con stock disponible (quantity > 0) ordenados por cantidad disponible. Útil para filtros de disponibilidad inmediata.",
    responses={
        200: {
            "description": "Lista de productos disponibles para compra",
            "content": {
                "application/json": {
                    "example": {
                        "data": [
                            {
                                "id": "MLA443322110",
                                "title": "Mouse Inalámbrico Logitech MX Master 3S",
                                "category_id": "MLA43156",
                                "price": 64999.0,
                                "currency_id": "ARS",
                                "available_quantity": 40,
                                "sold_quantity": 1500,
                                "condition": "new"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def get_available_items(
    limit: int = Query(
        10, 
        ge=1, 
        le=50, 
        description="Número máximo de productos disponibles a devolver (1-50)",
        examples=[10]
    ),
    controller: ItemController = Depends(get_item_controller)
) -> ItemsResponse:
    """
    Obtiene productos que están disponibles para compra (con stock > 0).
    
    Args:
        limit: Número máximo de productos disponibles (1-50)
        controller: Controlador de items inyectado
        
    Returns:
        ItemsResponse: Lista de productos disponibles ordenados por cantidad de stock
        
    Raises:
        500: Error interno del servidor
    """
    return {"data": controller.get_available_items(limit)}


@router.get(
    "/items",
    response_model=SearchResponse,
    tags=["search"],
    summary="Búsqueda avanzada de productos",
    description="Búsqueda de productos con múltiples filtros: texto, categoría, marca, precio y disponibilidad. Incluye ordenamiento y paginación.",
    responses={
        200: {
            "description": "Lista de productos que coinciden con los criterios de búsqueda"
        },
        400: {
            "description": "Criterios de búsqueda inválidos"
        }
    }
)
async def search_items(
    q: str = Query(
        "", 
        description="Texto a buscar en título, marca o modelo del producto",
        examples=["iphone"],
        max_length=100
    ),
    limit: int = Query(
        10, 
        ge=1, 
        le=100, 
        description="Número máximo de resultados por página (1-100)",
        examples=[10]
    ),
    offset: int = Query(
        0, 
        ge=0, 
        description="Número de resultados a saltar para paginación",
        examples=[0]
    ),
    sort_field: Optional[str] = Query(
        None, 
        description="Campo de ordenamiento",
        examples=["price"]
    ),
    sort_direction: str = Query(
        "asc", 
        description="Dirección de ordenamiento",
        examples=["desc"],
        pattern="^(asc|desc)$"
    ),
    category_id: Optional[str] = Query(
        None, 
        description="ID de categoría para filtrar productos",
        examples=["MLA1055"]
    ),
    brand: Optional[str] = Query(
        None, 
        description="Marca específica para filtrar productos",
        examples=["Apple"]
    ),
    min_price: Optional[float] = Query(
        None, 
        ge=0, 
        description="Precio mínimo en pesos argentinos",
        examples=[100000.0]
    ),
    max_price: Optional[float] = Query(
        None, 
        ge=0, 
        description="Precio máximo en pesos argentinos",
        examples=[500000.0]
    ),
    available_only: bool = Query(
        False, 
        description="Si es true, solo devuelve productos con stock disponible",
        examples=[False]
    ),
    controller: ItemController = Depends(get_item_controller)
) -> SearchResponse:
    """
    Busca productos con criterios específicos y devuelve resultados paginados.
    """
    return controller.search_items(
        query=q,
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


@router.get(
    "/items/{item_id}",
    response_model=ItemResponse,
    tags=["items"],
    summary="Obtener detalle completo de producto",
    description="Devuelve información completa de un producto: título, precio, imágenes, atributos, envío, vendedor y garantía.",
    responses={
        200: {
            "description": "Detalle del producto solicitado"
        },
        404: {
            "description": "El producto no fue encontrado",
            "content": {
                "application/json": {
                    "example": {
                        "code": "ITEM_NOT_FOUND",
                        "message": "Item with id 'MLA999999999' not found",
                        "status": 404,
                        "cause": ["Item ID: MLA999999999"]
                    }
                }
            }
        }
    }
)
async def get_item(
    item_id: str = Path(
        ..., 
        description="Identificador único del producto (formato: MLA + números)",
        examples=["MLA111222333"],
        min_length=1,
        max_length=20
    ),
    controller: ItemController = Depends(get_item_controller)
) -> ItemResponse:
    """
    Obtiene el detalle completo de un producto específico.
    
    Args:
        item_id: Identificador único del producto
        controller: Controlador de items inyectado
        
    Returns:
        ItemResponse: Respuesta con el detalle del producto
        
    Raises:
        404: Producto no encontrado
        400: Parámetros inválidos
        500: Error interno del servidor
    """
    return controller.get_item_by_id(item_id)


@router.get(
    "/items/{item_id}/recommendations",
    response_model=ItemsResponse,
    tags=["recommendations"],
    summary="Obtener productos recomendados",
    description="Sistema de recomendaciones basado en similitud: marca, categoría, precio y popularidad. Algoritmo de puntuación por características similares.",
    responses={
        200: {
            "description": "Lista de productos recomendados"
        },
        404: {
            "description": "El producto base no fue encontrado"
        }
    }
)
async def get_recommendations(
    item_id: str = Path(
        ..., 
        description="ID del producto base para generar recomendaciones",
        examples=["MLA111222333"]
    ),
    k: int = Query(
        5, 
        ge=1, 
        le=20, 
        description="Número máximo de recomendaciones a devolver (1-20)",
        examples=[5]
    ),
    controller: ItemController = Depends(get_item_controller)
) -> ItemsResponse:
    """
    Obtiene recomendaciones de productos similares basados en un producto específico.
    
    Args:
        item_id: ID del producto base para generar recomendaciones
        k: Número máximo de recomendaciones (1-20)
        controller: Controlador de items inyectado
        
    Returns:
        ItemsResponse: Lista de productos recomendados ordenados por similitud
        
    Raises:
        404: Producto base no encontrado
        500: Error interno del servidor
    """
    return {"data": controller.get_recommendations(item_id, k)}
