"""Route pen coordinates directly through the image editor's drawing handlers."""
from pathlib import Path
import argparse

REPLACEMENTS = (
    ('componentDidMount(){const{item:e}=this.props;e.containerRef.addEventListener("mousedown",this.startRightPan,true),',
     'componentDidMount(){const{item:e}=this.props;this.disposePenInput=globalThis.__labelStudioPenInput(this);e.containerRef.addEventListener("mousedown",this.startRightPan,true),'),
    ('componentWillUnmount(){this.endRightPan();',
     'componentWillUnmount(){this.disposePenInput?.();this.endRightPan();'),
)


def patch(source):
    for old, new in REPLACEMENTS:
        if new in source:
            continue
        if source.count(old) != 1:
            raise ValueError(f'Unsupported editor bundle: {old!r}')
        source = source.replace(old, new)
    helper = Path(__file__).with_suffix('.js').read_text()
    marker = '/* Feed pen coordinates directly to the image editor; keep mouse input native. */'
    start = source.find(marker)
    if start != -1:
        end = source.find('\n};', start + len(marker))
        if end == -1:
            raise ValueError('Unsupported editor bundle: unterminated pen input helper')
        source = source[:start] + source[end + len('\n};'):].lstrip('\n')
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
