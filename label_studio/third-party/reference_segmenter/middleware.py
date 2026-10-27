import hashlib
from pathlib import Path


class PanelMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if (request.path.startswith("/projects/") and response.status_code == 200
                and "text/html" in response.get("Content-Type", "")
                and not response.streaming and not response.get("Content-Encoding")):
            version = hashlib.sha256(Path(__file__).with_name("panel.js").read_bytes()).hexdigest()[:12]
            response.content = response.content.replace(
                b"</body>", f'<script src="/reference-segmenter/panel.js?v={version}" defer></script></body>'.encode())
            response["Content-Length"] = str(len(response.content))
        return response
