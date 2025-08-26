from typing import List, Optional


class DomainError(Exception):
    """Excepción base para errores del dominio."""
    
    def __init__(self, message: str, code: str = "DOMAIN_ERROR", details: Optional[List[str]] = None):
        self.message = message
        self.code = code
        self.details = details or []
        super().__init__(self.message)


class ItemNotFoundError(DomainError):
    """Excepción cuando no se encuentra un item."""
    
    def __init__(self, item_id: str):
        super().__init__(
            message=f"Item with id '{item_id}' not found",
            code="ITEM_NOT_FOUND",
            details=[f"Item ID: {item_id}"]
        )
        self.item_id = item_id
        self.status_code = 404


class InvalidSearchCriteriaError(DomainError):
    """Excepción para criterios de búsqueda inválidos."""
    
    def __init__(self, field: str, value: str, reason: str):
        super().__init__(
            message=f"Invalid search criteria: {field} = {value}",
            code="INVALID_SEARCH_CRITERIA",
            details=[f"Field: {field}", f"Value: {value}", f"Reason: {reason}"]
        )


class DataValidationError(DomainError):
    """Excepción para errores de validación de datos."""
    
    def __init__(self, field: str, value: str, expected_type: str):
        super().__init__(
            message=f"Data validation failed for field '{field}'",
            code="DATA_VALIDATION_ERROR",
            details=[f"Field: {field}", f"Value: {value}", f"Expected: {expected_type}"]
        )


class RepositoryError(DomainError):
    """Excepción base para errores de repositorio."""
    
    def __init__(self, message: str, repository_name: str):
        super().__init__(
            message=message,
            code="REPOSITORY_ERROR",
            details=[f"Repository: {repository_name}"]
        )


class FileNotFoundError(RepositoryError):
    """Excepción cuando no se encuentra el archivo de datos."""
    
    def __init__(self, file_path: str):
        super().__init__(
            message=f"Data file not found: {file_path}",
            repository_name="FileRepository"
        )


class SerializationError(DomainError):
    """Excepción para errores de serialización/deserialización."""
    
    def __init__(self, data_type: str, reason: str):
        super().__init__(
            message=f"Serialization error for {data_type}",
            code="SERIALIZATION_ERROR",
            details=[f"Type: {data_type}", f"Reason: {reason}"]
        )
