import pytest

from app.repositories.search_session import (
    SearchSessionRepository,
)


def test_search_session_repository_cannot_be_instantiated():
    with pytest.raises(TypeError):
        SearchSessionRepository()
