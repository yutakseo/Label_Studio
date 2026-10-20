"""Allow brush and eraser sizes from 0.2 to 30 in half-pixel steps."""
from pathlib import Path
import argparse

REPLACEMENTS = (
    ('value:e.strokeWidth,min:1,max:30,reverse:!0',
     'value:e.strokeWidth,min:.2,max:30,step:.5,reverse:!0', 4),
    ('(0,M.clamp)(e.strokeWidth-1,1,30)',
     '(0,M.clamp)(e.strokeWidth-.5,.2,30)', 4),
    ('(0,M.clamp)(e.strokeWidth+1,1,30)',
     '(0,M.clamp)(e.strokeWidth+.5,.2,30)', 4),
    ('Math.max(1,Math.min(30,i.strokeWidth+(t.deltaY<0?1:-1)))',
     'Math.max(.2,Math.min(30,i.strokeWidth+(t.deltaY<0?.5:-.5)))', 1),
    ('setStroke(t){e.strokeWidth=t,e.updateCursor()}',
     'setStroke(t){e.strokeWidth=Math.max(.2,Math.min(30,Math.round(t*2)/2)),e.updateCursor()}', 4),
)


def patch(source):
    for old, new, count in REPLACEMENTS:
        if source.count(old) == 0 and source.count(new) == count:
            continue
        if source.count(old) != count or source.count(new):
            raise ValueError(f'Unsupported editor bundle: expected {count} occurrences of {old!r}')
        source = source.replace(old, new)
    return source


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('bundle', type=Path)
    args = parser.parse_args()
    source = args.bundle.read_text()
    patched = patch(source)
    if patched != source:
        args.bundle.write_text(patched)
