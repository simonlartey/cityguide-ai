from flask import (
    Blueprint,
    current_app,
    jsonify,
    redirect,
    request,
)

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
    assistant_provider = current_app.extensions["assistant_provider"]

    service = SearchService(
        places_provider=places_provider,
        assistant_provider=assistant_provider,
    )

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


@search_api_bp.get("/place-photo")
def get_place_photo():
    """Resolve a Google Places photo without exposing the API key."""

    photo_name = request.args.get("name", "").strip()
    width_value = request.args.get("width", "800")

    try:
        max_width = int(width_value)
    except ValueError:
        return jsonify(
            {
                "error": {
                    "code": "invalid_photo_request",
                    "message": "Photo width must be an integer.",
                }
            }
        ), 400

    places_provider = current_app.extensions["places_provider"]

    get_photo_url = getattr(
        places_provider,
        "get_photo_url",
        None,
    )

    if not callable(get_photo_url):
        return jsonify(
            {
                "error": {
                    "code": "place_photos_unavailable",
                    "message": (
                        "Place photos are unavailable for "
                        "the configured provider."
                    ),
                }
            }
        ), 503

    try:
        photo_url = get_photo_url(
            photo_name,
            max_width=max_width,
        )
    except ValueError as error:
        return jsonify(
            {
                "error": {
                    "code": "invalid_photo_request",
                    "message": str(error),
                }
            }
        ), 400
    except PlacesProviderError:
        current_app.logger.exception(
            "Places provider failed while loading a photo."
        )

        return jsonify(
            {
                "error": {
                    "code": "place_photo_unavailable",
                    "message": (
                        "This place photo is temporarily "
                        "unavailable."
                    ),
                }
            }
        ), 503

    return redirect(photo_url, code=302)
