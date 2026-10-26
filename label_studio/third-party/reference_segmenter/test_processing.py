import unittest

import numpy as np
import cv2
from label_studio_sdk.converter.brush import decode_rle

from .processing import detect, brush_result


OPTIONS = {"blur_size": 51, "adaptive_size": 31, "min_contrast": 20, "offset": 3,
           "close_size": 5, "min_area": 20, "min_path_length": 60,
           "min_elongation": 5, "max_width": 20, "edge_margin": 0}


class DarkLineTests(unittest.TestCase):
    def image(self):
        gray = np.tile(np.linspace(150, 190, 320, dtype=np.uint8), (160, 1))
        gray[40:44, 30:290] = 60
        gray[40:44, 130:133] = 170  # A short break in the line.
        gray[80:83, 30:290] = 255  # A bright line must not become a dark line.
        gray[100:140, 80:83] = 60  # This short mark is below the path length cutoff.
        gray[110:113, 270:273] = 60
        return gray

    def test_dark_direction_gap_connection_and_shape_filters(self):
        gray = self.image(); original = gray.copy()
        mask, _, _, stats = detect(gray, OPTIONS)
        self.assertGreater(np.count_nonzero(mask[40:44, 40:280]), 800)
        self.assertTrue(np.all(mask[41:43, 130:133] == 255))
        self.assertFalse(mask[80:83, 40:280].any())
        self.assertFalse(mask[105:135, 80:83].any())
        self.assertFalse(mask[110:113, 270:273].any())
        self.assertEqual(stats["components"], 1)
        np.testing.assert_array_equal(gray, original)

    def test_tight_winding_curve_and_rotation_are_preserved(self):
        gray=np.full((180,180),170,dtype=np.uint8)
        truth=np.zeros_like(gray)
        # A tall S with a nearly square bounding box: horizontal aspect filters fail.
        points=np.array([[120,20],[65,20],[30,45],[30,65],[60,85],
                         [120,95],[145,115],[145,140],[110,160],[50,160]],np.int32)
        cv2.polylines(truth,[points],False,255,3)
        gray[truth>0]=45
        cv2.circle(gray,(80,125),8,45,-1)  # A compact dark spot must be rejected.
        for turns in range(4):
            image=np.rot90(gray,turns).copy();expected=np.rot90(truth,turns)
            mask,_,_,_=detect(image,{**OPTIONS,'max_width':10,'min_elongation':8})
            recall=np.count_nonzero((mask>0)&(expected>0))/np.count_nonzero(expected)
            self.assertGreater(recall,0.9, f'rotation={turns}')
            inverse=np.rot90(mask,-turns)
            self.assertFalse(inverse[120:130,75:85].any())

    def test_long_vertical_and_diagonal_curves_are_eligible(self):
        for points in ([[30,20],[35,60],[25,110],[30,160]], [[20,20],[60,45],[80,100],[150,155]]):
            gray=np.full((180,180),170,dtype=np.uint8);truth=np.zeros_like(gray)
            cv2.polylines(truth,[np.array(points,np.int32)],False,255,3);gray[truth>0]=45
            mask,_,_,_=detect(gray,OPTIONS)
            self.assertGreater(np.count_nonzero((mask>0)&(truth>0))/np.count_nonzero(truth),0.9)

    def test_roi_clips_output_and_preserves_original_resolution(self):
        mask, _, _, _ = detect(self.image(), OPTIONS, [50, 30, 150, 55])
        self.assertTrue(mask.any())
        self.assertEqual(mask.shape, (160, 320))
        outside=mask.copy();outside[30:55,50:150]=0
        self.assertFalse(outside.any())
        result=brush_result(mask, "brush", "image", "Exposure")[0]
        np.testing.assert_array_equal(decode_rle(result["value"]["rle"]).reshape(160,320,4)[:,:,3], mask)

    def test_black_padding_and_specimen_edges_are_not_lines(self):
        gray=np.zeros((160,320),dtype=np.uint8);gray[30:130,20:300]=160;gray[75:78,40:280]=50
        mask, _, _, _ = detect(gray, {**OPTIONS, "edge_margin":8})
        self.assertTrue(mask[75:78,50:270].any())
        self.assertFalse(mask[:40].any());self.assertFalse(mask[120:].any())
        self.assertFalse(mask[:,:30].any());self.assertFalse(mask[:,290:].any())

    def test_constant_and_black_images_are_empty(self):
        for value in (0, 160):
            mask, _, _, stats=detect(np.full((100,160),value,dtype=np.uint8),OPTIONS)
            self.assertFalse(mask.any());self.assertEqual(stats["pixels"],0)

    def test_invalid_options_and_regions(self):
        for options in ({"blur_size":20},{"adaptive_size":2},{"min_contrast":0},
                        {"min_elongation":float('nan')},{"close_size":10000},{"max_width":True}):
            with self.subTest(options=options),self.assertRaises(ValueError):detect(self.image(),options)
        for bbox in ([0,0,999,2],[4,4,4,5],[0.1,0,10,10],[]):
            with self.subTest(bbox=bbox),self.assertRaises(ValueError):detect(self.image(),OPTIONS,bbox)


if __name__ == '__main__':
    unittest.main()
