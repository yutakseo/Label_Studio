import base64
import io
import json
from pathlib import Path

import numpy as np
from PIL import Image
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.db import transaction
from tasks.api import AnnotationsListAPI
from tasks.models import Task

from .mask_merge import merge_masks


class MergeAnnotationAPI(AnnotationsListAPI):
    """Keep standard creation permissions and ownership; persist the tab title separately."""
    keep_separate_annotation = True

    @transaction.atomic
    def perform_create(self, serializer):
        super().perform_create(serializer)
        task = Task.objects.select_for_update().get(pk=serializer.instance.task_id)
        meta = dict(task.meta or {})
        names = dict(meta.get("mask_merge_annotations", {}))
        names[str(serializer.instance.pk)] = {"name": "MERGE"}
        meta["mask_merge_annotations"] = names
        task.meta = meta
        task.save(update_fields=["meta"])


def script(request):
    return HttpResponse(Path(__file__).with_name("merge_panel.js").read_text(),
                        content_type="application/javascript")


@require_POST
@csrf_protect
def preview(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "로그인이 필요합니다."}, status=401)
    try:
        data = json.loads(request.body)
        results, mask, stats = merge_masks(data["sources"], data["from_name"],
                                           data["to_name"], data["label"])
        rgba = np.zeros((*mask.shape, 4), dtype=np.uint8)
        rgba[:, :, :3] = [255, 70, 70]
        rgba[:, :, 3] = (mask > 0).astype(np.uint8) * 140
        image = Image.fromarray(rgba)
        image.thumbnail((1400, 1000))
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return JsonResponse({"results": results, "stats": stats,
                             "preview": "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()})
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        return JsonResponse({"error": str(exc)}, status=400)
