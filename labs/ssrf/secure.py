from urllib.parse import urlsplit
from labs.support import Denied, lab_fetch

def fetch_preview(url, public_origin, internal_origin):
    parsed = urlsplit(url)
    if url != public_origin + "/public/info" or parsed.query or parsed.fragment:
        raise Denied("Only the configured public preview endpoint is allowed")
    return lab_fetch(url, {public_origin})
