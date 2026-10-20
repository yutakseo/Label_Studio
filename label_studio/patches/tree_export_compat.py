"""Allow dataset names without dates and show export validation details."""
from pathlib import Path
import argparse

BACKEND = [("parts[0] != 'files' or not parts[1].startswith('2026') or parts[2] != 'images'", "parts[0] != 'files' or parts[2] != 'images'"), ('files/2026*/images/... 경로가 필요합니다.', 'files/<데이터셋>/images/... 경로가 필요합니다.')]
FRONTEND = [('        throw new Error(error?.detail || error?.error || `내보내기 실패 (${response.status})`);', "        const messages = value => {\n          if (typeof value === 'string') return [value];\n          if (Array.isArray(value)) return value.flatMap(messages);\n          if (value && typeof value === 'object') return Object.values(value).flatMap(messages);\n          return [];\n        };\n        const details = messages(error?.validation_errors || error?.errors || error?.detail || error?.error || error);\n        throw new Error(details.join(' · ') || `내보내기 실패 (${response.status})`);")]

def patch(path, replacements):
    source = path.read_text()
    for old, new in replacements:
        if new in source and old not in source:
            continue
        if source.count(old) != 1:
            raise ValueError(f'Unsupported export code in {path}: {old}')
        source = source.replace(old, new)
    path.write_text(source)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    patch(args.directory / 'archive.py', BACKEND)
    patch(args.directory / 'panel.js', FRONTEND)
