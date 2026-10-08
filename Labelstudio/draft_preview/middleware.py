from pathlib import Path
from django.http import HttpResponse


class DraftPreviewMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/draft-preview.js':
            return HttpResponse(Path(__file__).with_name('panel.js').read_text(), content_type='application/javascript')
        response = self.get_response(request)
        if (request.path.startswith('/projects/') and response.status_code == 200
                and 'text/html' in response.get('Content-Type', '')
                and not response.streaming and not response.get('Content-Encoding')):
            response.content = response.content.replace(b'</body>', b'<script src="/draft-preview.js?v=2" defer></script></body>')
            response['Content-Length'] = str(len(response.content))
        return response
