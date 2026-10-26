"""Select the latest saved mask after Data Manager finishes loading a task."""
from pathlib import Path
import argparse

OLD = 'l&&(n&&"prediction"===l.type?i.selectPrediction(l.id):i.selectAnnotation(l.id),this.datamanager.invoke("annotationSet",l))'
PREVIOUS = 'if(!this.labelStream&&!n&&(!s||"auto"===s||String(this.task.default_selected_annotation)===s)){const e=globalThis.__labelStudioLatestSavedTab(i,this.task.annotations||[]);e&&(l=e)}' + OLD
NEW = 'if(!this.labelStream&&!n){const e=await globalThis.__labelStudioLatestTaskTab(i,this.task);e&&(l=e)}' + OLD


def patch(source):
    if NEW in source:
        return source
    if PREVIOUS in source:
        return source.replace(PREVIOUS, NEW)
    if source.count(OLD) != 1:
        raise ValueError('Unsupported Data Manager annotation selection anchor')
    return source.replace(OLD, NEW)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('bundle', type=Path)
    path = parser.parse_args().bundle
    path.write_text(patch(path.read_text()))
