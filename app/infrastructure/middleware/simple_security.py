from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
import logging

logger = logging.getLogger(__name__)

class SimpleSecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware de seguridad simplificado que solo agrega headers básicos
    y logging opcional.
    """
    
    def __init__(self, app, enable_api_key_auth: bool = False):
        super().__init__(app)
        self.enable_api_key_auth = enable_api_key_auth
        self.api_keys = {
            "ml-api-key-admin-2024": "admin",
            "ml-api-key-user-2024": "user",
            "ml-api-key-readonly-2024": "readonly"
        }
        self.public_routes = {"/docs", "/redoc", "/openapi.json", "/test", "/api/v1/health", "/"}
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        
        if self.enable_api_key_auth and request.url.path not in self.public_routes:
            api_key = request.headers.get("X-API-Key") or request.query_params.get("api_key")
            
            if not api_key or api_key not in self.api_keys:
                return JSONResponse(
                    status_code=401,
                    content={
                        "error": {
                            "code": "AUTHENTICATION_REQUIRED",
                            "message": "API Key required. Use X-API-Key header or api_key query parameter."
                        }
                    }
                )
            
            
            request.state.user_role = self.api_keys[api_key]
            request.state.api_key = api_key
        
        
        response = await call_next(request)
        
        
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        
        duration = time.time() - start_time
        logger.info(f"REQUEST: {request.method} {request.url.path} - {response.status_code} - {duration:.3f}s")
        
        return response
