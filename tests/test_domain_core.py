"""
Tests unitarios para entidades y lógica de dominio.
"""

import pytest
from decimal import Decimal
from app.domain.entities.item import Item, Money
from app.domain.core.exceptions import ItemNotFoundError


@pytest.fixture
def sample_item():
    """Fixture que crea un item de ejemplo para tests."""
    return Item(
        id="MLA111222333",
        title="iPhone 15 Pro Max 256GB",
        category_id="MLA1055",
        price=Money(amount=Decimal("500000.00"), currency="ARS"),
        available_quantity=10,
        sold_quantity=50,
        condition="new",
        permalink="https://test.com/item",
        pictures=[],
        attributes=[]
    )


class TestItemEntity:
    """Tests unitarios para la entidad Item."""
    
    def test_item_availability_logic(self, sample_item):
        """Test lógica de disponibilidad - crítico para compras."""
        # Item con stock disponible
        assert sample_item.is_available is True
        assert sample_item.available_quantity > 0
        
        # Item sin stock
        sample_item.available_quantity = 0
        assert sample_item.is_available is False
    
    def test_item_price_validation(self):
        """Test validación de precio - crítico para transacciones."""
        # Precio válido
        valid_price = Money(amount=Decimal("100.00"), currency="ARS")
        assert valid_price.amount == Decimal("100.00")
        
        # Precio negativo debe fallar
        with pytest.raises(ValueError):
            Money(amount=Decimal("-100.00"), currency="ARS")
    
    def test_item_serialization(self, sample_item):
        """Test serialización de item - crítico para API responses."""
        item_dict = sample_item.to_dict()
        
        # Verificar campos obligatorios
        assert item_dict["id"] == "MLA111222333"
        assert item_dict["title"] == "iPhone 15 Pro Max 256GB"
        assert item_dict["price"] == 500000.0
        assert item_dict["currency_id"] == "ARS"
        assert item_dict["available_quantity"] == 10
        assert item_dict["sold_quantity"] == 50
        assert item_dict["condition"] == "new"
    
    def test_item_similarity_calculation(self, sample_item):
        """Test algoritmo de similitud - crítico para recomendaciones."""
        # Item similar (misma categoría y marca)
        similar_item = Item(
            id="MLA444555666",
            title="iPhone 14 Pro 128GB",
            category_id="MLA1055",  # Misma categoría
            price=Money(amount=Decimal("400000.00"), currency="ARS"),
            available_quantity=5,
            sold_quantity=30,
            condition="new",
            permalink="https://test.com/similar",
            pictures=[],
            attributes=[]
        )
        
        # Calcular similitud
        similarity = sample_item.calculate_similarity_with(similar_item)
        assert similarity > 0  # Debe tener similitud por categoría
        
        # Item completamente diferente
        different_item = Item(
            id="MLA777888999",
            title="Auriculares Sony",
            category_id="MLA3697",  # Categoría diferente
            price=Money(amount=Decimal("50000.00"), currency="ARS"),
            available_quantity=15,
            sold_quantity=100,
            condition="new",
            permalink="https://test.com/different",
            pictures=[],
            attributes=[]
        )
        
        different_similarity = sample_item.calculate_similarity_with(different_item)
        assert similarity > different_similarity  # Similar debe tener mayor puntuación


class TestDomainExceptions:
    """Tests unitarios para excepciones de dominio."""
    
    def test_item_not_found_exception(self):
        """Test excepción ItemNotFoundError - crítico para manejo de errores."""
        item_id = "MLA999999999"
        exception = ItemNotFoundError(item_id)
        
        # Verificar atributos de la excepción
        assert exception.item_id == item_id
        assert exception.status_code == 404
        assert exception.code == "ITEM_NOT_FOUND"
        assert "not found" in str(exception)
        assert item_id in str(exception)
