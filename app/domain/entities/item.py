from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    """Objeto de valor para representar dinero."""
    amount: Decimal
    currency: str
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
        if not self.currency:
            raise ValueError("Currency cannot be empty")


@dataclass(frozen=True)
class Picture:
    """Objeto de valor para imágenes."""
    id: str
    url: str
    secure_url: Optional[str] = None
    size: Optional[str] = None
    max_size: Optional[str] = None
    quality: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la imagen a diccionario para serialización."""
        return {
            "id": self.id,
            "url": self.url,
            "secure_url": self.secure_url,
            "size": self.size,
            "max_size": self.max_size,
            "quality": self.quality
        }


@dataclass(frozen=True)
class Attribute:
    """Objeto de valor para atributos del producto."""
    id: str
    name: str
    value_name: Optional[str] = None
    value_id: Optional[str] = None
    attribute_group_id: Optional[str] = None
    attribute_group_name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el atributo a diccionario para serialización."""
        return {
            "id": self.id,
            "name": self.name,
            "value_name": self.value_name,
            "value_id": self.value_id,
            "attribute_group_id": self.attribute_group_id,
            "attribute_group_name": self.attribute_group_name
        }


@dataclass(frozen=True)
class Shipping:
    """Objeto de valor para información de envío."""
    free_shipping: bool
    mode: str
    logistic_type: str
    store_pick_up: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el shipping a diccionario para serialización."""
        return {
            "free_shipping": self.free_shipping,
            "mode": self.mode,
            "logistic_type": self.logistic_type,
            "store_pick_up": self.store_pick_up
        }


@dataclass(frozen=True)
class Seller:
    """Objeto de valor para información del vendedor."""
    id: str
    nickname: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el seller a diccionario para serialización."""
        return {
            "id": self.id,
            "nickname": self.nickname
        }


