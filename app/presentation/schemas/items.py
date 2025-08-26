from pydantic import BaseModel, Field
from typing import List, Optional


class Seller(BaseModel):
    id: str = Field(..., description="Identificador del vendedor.", example="SELLER001")
    nickname: Optional[str] = Field(
        None, description="Alias público del vendedor.", example="TechStore"
    )


class Shipping(BaseModel):
    free_shipping: bool = Field(
        ..., description="Indica si el envío es gratuito.", example=True
    )
    mode: str = Field(
        ..., description="Modo de envío (p. ej., 'me2' para Mercado Envíos).", example="me2"
    )
    logistic_type: str = Field(
        ..., description="Tipo de logística (p. ej., 'drop_off', 'cross_docking').", example="drop_off"
    )
    store_pick_up: bool = Field(
        ..., description="Indica si permite retiro en tienda.", example=False
    )


class Picture(BaseModel):
    id: str = Field(..., description="ID de la imagen.", example="624029-MLA31151332127_062019")
    url: str = Field(..., description="URL de la imagen.", example="http://http2.mlstatic.com/D_...-O.jpg")
    secure_url: Optional[str] = Field(
        None, description="URL segura (https) de la imagen.", example="https://http2.mlstatic.com/D_...-O.jpg"
    )
    size: Optional[str] = Field(None, description="Tamaño (p. ej., '500x500').", example="500x500")
    max_size: Optional[str] = Field(None, description="Tamaño máximo disponible.", example="1200x1200")
    quality: Optional[str] = Field(None, description="Calidad de la imagen.", example="")


class Attribute(BaseModel):
    id: str = Field(..., description="ID del atributo.", example="BRAND")
    name: str = Field(..., description="Nombre del atributo.", example="Marca")
    value_id: Optional[str] = Field(None, description="ID del valor (si es predefinido).", example="9344")
    value_name: Optional[str] = Field(None, description="Valor legible del atributo.", example="Apple")
    value_struct: Optional[dict] = Field(
        None, description="Valor estructurado (p. ej., unidades).", example=None
    )
    attribute_group_id: Optional[str] = Field(
        None, description="ID del grupo de atributos.", example="OTHERS"
    )
    attribute_group_name: Optional[str] = Field(
        None, description="Nombre del grupo de atributos.", example="Otros"
    )


class Item(BaseModel):
    # Identidad / básicos
    id: str = Field(
        ..., description="Identificador único del producto (item ID).", example="MLA123456789"
    )
    title: str = Field(..., description="Título o nombre del producto.", example="Apple iPhone 11 64GB Black")
    category_id: str = Field(..., description="ID de la categoría del producto.", example="MLA1055")

    # Precio / stock
    price: float = Field(
        ..., ge=0, description="Precio del producto.", example=69999.99
    )
    currency_id: str = Field(
        ..., description="Moneda del precio (ISO).", example="ARS"
    )
    available_quantity: int = Field(
        ..., ge=0, description="Cantidad disponible en stock.", example=10
    )
    sold_quantity: int = Field(
        ..., ge=0, description="Cantidad vendida.", example=5
    )

    # Estado / enlaces
    condition: str = Field(
        ..., description="Condición (new, used, etc.).", example="new"
    )
    permalink: str = Field(
        ..., description="URL pública del producto.", example="https://articulo.mercadolibre.com.ar/MLA-123456789"
    )

    # Media
    pictures: List[Picture] = Field(
        default_factory=list, description="Lista de imágenes del producto."
    )

    # Envío / atributos
    shipping: Optional[Shipping] = Field(
        None, description="Información de envío (si aplica)."
    )
    attributes: List[Attribute] = Field(
        default_factory=list, description="Atributos del producto (marca, modelo, color, etc.)."
    )

    # Vendedor / garantías / taxonomía extendida
    seller: Optional[Seller] = Field(
        None, description="Información del vendedor."
    )
    warranty: Optional[str] = Field(
        None, description="Información de garantía.", example="12 meses"
    )
    category_path: List[str] = Field(
        default_factory=list, description="Ruta de categorías (breadcrumbs).", example=["Electrónica", "Audio", "Auriculares"]
    )


class PageMeta(BaseModel):
    total: int = Field(..., ge=0, description="Total de resultados.", example=123)
    limit: int = Field(..., ge=1, description="Límite por página.", example=10)
    offset: int = Field(..., ge=0, description="Desplazamiento (inicio).", example=0)


class ItemListResponse(BaseModel):
    data: List[Item] = Field(..., description="Listado de productos.")
    meta: PageMeta = Field(..., description="Metadatos de paginación.")
    