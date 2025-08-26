"""
Manejadores de errores centralizados.
Proporciona respuestas consistentes para diferentes tipos de errores.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.domain.core.exceptions import DomainError
from app.domain.core.api_response import ErrorResponse


def _create_error_response(code: str, message: str, status: int, cause=None) -> dict:
    """
    Crea una respuesta de error consistente.
    
    Args:
        code: Código de error
        message: Mensaje de error
        status: Código de estado HTTP
        cause: Causa del error (opcional)
        
    Returns:
        Diccionario con la respuesta de error
    """
    return ErrorResponse(
        code=code,
        message=message,
        status=status,
        cause=cause or []
    ).model_dump()


async def api_error_handler(_: Request, exc: DomainError) -> JSONResponse:
    """
    Manejador para errores del dominio.
    
    Args:
        _: Request (no usado)
        exc: Excepción del dominio
        
    Returns:
        Respuesta JSON con el error
    """
    status = getattr(exc, "status", 400)
    return JSONResponse(
        status_code=status,
        content=_create_error_response(
            code=getattr(exc, "code", "DOMAIN_ERROR"),
            message=exc.message,
            status=status,
            cause=exc.details
        )
    )


async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Manejador para errores de validación.
    
    Args:
        _: Request (no usado)
        exc: Excepción de validación
        
    Returns:
        Respuesta JSON con el error
    """
    return JSONResponse(
        status_code=422,
        content=_create_error_response(
            code="VALIDATION_ERROR",
            message="Invalid request data",
            status=422,
            cause=[str(error) for error in exc.errors()]
        )
    )


async def http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Manejador para excepciones HTTP de Starlette.
    
    Args:
        _: Request (no usado)
        exc: Excepción HTTP
        
    Returns:
        Respuesta JSON con el error
    """
    # Si ya es un ErrorResponse, devolverlo directamente
    if hasattr(exc, "detail") and isinstance(exc.detail, dict) and "code" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=ErrorResponse(**exc.detail).model_dump())
    
    return JSONResponse(
        status_code=exc.status_code,
        content=_create_error_response(
            code=str(exc.status_code),
            message=exc.detail,
            status=exc.status_code,
            cause=[]
        )
    )


async def starlette_http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Manejador para excepciones HTTP de Starlette.
    
    Args:
        _: Request (no usado)
        exc: Excepción HTTP
        
    Returns:
        Respuesta JSON con el error
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=_create_error_response(
            code=str(exc.status_code),
            message=str(exc.detail),
            status=exc.status_code,
            cause=[]
        )
    )


async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    """
    Manejador para excepciones no manejadas.
    
    Args:
        _: Request (no usado)
        exc: Excepción no manejada
        
    Returns:
        Respuesta JSON con el error
    """
    return JSONResponse(
        status_code=500,
        content=_create_error_response(
            code="INTERNAL_ERROR",
            message="An unexpected error occurred",
            status=500,
            cause=[str(exc)]
        )
    )


def setup_error_handlers(app):
    """
    Configura todos los manejadores de errores en la aplicación FastAPI.
    
    Args:
        app: Instancia de FastAPI
    """
    app.add_exception_handler(DomainError, api_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