@dataclass
class Item:
    """
    Entidad principal que representa un producto.
    Inmutable y con validaciones de dominio.
    """
    id: str
    title: str
    category_id: str
    price: Money
    available_quantity: int
    sold_quantity: int
    condition: str
    permalink: str
    pictures: List[Picture]
    attributes: List[Attribute]
    shipping: Optional[Shipping] = None
    seller: Optional[Seller] = None
    warranty: Optional[str] = None
    category_path: List[str] = None
    
    def __post_init__(self):
        """Validaciones de dominio."""
        if not self.id:
            raise ValueError("Item ID cannot be empty")
        if not self.title:
            raise ValueError("Item title cannot be empty")
        if self.available_quantity < 0:
            raise ValueError("Available quantity cannot be negative")
        if self.sold_quantity < 0:
            raise ValueError("Sold quantity cannot be negative")
        if not self.permalink:
            raise ValueError("Permalink cannot be empty")
        
        # Hacer inmutables las listas
        object.__setattr__(self, 'pictures', tuple(self.pictures))
        object.__setattr__(self, 'attributes', tuple(self.attributes))
        if self.category_path:
            object.__setattr__(self, 'category_path', tuple(self.category_path))
    
    @property
    def is_available(self) -> bool:
        """Verifica si el item está disponible para compra."""
        return self.available_quantity > 0
    
    @property
    def total_quantity(self) -> int:
        """Cantidad total (disponible + vendida)."""
        return self.available_quantity + self.sold_quantity
    
    def get_attribute_by_id(self, attribute_id: str) -> Optional[Attribute]:
        """Obtiene un atributo por su ID."""
        for attr in self.attributes:
            if attr.id == attribute_id:
                return attr
        return None
    
    def get_attribute_by_name(self, name: str) -> Optional[Attribute]:
        """Obtiene un atributo por su nombre."""
        for attr in self.attributes:
            if attr.name.lower() == name.lower():
                return attr
        return None
    
    def has_brand(self) -> bool:
        """Verifica si el item tiene marca definida."""
        return self.get_attribute_by_id("BRAND") is not None
    
    def get_brand(self) -> Optional[str]:
        """Obtiene la marca del item."""
        brand_attr = self.get_attribute_by_id("BRAND")
        return brand_attr.value_name if brand_attr else None
    
    def get_model(self) -> Optional[str]:
        """Obtiene el modelo del item."""
        model_attr = self.get_attribute_by_id("MODEL")
        return model_attr.value_name if model_attr else None
    
    def get_main_category(self) -> Optional[str]:
        """Obtiene la categoría principal."""
        return self.category_path[0] if self.category_path and len(self.category_path) > 0 else None
    
    def matches_search_term(self, search_term: str) -> bool:
        """Verifica si el item coincide con un término de búsqueda.
        
        Esta es lógica de dominio que encapsula las reglas de negocio
        para determinar si un item es relevante para una búsqueda.
        """
        if not search_term:
            return True
        
        term = search_term.lower()
        return (
            term in self.title.lower() or
            (self.get_brand() and term in self.get_brand().lower()) or
            (self.get_model() and term in self.get_model().lower())
        )
    
    def is_in_price_range(self, min_price: Optional[float], max_price: Optional[float]) -> bool:
        """Verifica si el item está en el rango de precios especificado.
        
        Lógica de dominio para filtrado por precio.
        """
        item_price = float(self.price.amount)
        
        if min_price is not None and item_price < min_price:
            return False
        
        if max_price is not None and item_price > max_price:
            return False
        
        return True
    
    def calculate_similarity_with(self, other: 'Item') -> float:
        """Calcula la similitud con otro item para recomendaciones.
        
        Implementa la lógica de dominio para el sistema de recomendaciones.
        """
        if not isinstance(other, Item):
            return 0.0
        
        score = 0.0
        
        # Misma marca: +3 puntos
        if self.get_brand() and other.get_brand() and self.get_brand() == other.get_brand():
            score += 3.0
        
        # Misma categoría principal: +2 puntos
        if self.get_main_category() and other.get_main_category() and self.get_main_category() == other.get_main_category():
            score += 2.0
        
        # Misma categoría ID: +1 punto
        if self.category_id == other.category_id:
            score += 1.0
        
        # Precio similar (±20%): +1 punto
        self_price = float(self.price.amount)
        other_price = float(other.price.amount)
        price_diff = abs(self_price - other_price) / max(self_price, other_price)
        if price_diff <= 0.2:
            score += 1.0
        
        return score
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la entidad Item a diccionario para serialización.
        
        Método de infraestructura para serialización, no contiene lógica de dominio.
        """
        return {
            "id": self.id,
            "title": self.title,
            "category_id": self.category_id,
            "price": float(self.price.amount),
            "currency_id": self.price.currency,
            "available_quantity": self.available_quantity,
            "sold_quantity": self.sold_quantity,
            "condition": self.condition,
            "permalink": self.permalink,
            "pictures": [pic.to_dict() for pic in self.pictures],
            "attributes": [attr.to_dict() for attr in self.attributes],
            "shipping": self.shipping.to_dict() if self.shipping else None,
            "seller": self.seller.to_dict() if self.seller else None,
            "warranty": self.warranty,
            "category_path": list(self.category_path) if self.category_path else []
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Item':
        """Crea una entidad Item desde un diccionario validado.
        
        Factory method para crear entidades desde datos externos.
        Incluye validaciones de dominio durante la construcción.
        """
        # Convertir price a Money
        price = Money(
            amount=Decimal(str(data["price"])),
            currency=data.get("currency_id", "ARS")
        )
        
        # Convertir pictures
        pictures = []
        for pic_data in data.get("pictures", []):
            pictures.append(Picture(
                id=pic_data["id"],
                url=pic_data["url"],
                secure_url=pic_data.get("secure_url"),
                size=pic_data.get("size"),
                max_size=pic_data.get("max_size"),
                quality=pic_data.get("quality")
            ))
        
        # Convertir attributes
        attributes = []
        for attr_data in data.get("attributes", []):
            attributes.append(Attribute(
                id=attr_data["id"],
                name=attr_data["name"],
                value_name=attr_data.get("value_name"),
                value_id=attr_data.get("value_id"),
                attribute_group_id=attr_data.get("attribute_group_id"),
                attribute_group_name=attr_data.get("attribute_group_name")
            ))
        
        # Convertir shipping (opcional)
        shipping = None
        if data.get("shipping"):
            shipping_data = data["shipping"]
            shipping = Shipping(
                free_shipping=shipping_data["free_shipping"],
                mode=shipping_data["mode"],
                logistic_type=shipping_data["logistic_type"],
                store_pick_up=shipping_data["store_pick_up"]
            )
        
        # Convertir seller (opcional)
        seller = None
        if data.get("seller"):
            seller_data = data["seller"]
            seller = Seller(
                id=seller_data["id"],
                nickname=seller_data.get("nickname")
            )
        
        return cls(
            id=data["id"],
            title=data["title"],
            category_id=data["category_id"],
            price=price,
            available_quantity=data["available_quantity"],
            sold_quantity=data["sold_quantity"],
            condition=data["condition"],
            permalink=data["permalink"],
            pictures=pictures,
            attributes=attributes,
            shipping=shipping,
            seller=seller,
            warranty=data.get("warranty"),
            category_path=data.get("category_path", [])
        )
