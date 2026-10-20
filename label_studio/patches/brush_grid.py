"""Use square grid stamps for live drawing, redraw/hit testing, and export."""
from pathlib import Path
import argparse

REPLACEMENTS = (
    ('a.stroke(),a.restore(),o=i,s=r',
     'a.fillStyle=e.strokeColor;const gridOrigin=e.prepareCoords([0,0]),gridUnit=e.prepareCoords([e.scaleX*.1,e.scaleY*.1]);globalThis.__labelStudioSquareBrush(a,[...e.prepareCoords(n.length?[o,s]:[i,r]),...e.prepareCoords([i,r])],t.strokeWidth*e.scaleX*e.parent.stageScale,gridUnit[0]-gridOrigin[0],gridUnit[1]-gridOrigin[1],...gridOrigin);a.restore(),o=i,s=r'),
    ('e.globalCompositeOperation=o,e.stroke(),e.restore()',
     'e.globalCompositeOperation=o,e.fillStyle=i,globalThis.__labelStudioSquareBrush(e,t,n),e.restore()'),
    ('s.globalCompositeOperation=e.compositeOperation,s.stroke()',
     's.globalCompositeOperation=e.compositeOperation,s.fillStyle="#000",globalThis.__labelStudioSquareBrush(s,i.flatMap((v,k)=>k%2?[]:o(v,i[k+1])),e.relativeStrokeWidth/100*t),s.restore()'),
)


def patch(source):
    for old, new in REPLACEMENTS:
        if source.count(new) == 1 and source.count(old) == 0:
            continue
        if source.count(old) != 1 or source.count(new):
            raise ValueError(f'Unsupported editor bundle: {old!r}')
        source = source.replace(old, new)
    helper = Path(__file__).with_suffix('.js').read_text()
    if helper not in source:
        source = helper + '\n' + source
    return source


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('bundle', type=Path)
    args = parser.parse_args()
    source = args.bundle.read_text()
    result = patch(source)
    if result != source:
        args.bundle.write_text(result)
