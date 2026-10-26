"""Reference segmentation has a fixed 64x64 input/output contract."""
from u_net_labeller.model import UNet


class ReferenceUNet(UNet):
    """Keep existing state-dict keys while rejecting all other spatial sizes."""
    def forward(self, x):
        if x.ndim != 4 or tuple(x.shape[1:]) != (1, 64, 64):
            raise ValueError('참조 U-Net 입력은 [N, 1, 64, 64]이어야 합니다.')
        output = super().forward(x)
        if tuple(output.shape) != (x.shape[0], 1, 64, 64):
            raise ValueError('참조 U-Net 출력은 [N, 1, 64, 64]이어야 합니다.')
        return output
