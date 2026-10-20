"""Assign an unowned imported annotation only after its labeling result changes."""
from pathlib import Path
import argparse

ANCHOR = '    def perform_destroy(self, annotation):\n'
METHOD = '''    def perform_update(self, serializer):
        annotation = serializer.instance
        result_changed = ('result' in serializer.validated_data
                          and serializer.validated_data['result'] != annotation.result)
        if annotation.completed_by_id is None and result_changed:
            serializer.save(completed_by=self.request.user)
        else:
            serializer.save()

'''


def patch(source):
    if METHOD in source:
        return source
    if source.count(ANCHOR) != 1:
        raise ValueError('Unsupported annotation API: perform_destroy anchor')
    return source.replace(ANCHOR, METHOD + ANCHOR)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    source = args.source.read_text()
    result = patch(source)
    if result != source:
        args.source.write_text(result)
