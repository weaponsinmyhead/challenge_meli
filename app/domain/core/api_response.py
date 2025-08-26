from pydantic import BaseModel, Field
from typing import Optional, List, Any, Generic, TypeVar, Literal
from app.domain.entities.item import Item

T = TypeVar("T")
     
class ApiResponse(BaseModel):
    code: Optional[str] = Field(None, description="Código de resultado o error. En caso de error, corresponde al tipo de error (ej: 'not_found').")
    message: Optional[str] = Field(None, description="Mensaje explicativo de la respuesta o del error.")
    status: int = Field(..., description="Código HTTP de la respuesta.")
    cause: Optional[Any] = Field(None, description="Causa del error (puede ser una lista de detalles adicionales).")

class SuccessResponse(ApiResponse, Generic[T]):
    """Respuesta satisfactoria con los datos de un producto."""
    code: Literal["OK"] = Field("OK", description="Código de resultado en caso exitoso (OK).", example="OK")
    status: int = Field(200, description="Código HTTP 200 indicando éxito.")
    data: T = Field(..., description="Datos de respuesta.")

class ErrorResponse(ApiResponse):
    """Respuesta de error con detalles del problema."""
    code: str = Field(..., description="Código de error ocurrido (por ejemplo, not_found, bad_request).", example="not_found")
    message: str = Field(..., description="Mensaje descriptivo del error.", example="Item with id MLA123456789 not found")
    status: int = Field(..., description="Código HTTP correspondiente al error.", example=404)
    cause: Optional[List[Any]] = Field([], description="Lista de causas adicionales del error, si aplican.", example=[])

# Nuevos tipos para respuestas directas (sin capa 'data')
class DirectSuccessResponse(BaseModel):
    """Respuesta satisfactoria que devuelve directamente los datos sin capa 'data'."""
    pass

class ItemResponse(DirectSuccessResponse):
    """Respuesta directa para un item individual."""
    id: str = Field(..., description="Identificador único del producto")
    title: str = Field(..., description="Título del producto")
    category_id: str = Field(..., description="ID de la categoría")
    price: float = Field(..., description="Precio del producto")
    currency_id: str = Field(..., description="Moneda del precio")
    available_quantity: int = Field(..., description="Cantidad disponible")
    sold_quantity: int = Field(..., description="Cantidad vendida")
    condition: str = Field(..., description="Condición del producto")
    permalink: str = Field(..., description="Enlace permanente del producto")
    pictures: List[dict] = Field(..., description="Lista de imágenes del producto")
    shipping: Optional[dict] = Field(None, description="Información de envío")
    attributes: List[dict] = Field(..., description="Atributos del producto")
    seller: Optional[dict] = Field(None, description="Información del vendedor")
    warranty: Optional[str] = Field(None, description="Información de garantía")
    category_path: Optional[List[str]] = Field(None, description="Ruta de categorías")

class SearchResponse(DirectSuccessResponse):
    """Respuesta directa para búsqueda de items."""
    data: List[dict] = Field(..., description="Lista de productos encontrados")
    meta: dict = Field(..., description="Metadatos de la búsqueda (paginación, total, etc.)")

class ItemsResponse(DirectSuccessResponse):
    """Respuesta directa para listas de items."""
    data: List[dict] = Field(..., description="Lista de productos")
