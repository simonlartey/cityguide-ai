from flask import Blueprint, jsonify, request

from app.providers.places.mock_provider import MockPlacesProvider
from app.schemas.search import SearchRequest, SearchValidationError
from app.services.search_service import SearchService


search_api_bp = Blueprint(
    "search_api",
    __name__,
    url_prefix="/api/v1",
)


@search_api_bp.post("/search")
def search_places():
    """Return normalized place recommendations for a user query."""

    if not request.is_json:
        return jsonify(
            {
                "error": {
                    "code": "invalid_content_type",
                    "message": "Request body must use application/json.",
                }
            }
        ), 415

    try:
        search_request = SearchRequest.from_dict(
            request.get_json(silent=True)
        )
    except SearchValidationError as error:
        return jsonify(
            {
                "error": {
                    "code": "invalid_search_request",
                    "message": str(error),
                }
            }
        ), 400

    service = SearchService(MockPlacesProvider())
    response = service.search(search_request)

    return jsonify(response), 200