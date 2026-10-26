import unittest
import numpy as np
from .learning import update, predict


class LearningTests(unittest.TestCase):
    def test_roundtrip_and_incremental_learning(self):
        image = np.full((64, 64, 3), 220, np.uint8)
        image[:, 24:32] = 25
        mask = np.zeros((64, 64), np.uint8)
        mask[:, 24:32] = 1
        state = update(None, image, mask)
        self.assertEqual(state['round'], 1)
        result = predict(state, image)
        self.assertGreater(np.mean((result > 0) == (mask > 0)), .98)
        second = update(state, image, mask)
        self.assertEqual(second['round'], 2)
        self.assertEqual(second['1']['n'], 2 * state['1']['n'])
        large = np.tile(image, (5, 2, 1))
        self.assertEqual(predict(second, large).shape, (320, 128))

    def test_invalid_reference_and_untrained_model(self):
        image = np.zeros((64, 64, 3), np.uint8)
        with self.assertRaises(ValueError):
            update(None, image, np.zeros((64, 64)))
        with self.assertRaises(ValueError):
            predict(None, image)
