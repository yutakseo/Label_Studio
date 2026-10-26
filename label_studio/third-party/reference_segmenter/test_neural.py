import tempfile
import unittest
from pathlib import Path
import numpy as np
import torch
from . import neural


class NeuralTests(unittest.TestCase):
    def test_correction_training_checkpoint_and_inference(self):
        rgb=np.full((64,64,3),180,np.uint8)
        rgb[:,24:32]=40
        mask=np.zeros((64,64),np.uint8);mask[:,24:32]=1
        with tempfile.TemporaryDirectory() as name:
            directory=Path(name)
            neural.save_pair(directory/'pairs',rgb,mask,'correction')
            pairs=neural.read_pairs(directory/'pairs')
            self.assertTrue(np.array_equal(pairs[0][1],mask))
            checkpoint=directory/'model.pt'
            info=neural.train(checkpoint,pairs,steps=2,batch_size=2)
            self.assertEqual(info['steps'],2)
            self.assertGreater(info['parameters'],1_000_000)
            model,_=neural.load(checkpoint)
            with torch.no_grad():
                self.assertEqual(tuple(model(torch.zeros(1,1,64,64,device=neural.device())).shape),(1,1,64,64))
            predicted=neural.predict(checkpoint,rgb)
            self.assertEqual(predicted.shape,mask.shape)
            self.assertTrue(set(np.unique(predicted)).issubset({0,255}))
            neural.train(checkpoint,pairs,steps=1,batch_size=2)
            self.assertTrue(checkpoint.with_suffix('.previous.pt').exists())
            _,updated=neural.load(checkpoint)
            self.assertEqual(updated['steps'],3)


    def test_random_initialization_does_not_load_existing_weights(self):
        from unittest.mock import patch
        rgb=np.full((64,64,3),120,np.uint8)
        mask=np.zeros((64,64),np.uint8);mask[:,20:30]=1
        validation_rgb=np.tile(rgb,(4,4,1));validation_mask=np.tile(mask,(4,4))
        with tempfile.TemporaryDirectory() as name:
            checkpoint=Path(name)/'scratch.pt'
            with patch.object(neural,'load',side_effect=AssertionError('must not load existing weights')):
                info=neural.train(checkpoint,[(rgb,mask)],steps=2,batch_size=2,start_from_scratch=True,
                                  validation_pairs=[(validation_rgb,validation_mask)],validation_interval=2)
            self.assertEqual(info['initialization'],'random')
            self.assertEqual(info['steps'],2)
            self.assertEqual(info['selected_step'],2)
            self.assertEqual(len(info['validation_history']),1)
            _,metadata=neural.load(checkpoint)
            self.assertEqual(metadata['initialization'],'random')

    def test_full_images_cannot_enter_training(self):
        with tempfile.TemporaryDirectory() as name:
            with self.assertRaisesRegex(ValueError,'64×64'):
                neural.train(Path(name)/'model.pt',[(np.zeros((256,256,3),np.uint8),np.zeros((256,256),np.uint8))],steps=1)

    def test_64_pixel_tiles_reconstruct_odd_and_small_images_without_seams(self):
        class PixelModel(torch.nn.Module):
            def __init__(self):
                super().__init__();self.shapes=[]
            def forward(self,inputs):
                self.shapes.append(tuple(inputs.shape))
                assert tuple(inputs.shape[-2:])==(64,64)
                return (inputs-.5)*20
        rng=np.random.default_rng(9)
        for h,w in [(73,131),(1,9),(64,64)]:
            gray=rng.integers(1,256,(h,w),dtype=np.uint8)
            rgb=np.repeat(gray[:,:,None],3,axis=2)
            model=PixelModel()
            actual=neural.predict_tiled(model,rgb,batch_size=3)
            expected=(gray>=128).astype(np.uint8)*255
            self.assertEqual(actual.shape,(h,w))
            self.assertTrue(np.array_equal(actual,expected))
            self.assertTrue(model.shapes)
        model=PixelModel()
        self.assertFalse(neural.predict_tiled(model,np.zeros((71,89,3),np.uint8)).any())
        self.assertFalse(model.shapes)


    def test_reference_model_rejects_256_input_before_convolution(self):
        from .model import ReferenceUNet
        from unittest.mock import patch
        model=ReferenceUNet(32)
        with patch.object(model.encoders[0], 'forward', side_effect=AssertionError('invalid input reached convolution')):
            for shape in [(1,1,256,256),(1,1,64,256),(1,3,64,64),(1,64,64)]:
                with self.assertRaisesRegex(ValueError,'64, 64'):
                    model(torch.zeros(shape))
        with torch.inference_mode():
            self.assertEqual(tuple(model(torch.zeros(2,1,64,64)).shape),(2,1,64,64))
