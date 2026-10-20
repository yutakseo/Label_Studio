"""Snap brush and eraser strokes to a 0.1 image-pixel grid."""
from pathlib import Path
import argparse

OLD = 'addPoint(e,n){t.addPoint(Math.floor(e),Math.floor(n))}'
NEW = 'addPoint(e,n){t.addPoint(e,n)}'


GRID_OLD = 'addPoint(t,n){t/=e.parent.scaleX,n/=e.parent.scaleY,e.points.push(t),e.points.push(n)}'
GRID_NEW = 'addPoint(t,n){t=Math.round(t/e.parent.scaleX*10)/10,n=Math.round(n/e.parent.scaleY*10)/10,e.points.push(t),e.points.push(n)}'


def patch(source):
    if source.count(OLD) == 2 and source.count(NEW) == 0:
        source = source.replace(OLD, NEW)
    elif source.count(OLD) != 0 or source.count(NEW) != 2:
        raise ValueError('Unsupported editor bundle: expected brush and eraser anchors')
    if source.count(GRID_OLD) == 1 and source.count(GRID_NEW) == 0:
        source = source.replace(GRID_OLD, GRID_NEW)
    elif source.count(GRID_OLD) != 0 or source.count(GRID_NEW) != 1:
        raise ValueError('Unsupported editor bundle: expected brush point model anchor')
    return source


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('bundle', type=Path)
    args = parser.parse_args()
    source = args.bundle.read_text()
    patched = patch(source)
    if patched != source:
        args.bundle.write_text(patched)
