import tempfile
import unittest
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from .storage import model_directory


class SharedStorageTests(unittest.TestCase):
    def test_adopts_existing_model_once_and_preserves_original(self):
        with tempfile.TemporaryDirectory() as base:
            personal = Path(base) / 'reference_segmenter/16/1'
            personal.mkdir(parents=True)
            (personal / 'key.pt').write_bytes(b'weights')
            (personal / 'key.json').write_text('{"round":28}')
            corrections = personal / 'key.samples/corrections'
            corrections.mkdir(parents=True)
            (corrections / 'task_9_0_0.npz').write_bytes(b'pair')
            with ThreadPoolExecutor(max_workers=2) as pool:
                paths = list(pool.map(lambda _: model_directory(base, 16, 'key'), range(2)))
            self.assertEqual(paths[0], paths[1])
            shared = paths[0]
            self.assertEqual((shared / 'key.pt').read_bytes(), b'weights')
            self.assertEqual((shared / 'key.samples/corrections/user_1_task_9_0_0.npz').read_bytes(), b'pair')
            self.assertTrue((corrections / 'task_9_0_0.npz').exists())
            (shared / 'key.pt').write_bytes(b'updated')
            self.assertEqual((model_directory(base, 16, 'key') / 'key.pt').read_bytes(), b'updated')
            self.assertFalse((model_directory(base, 17, 'key') / 'key.pt').exists())
            self.assertFalse((model_directory(base, 16, 'other') / 'key.pt').exists())
