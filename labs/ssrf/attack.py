from . import vulnerable, secure
from labs.support import json_service, outcome, rejected

def demonstrate(work):
    with json_service({"/public/info": {"title": "Synthetic public page"}}) as (public, public_requests):
        with json_service({"/internal/metadata": {"dummy_metadata": "LAB_INTERNAL_ONLY"}}) as (internal, internal_requests):
            target = internal + "/internal/metadata"
            stolen = vulnerable.fetch_preview(target, public, internal)
            count = len(internal_requests)
            blocked = rejected(lambda: secure.fetch_preview(target, public, internal)) and len(internal_requests) == count
            normal = secure.fetch_preview(public + "/public/info", public, internal)
            return outcome(stolen.get("dummy_metadata") == "LAB_INTERNAL_ONLY", blocked, "title" in normal,
                           {"vulnerable_response": stolen, "internal_mock_requests": list(internal_requests), "public_mock_requests": list(public_requests), "external_traffic": False})
