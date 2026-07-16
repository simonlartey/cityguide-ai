from flask import Blueprint, current_app, jsonify, request

from app.providers.places.errors import PlacesProviderError
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

    places_provider = current_app.extensions["places_provider"]

    service = SearchService(places_provider)

    try:
        response = service.search(search_request)
    except PlacesProviderError:
        current_app.logger.exception(
            "Places provider failed during search."
        )

        return jsonify(
            {
                "error": {
                    "code": "places_provider_unavailable",
                    "message": (
                        "Local recommendations are temporarily unavailable."
                    ),
                }
            }
        ), 503

    return jsonify(response), 200