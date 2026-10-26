"""Project-shared models, with atomic adoption of existing personal models."""
from contextlib import ExitStack
import fcntl
import os
from pathlib import Path
import shutil
import tempfile


def model_directory(base, project_id, key):
    root = Path(base) / 'reference_segmenter' / str(project_id)
    shared = root / 'shared'
    shared.mkdir(parents=True, exist_ok=True)
    destination = shared / key
    with (shared / (key + '.migration.lock')).open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if destination.exists():
            return destination
        # Adopt one complete model family; never mix incompatible weights/data.
        candidates = [p for p in root.iterdir() if p.is_dir() and p.name.isdigit()
                      and (p / (key + '.pt')).exists()]
        source = max(candidates, key=lambda p: ((p / (key + '.pt')).stat().st_mtime_ns, p.name), default=None)
        staging = Path(tempfile.mkdtemp(prefix='.' + key + '-', dir=shared))
        try:
            with ExitStack() as locks:
                if source is not None:
                    legacy_lock = locks.enter_context((source / (key + ".lock")).open("a"))
                    fcntl.flock(legacy_lock, fcntl.LOCK_EX)
                    if (source / (key + '.retraining')).exists():
                        raise ValueError('기존 모델 재학습이 끝난 후 다시 실행하세요.')
                    for item in source.glob(key + '.*'):
                        if item.suffix in ('.lock', '.tmp', '.retraining'):
                            continue
                        target = staging / item.name
                        if item.is_dir():
                            shutil.copytree(item, target)
                            if item.name == key + ".samples":
                                for pair in (target / "corrections").glob("task_*.npz"):
                                    pair.rename(pair.with_name(f"user_{source.name}_{pair.name}"))
                        else:
                            shutil.copy2(item, target)
            os.replace(staging, destination)
        finally:
            if staging.exists():
                shutil.rmtree(staging)
    return destination
