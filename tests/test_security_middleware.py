"""
Tests para el middleware de seguridad.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestSecurityMiddleware:
    """Tests para el middleware de seguridad."""
    
    def test_health_endpoint_public_access(self):
        """El endpoint de health debe ser accesible sin API key."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
    
    def test_protected_endpoint_without_api_key(self):
        """Los endpoints protegidos deben requerir API key."""
        response = client.get("/api/v1/items/MLA111222333")
        assert response.status_code == 401
        assert "AUTHENTICATION_REQUIRED" in response.json()["error"]["code"]
    
    def test_protected_endpoint_with_valid_api_key_header(self):
        """Debe permitir acceso con API key válida en header."""
        headers = {"X-API-Key": "ml-api-key-user-2024"}
        response = client.get("/api/v1/items/MLA111222333", headers=headers)
        assert response.status_code in [200, 404]  # 404 si el item no existe
    
    def test_protected_endpoint_with_valid_api_key_query(self):
        """Debe permitir acceso con API key válida en query parameter."""
        response = client.get("/api/v1/items/MLA111222333?api_key=ml-api-key-user-2024")
        assert response.status_code in [200, 404]  # 404 si el item no existe
    
    def test_protected_endpoint_with_invalid_api_key(self):
        """Debe rechazar API keys inválidas."""
        headers = {"X-API-Key": "invalid-key"}
        response = client.get("/api/v1/items/MLA111222333", headers=headers)
        assert response.status_code == 401
        assert "Invalid API Key" in response.json()["error"]["message"]
    
    def test_security_headers_present(self):
        """Debe agregar headers de seguridad a las respuestas."""
        response = client.get("/api/v1/health")
        
        # Verificar headers de seguridad
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        assert "X-XSS-Protection" in response.headers
        assert "Strict-Transport-Security" in response.headers
        assert "X-API-Version" in response.headers
    
    def test_different_api_key_roles(self):
        """Debe reconocer diferentes roles de API keys."""
        # Test admin key
        headers = {"X-API-Key": "ml-api-key-admin-2024"}
        response = client.get("/api/v1/items", headers=headers)
        assert response.status_code == 200
        
        # Test user key
        headers = {"X-API-Key": "ml-api-key-user-2024"}
        response = client.get("/api/v1/items", headers=headers)
        assert response.status_code == 200
        
        # Test readonly key
        headers = {"X-API-Key": "ml-api-key-readonly-2024"}
        response = client.get("/api/v1/items", headers=headers)
        assert response.status_code == 200
    
    def test_rate_limiting_basic(self):
        """Test básico de rate limiting (no exhaustivo por tiempo)."""
        headers = {"X-API-Key": "ml-api-key-user-2024"}
        
        # Hacer algunas requests para verificar que no hay error inmediato
        for _ in range(5):
            response = client.get("/api/v1/health", headers=headers)
            assert response.status_code == 200
    
    def test_docs_access_without_auth(self):
        """La documentación debe ser accesible sin autenticación."""
        response = client.get("/docs")
        assert response.status_code == 200
        
        response = client.get("/redoc")
        assert response.status_code == 200
