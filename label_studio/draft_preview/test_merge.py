import copy
import unittest

import numpy as np
from label_studio_sdk.converter.brush import mask2rle, decode_rle

from .mask_merge import merge_masks


def region(mask, **changes):
    mask = np.array(mask, dtype=np.uint8) * 255
    return {"id": "original", "type": "brushlabels", "from_name": "brush", "to_name": "image",
            "original_width": mask.shape[1], "original_height": mask.shape[0],
            "value": {"format": "rle", "brushlabels": ["Exposure"], "rle": mask2rle(mask)}, **changes}


class MergeTests(unittest.TestCase):
    def merge(self, sources):
        return merge_masks(sources, "brush", "image", "Exposure")

    def test_union_overlap_multiple_regions_and_source_preservation(self):
        sources = [[region([[1, 0], [0, 0]]), region([[0, 1], [0, 0]])],
                   [region([[1, 0], [1, 0]])], [region([[0, 0], [0, 1]])]]
        original = copy.deepcopy(sources)
        results, mask, stats = self.merge(sources)
        np.testing.assert_array_equal(mask, [[255, 255], [255, 255]])
        np.testing.assert_array_equal(decode_rle(results[0]["value"]["rle"]).reshape(2, 2, 4)[:, :, 3], mask)
        self.assertEqual(stats, {"sources": 3, "regions": 4, "pixels": 4})
        self.assertEqual(sources, original)
        self.assertNotEqual(results[0]["id"], "original")

    def test_unrelated_targets_and_non_brush_regions_are_excluded(self):
        sources = [[region([[1, 0]]), region([[0, 1]], to_name="other"), {"type": "rectanglelabels"}],
                   [region([[1, 0]])]]
        _, mask, stats = self.merge(sources)
        np.testing.assert_array_equal(mask, [[255, 0]])
        self.assertEqual(stats["regions"], 2)
        with self.assertRaises(ValueError):
            self.merge([sources[0], [region([[0, 1]], from_name="other")]])

    def test_empty_masks_are_valid(self):
        results, mask, stats = self.merge([[region([[0, 0]])], [region([[0, 0]])]])
        self.assertEqual(stats["pixels"], 0)
        self.assertFalse(mask.any())
        self.assertEqual(len(results), 1)

    def test_dimensions_rotation_and_malformed_stream_are_rejected(self):
        valid = region([[1, 0]])
        invalid = [region([[1], [0]]), region([[1, 0]], image_rotation=90),
                   region([[1, 0]], original_width=20_000_000),
                   region([[1, 0]], original_height=True),
                   {**valid, "value": {**valid["value"], "rle": [0]}}]
        for item in invalid:
            with self.subTest(item=item), self.assertRaises(ValueError):
                self.merge([[valid], [item]])

    def test_source_count_and_missing_label(self):
        for sources in [None, [], [[region([[1]])]], [[]] * 33,
                        [[region([[1]])], []], [[region([[1]])], [None]]]:
            with self.subTest(sources=sources), self.assertRaises(ValueError):
                self.merge(sources)


if __name__ == "__main__":
    unittest.main()
