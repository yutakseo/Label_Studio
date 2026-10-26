"""Install per-user annotation saves, private drafts, and revision history."""
from pathlib import Path
import argparse


def replace_once(source, old, new):
    if new in source:
        return source
    if source.count(old) != 1:
        raise ValueError(f'Unsupported source: {old[:100]!r}')
    return source.replace(old, new)


def patch_api(source):
    source = source.replace('serializer.save(completed_by=self.request.user)',
                            'serializer.save(completed_by=self.request.user, updated_by=self.request.user)')
    source = source.replace('        return queryset.filter(task_id=task_id, user=self.request.user)',
        '        from draft_preview.user_isolation import latest_user_drafts\n        return latest_user_drafts(queryset.filter(task_id=task_id), self.request.user)')
    source = replace_once(source,
        '    def update(self, request, *args, **kwargs):\n        # save user history with annotator_id, time & annotation result',
        '''    def update(self, request, *args, **kwargs):
        from draft_preview.user_isolation import isolate_update
        return isolate_update(self, request, args, kwargs, self.update_isolated)

    def update_isolated(self, request, *args, **kwargs):
        # save user history with annotator_id, time & annotation result''')
    source = replace_once(source,
        '    def perform_destroy(self, annotation):\n        annotation.delete()',
        '''    def perform_destroy(self, annotation):
        from draft_preview.user_isolation import protect_delete
        protect_delete(annotation, self.request.user)
        annotation.delete()''')
    source = replace_once(source,
        '            serializer.save()\n\n    def perform_destroy(self, annotation):',
        '            serializer.save(completed_by=self.request.user, updated_by=self.request.user)\n\n    def perform_destroy(self, annotation):')
    source = replace_once(source,
        "        serializer.save(task_id=self.kwargs['pk'], annotation_id=annotation_id, user=self.request.user)",
        """        from draft_preview.user_isolation import draft_annotation
        annotation_id = draft_annotation(task_id, annotation_id, user)
        serializer.save(task_id=task_id, annotation_id=annotation_id, user=user)""")
    source = replace_once(source,
        '        return queryset.filter(task_id=task_id)',
        '        from draft_preview.user_isolation import latest_user_drafts\n        return latest_user_drafts(queryset.filter(task_id=task_id), self.request.user)')
    source = replace_once(source,
        "        if 'completed_by' not in ser.validated_data:\n            extra_args['completed_by'] = self.request.user",
        "        extra_args['completed_by'] = self.request.user")
    source = replace_once(source,
        'class AnnotationDraftAPI(generics.RetrieveUpdateDestroyAPIView):\n',
        '''class AnnotationDraftAPI(generics.RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

''')
    source = replace_once(source,
        '        annotation = ser.save(**extra_args)',
        '        from draft_preview.user_isolation import save_user_annotation\n        annotation = save_user_annotation(self, ser, extra_args)')
    source = replace_once(source,
        '        return queryset.filter(task_id=task_id, user=self.request.user)',
        '        from draft_preview.user_isolation import latest_user_drafts\n        return latest_user_drafts(queryset.filter(task_id=task_id), self.request.user)')
    return source


def patch_models(source):
    return replace_once(source,
        "    query_args = {'task': task, 'annotation': instance}",
        "    query_args = {'task': task, 'annotation': instance, 'user_id': instance.completed_by_id}")


def patch_middleware(source):
    return replace_once(source,
        '        self.get_response = get_response',
        '''        self.get_response = get_response
        from .user_isolation import install_revision_history
        install_revision_history()''')


def install(root):
    for name, patch in [('tasks/api.py', patch_api), ('tasks/models.py', patch_models),
                        ('draft_preview/middleware.py', patch_middleware)]:
        path = root / name
        original = path.read_text()
        changed = patch(original)
        if changed != original:
            path.write_text(changed)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    install(parser.parse_args().root)
