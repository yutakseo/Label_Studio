"""Preserve fractional coordinates for brush and eraser strokes."""
from pathlib import Path
import argparse

OLD = 'addPoint(e,n){t.addPoint(Math.floor(e),Math.floor(n))}'
NEW = 'addPoint(e,n){t.addPoint(e,n)}'


def patch(source):
    if source.count(OLD) == 0 and source.count(NEW) == 2:
        return source
    if source.count(OLD) != 2:
        raise ValueError('Unsupported editor bundle: expected brush and eraser anchors')
    return source.replace(OLD, NEW)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('bundle', type=Path)
    args = parser.parse_args()
    source = args.bundle.read_text()
    patched = patch(source)
    if patched != source:
        args.bundle.write_text(patched)
