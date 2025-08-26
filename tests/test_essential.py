"""
Tests esenciales - Solo los más importantes para el proyecto
Mantiene únicamente tests críticos que deben pasar siempre.
"""

import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from unittest.mock import Mock

from app.domain.entities.item import Item, Money
from app.domain.core.exceptions import ItemNotFoundError
from app.domain.services.item_service import ItemService
from app.infrastructure.repositories.json_item_repository import JsonItemRepository
from app.main import app


class TestDomainCore:
    """Tests críticos para entidades de dominio."""
    
    def test_money_validation(self):
        """Test validación de dinero - crítico para transacciones."""
        # Precio válido
        valid_price = Money(amount=Decimal("100.00"), currency="ARS")
        assert valid_price.amount == Decimal("100.00")
        assert valid_price.currency == "ARS"
        
        # Precio negativo debe fallar
        with pytest.raises(ValueError):
            Money(amount=Decimal("-100.00"), currency="ARS")
    
    def test_item_availability(self):
        """Test lógica de disponibilidad - crítico para compras."""
        item = Item(
            id="MLA111222333",
            title="Test Item",
            category_id="MLA1055",
            price=Money(amount=Decimal("100000.00"), currency="ARS"),
            available_quantity=10,
            sold_quantity=5,
            condition="new",
            permalink="https://test.com",
            pictures=[],
            attributes=[]
        )
        
        # Con stock
        assert item.is_available is True
        assert item.available_quantity == 10
        
        # Sin stock
        item.available_quantity = 0
        assert item.is_available is False
    
    def test_item_serialization(self):
        """Test serialización - crítico para API."""
        item = Item(
            id="MLA111222333",
            title="iPhone 15 Pro",
            category_id="MLA1055",
            price=Money(amount=Decimal("500000.00"), currency="ARS"),
            available_quantity=10,
            sold_quantity=50,
            condition="new",
            permalink="https://test.com",
            pictures=[],
            attributes=[]
        )
        
        item_dict = item.to_dict()
        assert item_dict["id"] == "MLA111222333"
        assert item_dict["title"] == "iPhone 15 Pro"
        assert item_dict["price"] == 500000.0
        assert item_dict["currency_id"] == "ARS"
        assert item_dict["available_quantity"] == 10
    
    def test_item_not_found_exception(self):
        """Test excepción crítica para manejo de errores."""
        exc = ItemNotFoundError("MLA999999999")
        assert exc.item_id == "MLA999999999"
        assert exc.status_code == 404
        assert "not found" in str(exc)


class TestServices:
    """Tests críticos para servicios."""
    
    def test_item_service_get_by_id(self):
        """Test servicio básico - operación crítica."""
        mock_repo = Mock()
        test_item = Item(
            id="MLA111222333",
            title="Test Item",
            category_id="MLA1055",
            price=Money(amount=Decimal("100000.00"), currency="ARS"),
            available_quantity=10,
            sold_quantity=5,
            condition="new",
            permalink="https://test.com",
            pictures=[],
            attributes=[]
        )
        mock_repo.find_by_id.return_value = test_item
        
        service = ItemService(mock_repo)
        result = service.get_item_by_id("MLA111222333")
        
        assert result == test_item
        assert result.id == "MLA111222333"
        mock_repo.find_by_id.assert_called_once_with("MLA111222333")
    
    def test_item_service_not_found(self):
        """Test manejo de errores - crítico para UX."""
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = None
        
        service = ItemService(mock_repo)
        
        with pytest.raises(ItemNotFoundError) as exc_info:
            service.get_item_by_id("MLA999999999")
        
        assert exc_info.value.item_id == "MLA999999999"


class TestRepository:
    """Tests críticos para repositorio."""
    
    def test_repository_basic_operations(self):
        """Test operaciones básicas - crítico para datos."""
        repo = JsonItemRepository()
        
        # Debe inicializar correctamente
        assert repo is not None
        
        # Debe cargar items
        items = repo.find_all()
        assert isinstance(items, list)
        
        # Cada item debe ser válido
        for item in items[:3]:  # Solo primeros 3 para eficiencia
            assert isinstance(item, Item)
            assert item.id is not None
            assert item.title is not None
            assert item.price.amount >= 0
    
    def test_repository_find_by_id(self):
        """Test búsqueda por ID - operación crítica."""
        repo = JsonItemRepository()
        items = repo.find_all()
        
        if items:
            # Test con item existente
            first_item = items[0]
            found_item = repo.find_by_id(first_item.id)
            assert found_item is not None
            assert found_item.id == first_item.id
        
        # Test con item inexistente
        not_found = repo.find_by_id("MLA999999999")
        assert not_found is None


class TestAPIIntegration:
    """Tests críticos para API."""
    
    @pytest.fixture
    def client(self):
        """Cliente de test para API."""
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        """Test health check - crítico para monitoreo."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
    
    def test_search_endpoint_basic(self, client):
        """Test búsqueda básica - endpoint principal."""
        headers = {"X-API-Key": "ml-api-key-user-2024"}
        response = client.get("/api/v1/items", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert isinstance(data["data"], list)
    
    def test_search_with_limit(self, client):
        """Test paginación - funcionalidad crítica."""
        headers = {"X-API-Key": "ml-api-key-user-2024"}
        response = client.get("/api/v1/items?limit=3", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) <= 3
        assert data["meta"]["limit"] == 3
    
    def test_item_by_id_not_found(self, client):
        """Test manejo de errores 404 - crítico para UX."""
        headers = {"X-API-Key": "ml-api-key-user-2024"}
        response = client.get("/api/v1/items/MLA999999999", headers=headers)
        # Puede ser 404 o 400 dependiendo de la validación
        assert response.status_code in [400, 404]
        data = response.json()
        # Verificar que hay información de error
        assert "code" in data or "detail" in data
    
    def test_popular_items(self, client):
        """Test items populares - funcionalidad de negocio."""
        headers = {"X-API-Key": "ml-api-key-user-2024"}
        response = client.get("/api/v1/items/popular?limit=3", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]) <= 3
    
    def test_available_items(self, client):
        """Test items disponibles - filtrado crítico."""
        headers = {"X-API-Key": "ml-api-key-user-2024"}
        response = client.get("/api/v1/items/available?limit=3", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        
        # Todos deben tener stock
        for item in data["data"]:
            assert item["available_quantity"] > 0
