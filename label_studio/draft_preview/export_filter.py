"""Exclude comparison-only original masks from every serialized export."""
from pathlib import Path

MARKER = '        # Comparison-only originals must never enter exports.\n'
OLD = '''        return ret

    class Meta:
        model = Task
'''
NEW = '''        # Comparison-only originals must never enter exports.
        original_ids = set(task.predictions.filter(
            model_version='mask_original').values_list('id', flat=True))
        if 'predictions' in ret:
            ret['predictions'] = [
                item for item in ret['predictions']
                if (item.get('id') if isinstance(item, dict) else item) not in original_ids
                and not (isinstance(item, dict) and item.get('model_version') == 'mask_original')
            ]
        if 'total_predictions' in ret:
            ret['total_predictions'] = task.predictions.exclude(model_version='mask_original').count()
        return ret

    class Meta:
        model = Task
'''


def patch(path):
    path = Path(path)
    source = path.read_text()
    if MARKER in source:
        return
    if source.count(OLD) != 1:
        raise ValueError('Unsupported export serializer: expected Task representation hook')
    path.write_text(source.replace(OLD, NEW))


if __name__ == '__main__':
    patch(Path(__file__).resolve().parents[1] / 'data_export/serializers.py')
