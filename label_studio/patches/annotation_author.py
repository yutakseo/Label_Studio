"""Do not identify imported annotations without a known author as Admin."""
from pathlib import Path
import argparse

OLD = 'return null!=(t=e.createdBy)?t:"Admin"})(e)'
NEW = 'return e.createdBy||"작성자 미지정"})(e)'


def patch(source):
    if source.count(NEW) == 1 and source.count(OLD) == 0:
        return source
    if source.count(OLD) != 1 or source.count(NEW):
        raise ValueError('Unsupported editor bundle: annotation author fallback')
    return source.replace(OLD, NEW)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('bundle', type=Path)
    args = parser.parse_args()
    source = args.bundle.read_text()
    result = patch(source)
    if result != source:
        args.bundle.write_text(result)
