"""Keep saved-author tabs separate from the signed-in annotator's editable tab."""
from pathlib import Path
import argparse

OLD = 'return!e.viewingAll||o.exitViewAll?r.editable=!0:r.editable=!1,r.setupHotKeys()'
NEW = 'return!e.viewingAll||o.exitViewAll?r.editable=globalThis.__labelStudioCanEditAnnotation(e,r):r.editable=!1,r.setupHotKeys()'
MARKER = '/* Keep original author tabs read-only and edit in the signed-in user\'s tab. */'


def patch(source):
    if NEW not in source:
        if source.count(OLD) != 1:
            raise ValueError('Unsupported annotation selection anchor')
        source = source.replace(OLD, NEW)
    helper = Path(__file__).with_suffix('.js').read_text()
    if source.startswith(MARKER):
        end = source.find('\n};', len(MARKER))
        if 'globalThis.__labelStudioOwnTab' in source[:source.find('(self.webpackChunk')]:
            end = source.find('\n};', source.find('globalThis.__labelStudioOwnTab'))
        if end < 0:
            raise ValueError('Unterminated user tab helper')
        source = source[end + len('\n};'):].lstrip('\n')
    if helper not in source:
        source = helper + '\n' + source
    return source


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('bundle', type=Path)
    path = parser.parse_args().bundle
    original = path.read_text()
    updated = patch(original)
    if updated != original:
        path.write_text(updated)
