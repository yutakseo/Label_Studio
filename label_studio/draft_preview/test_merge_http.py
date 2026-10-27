import json
import os
import unittest
from types import SimpleNamespace

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.label_studio")
import django
django.setup()
from django.test import RequestFactory
from django.urls import resolve

from .merge_views import preview
from .test_merge import region


class MergeHttpTests(unittest.TestCase):
    def request(self, authenticated=True, csrf_bypass=True, data=None):
        if data is None:
            data = {"sources": [[region([[1, 0]])], [region([[0, 1]])]],
                    "from_name": "brush", "to_name": "image", "label": "Exposure"}
        request = RequestFactory().post("/mask-merge/preview", json.dumps(data), content_type="application/json")
        request.user = SimpleNamespace(is_authenticated=authenticated)
        request._dont_enforce_csrf_checks = csrf_bypass
        return request

    def test_union_preview_and_route(self):
        response = preview(self.request())
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["stats"]["pixels"], 2)
        self.assertTrue(data["preview"].startswith("data:image/png;base64,"))
        self.assertEqual(resolve("/mask-merge/preview").func, preview)

    def test_multilabel_preview(self):
        other = region([[1, 1]])
        other["value"]["brushlabels"] = ["Other"]
        response = preview(self.request(data={"sources": [[region([[1, 0]])], [other]],
                                              "from_name": "brush", "to_name": "image", "label": None}))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual([r["value"]["brushlabels"] for r in data["results"]], [["Exposure"], ["Other"]])
        self.assertTrue(data["preview"].startswith("data:image/png;base64,"))

    def test_auth_csrf_and_invalid_input(self):
        self.assertEqual(preview(self.request(authenticated=False)).status_code, 401)
        self.assertEqual(preview(self.request(csrf_bypass=False)).status_code, 403)
        self.assertEqual(preview(self.request(data={})).status_code, 400)
        self.assertEqual(preview(self.request(data=[])).status_code, 400)


if __name__ == "__main__":
    unittest.main()
