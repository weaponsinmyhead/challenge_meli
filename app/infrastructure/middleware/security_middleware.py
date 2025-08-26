import time
import secrets
from typing import Optional, Dict, Any
from fastapi import Request, Response, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging
from app.infrastructure.config.env_config import config

# Configurar logging
logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware de seguridad que implementa:
    - Autenticación por API Key
    - Rate limiting básico
    - Headers de seguridad
    - Logging de accesos
    """
    
    def __init__(self, app, api_keys: Optional[Dict[str, str]] = None):
        super().__init__(app)
        # API Keys desde variables de entorno
        self.api_keys = api_keys or config.get_api_keys()
        
        # Rate limiting desde configuración
        self.rate_limit_requests = config.RATE_LIMIT_REQUESTS
        self.rate_limit_window = config.RATE_LIMIT_WINDOW
        self.request_counts: Dict[str, Dict[str, Any]] = {}
        
        # Rutas públicas desde configuración
        self.public_routes = config.get_public_routes()
    
    async def dispatch(self, request: Request, call_next):
        """Procesa cada request aplicando medidas de seguridad."""
        start_time = time.time()
        
        try:
            # 1. Verificar rate limiting
            if not self._check_rate_limit(request):
                return self._create_error_response(
                    status.HTTP_429_TOO_MANY_REQUESTS,
                    "RATE_LIMIT_EXCEEDED",
                    "Too many requests. Please try again later."
                )
            
            # 2. Verificar autenticación (solo para rutas protegidas)
            if not self._is_public_route(request.url.path):
                auth_result = self._authenticate_request(request)
                if not auth_result["valid"]:
                    return self._create_error_response(
                        status.HTTP_401_UNAUTHORIZED,
                        "AUTHENTICATION_REQUIRED",
                        auth_result["message"]
                    )
                
                # Agregar información del usuario al request
                request.state.user_role = auth_result["role"]
                request.state.api_key = auth_result["api_key"]
            
            # 3. Procesar request
            response = await call_next(request)
            
            # 4. Agregar headers de seguridad
            self._add_security_headers(response)
            
            # 5. Log del acceso
            self._log_access(request, response, time.time() - start_time)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in security middleware: {str(e)}")
            return self._create_error_response(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "INTERNAL_ERROR",
                "Internal server error"
            )
    
    def _is_public_route(self, path: str) -> bool:
        """Verifica si la ruta es pública."""
        # Verificar rutas exactas primero
        if path in self.public_routes:
            return True
        
        # Verificar si la ruta es un subdirectorio de una ruta pública (ej. /static/css)
        for public_route in self.public_routes:
            if public_route != '/' and path.startswith(public_route):
                return True
        
        return False
    
    def _authenticate_request(self, request: Request) -> Dict[str, Any]:
        """
        Autentica el request usando API Key.
        
        Soporta dos métodos:
        1. Header: X-API-Key
        2. Query parameter: api_key
        """
        api_key = None
        
        # Método 1: Header X-API-Key
        api_key = request.headers.get("X-API-Key")
        
        # Método 2: Query parameter
        if not api_key:
            api_key = request.query_params.get("api_key")
        
        if not api_key:
            return {
                "valid": False,
                "message": "API Key required. Use X-API-Key header or api_key query parameter.",
                "role": None,
                "api_key": None
            }
        
        # Verificar si la API Key es válida
        if api_key in self.api_keys:
            return {
                "valid": True,
                "message": "Authentication successful",
                "role": self.api_keys[api_key],
                "api_key": api_key
            }
        
        return {
            "valid": False,
            "message": "Invalid API Key",
            "role": None,
            "api_key": api_key
        }
    
    def _check_rate_limit(self, request: Request) -> bool:
        """
        Implementa rate limiting básico por IP.
        Permite N requests por minuto por IP.
        """
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        
        # Limpiar contadores antiguos
        self._cleanup_old_requests(current_time)
        
        # Verificar límite para esta IP
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = {
                "count": 0,
                "window_start": current_time
            }
        
        ip_data = self.request_counts[client_ip]
        
        # Si estamos en una nueva ventana de tiempo, resetear contador
        if current_time - ip_data["window_start"] > self.rate_limit_window:
            ip_data["count"] = 0
            ip_data["window_start"] = current_time
        
        # Verificar límite
        if ip_data["count"] >= self.rate_limit_requests:
            return False
        
        # Incrementar contador
        ip_data["count"] += 1
        return True
    
    def _get_client_ip(self, request: Request) -> str:
        """Obtiene la IP del cliente considerando proxies."""
        # Verificar headers de proxy
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # IP directa
        return request.client.host if request.client else "unknown"
    
    def _cleanup_old_requests(self, current_time: float):
        """Limpia contadores de requests antiguos para liberar memoria."""
        expired_ips = []
        for ip, data in self.request_counts.items():
            if current_time - data["window_start"] > self.rate_limit_window * 2:
                expired_ips.append(ip)
        
        for ip in expired_ips:
            del self.request_counts[ip]
    
    def _add_security_headers(self, response: Response):
        """Agrega headers de seguridad a la respuesta."""
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'",
            "X-API-Version": "1.0.0"
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value
    
    def _log_access(self, request: Request, response: Response, duration: float):
        """Registra el acceso en los logs."""
        client_ip = self._get_client_ip(request)
        method = request.method
        path = request.url.path
        status_code = response.status_code
        user_agent = request.headers.get("User-Agent", "unknown")
        api_key = getattr(request.state, "api_key", "public")
        
        logger.info(
            f"ACCESS: {client_ip} - {method} {path} - {status_code} - "
            f"{duration:.3f}s - {api_key} - {user_agent}"
        )
    
    def _create_error_response(self, status_code: int, error_code: str, message: str) -> JSONResponse:
        """Crea una respuesta de error estandarizada."""
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": error_code,
                    "message": message,
                    "timestamp": time.time()
                }
            }
        )


class APIKeyValidator:
    """
    Validador de API Keys para uso en dependencias de FastAPI.
    """
    
    def __init__(self, required_role: Optional[str] = None):
        self.required_role = required_role
        self.security = HTTPBearer(auto_error=False)
    
    async def __call__(self, request: Request) -> Dict[str, Any]:
        """Valida API Key y rol requerido."""
        # Si ya fue validado por el middleware, usar esa información
        if hasattr(request.state, "user_role"):
            user_info = {
                "role": request.state.user_role,
                "api_key": request.state.api_key
            }
            
            # Verificar rol si es requerido
            if self.required_role and user_info["role"] != self.required_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": {
                            "code": "INSUFFICIENT_PERMISSIONS",
                            "message": f"Role '{self.required_role}' required"
                        }
                    }
                )
            
            return user_info
        
        # Si no hay información de usuario, es una ruta pública
        return {"role": "public", "api_key": None}


# Instancias predefinidas para diferentes roles
require_admin = APIKeyValidator("admin")
require_user = APIKeyValidator("user") 
require_readonly = APIKeyValidator("readonly")
optional_auth = APIKeyValidator()  # Sin rol requerido
