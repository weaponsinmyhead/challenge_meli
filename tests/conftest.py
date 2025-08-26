import pytest
from app.domain.services.search_service import SearchService
from app.domain.services.item_service import ItemService
from app.infrastructure.repositories.json_item_repository import JsonItemRepository

@pytest.fixture
def search_service():
    repo = JsonItemRepository()
    return SearchService(repo)

@pytest.fixture
def item_service():
    repo = JsonItemRepository()
    return ItemService(repo)

@pytest.fixture
def sample_items_list():
    repo = JsonItemRepository()
    return repo.find_all()