from typing import Dict, List, Any, Optional
from decimal import Decimal
from app.domain.entities.item import Item, Money, Picture, Attribute, Shipping, Seller
from app.domain.core.exceptions import SerializationError


class ItemSerializer:
    """
    Serializador especializado para entidades Item.
    Maneja la conversión entre entidades del dominio y representaciones de datos.
    """
    
    @staticmethod
    def to_dict(item: Item) -> Dict[str, Any]:
        """
        Convierte una entidad Item a diccionario.
        
        Args:
            item: Entidad Item a serializar
            
        Returns:
            Diccionario con los datos del item
        """
        try:
            return {
                "id": item.id,
                "title": item.title,
                "category_id": item.category_id,
                "price": float(item.price.amount),
                "currency_id": item.price.currency,
                "available_quantity": item.available_quantity,
                "sold_quantity": item.sold_quantity,
                "condition": item.condition,
                "permalink": item.permalink,
                "pictures": [ItemSerializer._convert_picture_to_dict(pic) for pic in item.pictures],
                "attributes": [ItemSerializer._convert_attribute_to_dict(attr) for attr in item.attributes],
                "shipping": ItemSerializer._convert_shipping_to_dict(item.shipping) if item.shipping else None,
                "seller": ItemSerializer._convert_seller_to_dict(item.seller) if item.seller else None,
                "warranty": item.warranty,
                "category_path": list(item.category_path) if item.category_path else []
            }
        except Exception as e:
            raise SerializationError("Item", f"Error serializing item: {str(e)}")
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Item:
        """
        Convierte un diccionario a entidad Item.
        
        Args:
            data: Diccionario con los datos del item
            
        Returns:
            Entidad Item creada
            
        Raises:
            SerializationError: Si hay error en la deserialización
        """
        try:
            # Validar campos requeridos
            required_fields = ["id", "title", "category_id", "price", "currency_id"]
            for field in required_fields:
                if field not in data:
                    raise SerializationError("Item", f"Missing required field: {field}")
            
            # Crear objeto Money
            price = Money(
                amount=Decimal(str(data["price"])),
                currency=data["currency_id"]
            )
            
            # Crear listas de objetos de valor
            pictures = [
                ItemSerializer._convert_picture_from_dict(pic_data) 
                for pic_data in data.get("pictures", [])
            ]
            
            attributes = [
                ItemSerializer._convert_attribute_from_dict(attr_data) 
                for attr_data in data.get("attributes", [])
            ]
            
            # Crear objetos opcionales
            shipping = None
            if data.get("shipping"):
                shipping = ItemSerializer._convert_shipping_from_dict(data["shipping"])
            
            seller = None
            if data.get("seller"):
                seller = ItemSerializer._convert_seller_from_dict(data["seller"])
            
            return Item(
                id=str(data["id"]),
                title=str(data["title"]),
                category_id=str(data["category_id"]),
                price=price,
                available_quantity=int(data.get("available_quantity", 0)),
                sold_quantity=int(data.get("sold_quantity", 0)),
                condition=str(data.get("condition", "new")),
                permalink=str(data.get("permalink", "")),
                pictures=pictures,
                attributes=attributes,
                shipping=shipping,
                seller=seller,
                warranty=data.get("warranty"),
                category_path=data.get("category_path", [])
            )
        except Exception as e:
            raise SerializationError("Item", f"Error deserializing item: {str(e)}")
    
    @staticmethod
    def _convert_picture_to_dict(picture: Picture) -> Dict[str, Any]:
        """Convierte Picture a diccionario."""
        return {
            "id": picture.id,
            "url": picture.url,
            "secure_url": picture.secure_url,
            "size": picture.size,
            "max_size": picture.max_size,
            "quality": picture.quality
        }
    
    @staticmethod
    def _convert_picture_from_dict(data: Dict[str, Any]) -> Picture:
        """Convierte diccionario a Picture."""
        return Picture(
            id=str(data.get("id", "")),
            url=str(data.get("url", "")),
            secure_url=data.get("secure_url"),
            size=data.get("size"),
            max_size=data.get("max_size"),
            quality=data.get("quality")
        )
    
    @staticmethod
    def _convert_attribute_to_dict(attribute: Attribute) -> Dict[str, Any]:
        """Convierte Attribute a diccionario."""
        return {
            "id": attribute.id,
            "name": attribute.name,
            "value_id": attribute.value_id,
            "value_name": attribute.value_name,
            "attribute_group_id": attribute.attribute_group_id,
            "attribute_group_name": attribute.attribute_group_name
        }
    
    @staticmethod
    def _convert_attribute_from_dict(data: Dict[str, Any]) -> Attribute:
        """Convierte diccionario a Attribute."""
        return Attribute(
            id=str(data.get("id", "")),
            name=str(data.get("name", "")),
            value_id=data.get("value_id"),
            value_name=data.get("value_name"),
            attribute_group_id=data.get("attribute_group_id"),
            attribute_group_name=data.get("attribute_group_name")
        )
    
    @staticmethod
    def _convert_shipping_to_dict(shipping: Shipping) -> Dict[str, Any]:
        """Convierte Shipping a diccionario."""
        return {
            "free_shipping": shipping.free_shipping,
            "mode": shipping.mode,
            "logistic_type": shipping.logistic_type,
            "store_pick_up": shipping.store_pick_up
        }
    
    @staticmethod
    def _convert_shipping_from_dict(data: Dict[str, Any]) -> Shipping:
        """Convierte diccionario a Shipping."""
        return Shipping(
            free_shipping=bool(data.get("free_shipping", False)),
            mode=str(data.get("mode", "me2")),
            logistic_type=str(data.get("logistic_type", "drop_off")),
            store_pick_up=bool(data.get("store_pick_up", False))
        )
    
    @staticmethod
    def _convert_seller_to_dict(seller: Seller) -> Dict[str, Any]:
        """Convierte Seller a diccionario."""
        return {
            "id": seller.id,
            "nickname": seller.nickname
        }
    
    @staticmethod
    def _convert_seller_from_dict(data: Dict[str, Any]) -> Seller:
        """Convierte diccionario a Seller."""
        return Seller(
            id=str(data.get("id", "")),
            nickname=data.get("nickname")
        )
    
    @staticmethod
    def validate_data(data: Dict[str, Any]) -> bool:
        """
        Valida que un diccionario tenga la estructura correcta para un Item.
        
        Args:
            data: Diccionario a validar
            
        Returns:
            True si es válido
            
        Raises:
            SerializationError: Si los datos son inválidos
        """
        try:
            # Verificar campos requeridos
            required_fields = ["id", "title", "category_id", "price"]
            for field in required_fields:
                if field not in data:
                    raise SerializationError("Item", f"Missing required field: {field}")
            
            # Validar tipos básicos
            if not isinstance(data["id"], str):
                raise SerializationError("Item", "ID must be a string")
            
            if not isinstance(data["title"], str):
                raise SerializationError("Item", "Title must be a string")
            
            if not isinstance(data["price"], (int, float, str)):
                raise SerializationError("Item", "Price must be a number")
            
            # Validar listas si existen
            if "pictures" in data and not isinstance(data["pictures"], list):
                raise SerializationError("Item", "Pictures must be a list")
            
            if "attributes" in data and not isinstance(data["attributes"], list):
                raise SerializationError("Item", "Attributes must be a list")
            
            return True
        except Exception as e:
            if isinstance(e, SerializationError):
                raise
            raise SerializationError("Item", f"Validation error: {str(e)}")
