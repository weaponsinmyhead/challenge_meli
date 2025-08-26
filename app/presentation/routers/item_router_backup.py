"""
Router para endpoints de items.
Define las rutas HTTP y delega la lógica al controlador.
"""

from fastapi import APIRouter, Query, Path, Depends
from typing import Optional
from app.presentation.controllers.item_controller import ItemController
from app.domain.core.api_response import ItemResponse, SearchResponse, ItemsResponse
from app.domain.core.dependencies import get_item_controller

router = APIRouter(prefix="/api/v1", tags=["items"])


@router.get(
    "/health",
    summary="Verificar el estado del servicio",
    description="""
    **Health Check Endpoint**
    
    Este endpoint verifica que el servicio esté funcionando correctamente.
    Es útil para monitoreo y balanceadores de carga.
    
    **Respuesta:**
    - `200 OK`: Servicio funcionando normalmente
    """,
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
    summary="Obtener artículos populares",
    description="""
    **Obtener Detalle de Producto**
    
    Devuelve información completa de un producto específico incluyendo:
    - Información básica (título, precio, condición)
    - Imágenes del producto
    - Atributos y especificaciones técnicas
    - Información de envío
    - Datos del vendedor
    - Garantía y ruta de categoría
    
    **Parámetros:**
    - `item_id`: Identificador único del producto (formato: MLA + números)
    
    **Ejemplos de uso:**
    - `/api/v1/items/MLA123456789` - Obtener iPhone 15 Pro
    - `/api/v1/items/MLA777888999` - Obtener Samsung Galaxy A34
    """,
    responses={
        200: {
            "description": "Detalle del producto solicitado",
            "content": {
                "application/json": {
                    "example": {
                        "id": "MLA111222333",
                        "title": "iPhone 15 Pro 256GB Titanio Natural",
                        "category_id": "MLA1055",
                        "price": 2499999.0,
                        "currency_id": "ARS",
                        "available_quantity": 8,
                        "sold_quantity": 1200,
                        "condition": "new",
                        "permalink": "https://articulo.mercadolibre.com.ar/MLA-111222333",
                        "pictures": [
                            {
                                "id": "PIC-IPHONE15PRO-1",
                                "url": "http://example.com/images/iphone15pro-1.jpg",
                                "secure_url": "https://example.com/images/iphone15pro-1.jpg",
                                "size": "500x500",
                                "max_size": "1200x1200",
                                "quality": ""
                            }
                        ],
                        "shipping": {
                            "free_shipping": True,
                            "mode": "me2",
                            "logistic_type": "drop_off",
                            "store_pick_up": False
                        },
                        "attributes": [
                            {
                                "id": "BRAND",
                                "name": "Marca",
                                "value_id": "APPLE",
                                "value_name": "Apple",
                                "value_struct": None,
                                "attribute_group_id": "OTHERS",
                                "attribute_group_name": "Otros"
                            },
                            {
                                "id": "MODEL",
                                "name": "Modelo",
                                "value_id": "IPHONE15PRO",
                                "value_name": "iPhone 15 Pro",
                                "value_struct": None,
                                "attribute_group_id": "OTHERS",
                                "attribute_group_name": "Otros"
                            },
                            {
                                "id": "INTERNAL_MEMORY",
                                "name": "Memoria interna",
                                "value_id": None,
                                "value_name": "256 GB",
                                "value_struct": {"number": 256, "unit": "GB"},
                                "attribute_group_id": "OTHERS",
                                "attribute_group_name": "Otros"
                            },
                            {
                                "id": "COLOR",
                                "name": "Color",
                                "value_id": "TITANIUM",
                                "value_name": "Titanio Natural",
                                "value_struct": None,
                                "attribute_group_id": "MAIN",
                                "attribute_group_name": "Principal"
                            }
                        ],
                        "seller": {
                            "id": "SELLER009",
                            "nickname": "AppleStore"
                        },
                        "warranty": "12 meses oficial",
                        "category_path": ["Electrónica", "Celulares y Teléfonos", "Celulares y Smartphones"]
                    }
                }
            }
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
        },
        400: {
            "description": "Parámetros inválidos",
            "content": {
                "application/json": {
                    "example": {
                        "code": "VALIDATION_ERROR",
                        "message": "Invalid request data",
                        "status": 400,
                        "cause": ["Item ID cannot be empty"]
                    }
                }
            }
        },
        500: {
            "description": "Error interno del servidor",
            "content": {
                "application/json": {
                    "example": {
                        "code": "INTERNAL_ERROR",
                        "message": "An unexpected error occurred",
                        "status": 500,
                        "cause": ["Database connection error"]
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
    "/items",
    response_model=SearchResponse,
    summary="Buscar artículos",
    description="""
    **Búsqueda Avanzada de Productos**
    
    Permite buscar productos con múltiples criterios de filtrado y ordenamiento.
    Soporta búsqueda por texto, filtros por categoría, marca, precio y disponibilidad.
    
    **Funcionalidades:**
    - 🔍 Búsqueda por texto en título, marca y modelo
    - 🏷️ Filtrado por categoría y marca
    - 💰 Filtrado por rango de precios
    - 📦 Filtrado por disponibilidad
    - 📊 Ordenamiento por múltiples campos
    - 📄 Paginación automática
    
    **Ejemplos de uso:**
    - `/api/v1/items?q=iphone` - Buscar productos con "iphone"
    - `/api/v1/items?brand=Apple&min_price=100000` - Apple con precio mínimo
    - `/api/v1/items?category_id=MLA1055&sort=price:desc` - Celulares ordenados por precio
    - `/api/v1/items?available_only=true&limit=5` - Solo disponibles, máximo 5
    """,
    responses={
        200: {
            "description": "Lista de productos que coinciden con los criterios de búsqueda",
            "content": {
                "application/json": {
                    "example": {
                        "data": [
                            {
                                "id": "MLA111222333",
                                "title": "iPhone 15 Pro 256GB Titanio Natural",
                                "category_id": "MLA1055",
                                "price": 2499999.0,
                                "currency_id": "ARS",
                                "available_quantity": 8,
                                "sold_quantity": 1200,
                                "condition": "new",
                                "permalink": "https://articulo.mercadolibre.com.ar/MLA-111222333",
                                "pictures": [
                                    {
                                        "id": "PIC-IPHONE15PRO-1",
                                        "url": "http://example.com/images/iphone15pro-1.jpg",
                                        "secure_url": "https://example.com/images/iphone15pro-1.jpg",
                                        "size": "500x500",
                                        "max_size": "1200x1200",
                                        "quality": ""
                                    }
                                ],
                                "shipping": {
                                    "free_shipping": True,
                                    "mode": "me2",
                                    "logistic_type": "drop_off",
                                    "store_pick_up": False
                                },
                                "attributes": [
                                    {
                                        "id": "BRAND",
                                        "name": "Marca",
                                        "value_id": "APPLE",
                                        "value_name": "Apple",
                                        "value_struct": None,
                                        "attribute_group_id": "OTHERS",
                                        "attribute_group_name": "Otros"
                                    }
                                ],
                                "seller": {
                                    "id": "SELLER009",
                                    "nickname": "AppleStore"
                                },
                                "warranty": "12 meses oficial",
                                "category_path": ["Electrónica", "Celulares y Teléfonos", "Celulares y Smartphones"]
                            }
                        ],
                        "meta": {
                            "total": 1,
                            "limit": 10,
                            "offset": 0,
                            "has_more": False,
                            "current_page": 1,
                            "total_pages": 1
                        }
                    }
                }
            }
        },
        400: {
            "description": "Criterios de búsqueda inválidos",
            "content": {
                "application/json": {
                    "example": {
                        "code": "INVALID_SEARCH_CRITERIA",
                        "message": "Invalid search criteria: limit = -5",
                        "status": 400,
                        "cause": ["Field: limit", "Value: -5", "Reason: Must be positive"]
                    }
                }
            }
        },
        500: {
            "description": "Error interno del servidor",
            "content": {
                "application/json": {
                    "example": {
                        "code": "INTERNAL_ERROR",
                        "message": "Unexpected error occurred during search",
                        "status": 500,
                        "cause": ["Database connection error"]
                    }
                }
            }
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
    
    Args:
        q: Término de búsqueda en título, marca o modelo
        limit: Límite de resultados por página (1-100)
        offset: Desplazamiento para paginación
        sort_field: Campo de ordenamiento (ej: price, title)
        sort_direction: Dirección de ordenamiento (asc o desc)
        category_id: ID de categoría para filtrar
        brand: Marca específica para filtrar
        min_price: Precio mínimo en pesos argentinos
        max_price: Precio máximo en pesos argentinos
        available_only: Solo productos con stock disponible
        controller: Controlador de items inyectado
        
    Returns:
        SearchResponse: Resultado de la búsqueda con datos y metadatos de paginación
        
    Raises:
        400: Criterios de búsqueda inválidos
        500: Error interno del servidor
    """
    # Los parámetros sort_field y sort_direction ya están parseados
    
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
    "/items/{item_id}/recommendations",
    response_model=ItemsResponse,
    summary="Obtener recomendaciones de artículos",
    description="""
    **Sistema de Recomendaciones**
    
    Devuelve productos similares basados en el artículo especificado.
    El algoritmo considera:
    - 🏷️ Misma marca (puntuación alta)
    - 📂 Misma categoría principal
    - 💰 Rango de precio similar (±20%)
    - 📊 Popularidad (cantidad vendida)
    
    **Algoritmo de similitud:**
    1. **Marca igual**: +3 puntos
    2. **Categoría principal igual**: +2 puntos
    3. **Categoría ID igual**: +1 punto
    4. **Precio similar (±20%)**: +1 punto
    5. **Ordenamiento**: Por puntuación descendente, luego por popularidad
    
    **Ejemplos de uso:**
    - `/api/v1/items/MLA111222333/recommendations` - Recomendaciones para iPhone 15 Pro
    - `/api/v1/items/MLA111222333/recommendations?k=10` - 10 recomendaciones
    """,
    responses={
        200: {
            "description": "Lista de productos recomendados",
            "content": {
                "application/json": {
                    "example": {
                        "data": [
                            {
                                "id": "MLA444555666",
                                "title": "MacBook Air M2 13\" 256GB",
                                "category_id": "MLA1652",
                                "price": 1899999.0,
                                "currency_id": "ARS",
                                "available_quantity": 12,
                                "sold_quantity": 450,
                                "condition": "new",
                                "permalink": "https://articulo.mercadolibre.com.ar/MLA-444555666",
                                "pictures": [
                                    {
                                        "id": "PIC-MACBOOKAIR-M2-1",
                                        "url": "http://example.com/images/macbook-air-m2-1.jpg",
                                        "secure_url": "https://example.com/images/macbook-air-m2-1.jpg",
                                        "size": "500x500",
                                        "max_size": "1200x1200",
                                        "quality": ""
                                    }
                                ],
                                "shipping": {
                                    "free_shipping": True,
                                    "mode": "me2",
                                    "logistic_type": "drop_off",
                                    "store_pick_up": False
                                },
                                "attributes": [
                                    {
                                        "id": "BRAND",
                                        "name": "Marca",
                                        "value_id": "APPLE",
                                        "value_name": "Apple",
                                        "value_struct": None,
                                        "attribute_group_id": "OTHERS",
                                        "attribute_group_name": "Otros"
                                    }
                                ],
                                "seller": {
                                    "id": "SELLER009",
                                    "nickname": "AppleStore"
                                },
                                "warranty": "12 meses oficial",
                                "category_path": ["Computación", "Laptops", "Notebooks"]
                            }
                        ]
                    }
                }
            }
        },
        404: {
            "description": "El producto base no fue encontrado",
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
        },
        500: {
            "description": "Error interno del servidor",
            "content": {
                "application/json": {
                    "example": {
                        "code": "INTERNAL_ERROR",
                        "message": "Unexpected error occurred while getting recommendations",
                        "status": 500,
                        "cause": ["Recommendation algorithm error"]
                    }
                }
            }
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


@router.get(
    "/items/popular",
    response_model=ItemsResponse,
    summary="Obtener artículos populares",
    description="""
    **Productos Más Populares**
    
    Devuelve los productos más populares basados en cantidad vendida.
    Útil para mostrar productos destacados en la página principal.
    
    **Criterio de ordenamiento:**
    - 📊 Cantidad vendida (descendente)
    - 🏷️ Mantiene productos con stock disponible
    
    **Casos de uso:**
    - Página principal del sitio
    - Sección "Más Vendidos"
    - Productos destacados
    - Análisis de tendencias
    
    **Ejemplos de uso:**
    - `/api/v1/items/popular` - Top 10 productos más vendidos
    - `/api/v1/items/popular?limit=5` - Top 5 productos más vendidos
    """,
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
                                "condition": "new",
                                "permalink": "https://articulo.mercadolibre.com.ar/MLA-777888999",
                                "pictures": [
                                    {
                                        "id": "PIC-SAM-A34-1",
                                        "url": "http://example.com/images/galaxy-a34-1.jpg",
                                        "secure_url": "https://example.com/images/galaxy-a34-1.jpg",
                                        "size": "500x500",
                                        "max_size": "1200x1200",
                                        "quality": ""
                                    }
                                ],
                                "shipping": {
                                    "free_shipping": True,
                                    "mode": "me2",
                                    "logistic_type": "drop_off",
                                    "store_pick_up": False
                                },
                                "attributes": [
                                    {
                                        "id": "BRAND",
                                        "name": "Marca",
                                        "value_id": "206",
                                        "value_name": "Samsung",
                                        "value_struct": None,
                                        "attribute_group_id": "OTHERS",
                                        "attribute_group_name": "Otros"
                                    }
                                ],
                                "seller": {
                                    "id": "SELLER004",
                                    "nickname": "MobileHouse"
                                },
                                "warranty": "12 meses oficial",
                                "category_path": ["Electrónica", "Celulares y Teléfonos", "Celulares y Smartphones"]
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "description": "Error interno del servidor",
            "content": {
                "application/json": {
                    "example": {
                        "code": "INTERNAL_ERROR",
                        "message": "Unexpected error occurred while getting popular items",
                        "status": 500,
                        "cause": ["Database query error"]
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
    summary="Obtener artículos disponibles",
    description="""
    **Productos Disponibles**
    
    Devuelve productos que están disponibles para compra (stock > 0).
    Útil para filtrar productos que se pueden comprar inmediatamente.
    
    **Criterios de filtrado:**
    - 📦 `available_quantity > 0`
    - 🏷️ Ordenados por cantidad disponible (descendente)
    - ⚡ Respuesta rápida para listados
    
    **Casos de uso:**
    - Filtro "Solo Disponibles"
    - Listado de productos en stock
    - Verificación de disponibilidad
    - Inventario activo
    
    **Ejemplos de uso:**
    - `/api/v1/items/available` - Todos los productos disponibles
    - `/api/v1/items/available?limit=20` - 20 productos disponibles
    """,
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
                                "condition": "new",
                                "permalink": "https://articulo.mercadolibre.com.ar/MLA-443322110",
                                "pictures": [
                                    {
                                        "id": "PIC-LOGI-MX3S-1",
                                        "url": "http://example.com/images/mx-master-3s-1.jpg",
                                        "secure_url": "https://example.com/images/mx-master-3s-1.jpg",
                                        "size": "500x500",
                                        "max_size": "1200x1200",
                                        "quality": ""
                                    }
                                ],
                                "shipping": {
                                    "free_shipping": False,
                                    "mode": "me2",
                                    "logistic_type": "drop_off",
                                    "store_pick_up": True
                                },
                                "attributes": [
                                    {
                                        "id": "BRAND",
                                        "name": "Marca",
                                        "value_id": "LOGITECH",
                                        "value_name": "Logitech",
                                        "value_struct": None,
                                        "attribute_group_id": "OTHERS",
                                        "attribute_group_name": "Otros"
                                    }
                                ],
                                "seller": {
                                    "id": "SELLER007",
                                    "nickname": "PerifericosYA"
                                },
                                "warranty": "24 meses",
                                "category_path": ["Computación", "Periféricos", "Mouses"]
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "description": "Error interno del servidor",
            "content": {
                "application/json": {
                    "example": {
                        "code": "INTERNAL_ERROR",
                        "message": "Unexpected error occurred while getting available items",
                        "status": 500,
                        "cause": ["Database connection error"]
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
