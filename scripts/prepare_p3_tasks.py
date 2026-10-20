"""Build editable Label Studio tasks from the P3 images and GT alpha masks."""
from pathlib import Path
import hashlib
import importlib.util
import json
from urllib.parse import quote

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / 'files/P3_72_with_masks'
spec = importlib.util.spec_from_file_location('ls_formatting', ROOT / '__pseudo_labeller/label_studio_formatting.py')
formatting = importlib.util.module_from_spec(spec)
spec.loader.exec_module(formatting)


def main():
    manifest = json.loads((DATASET / 'manifest.json').read_text())
    tiles = manifest['tiles']
    names = {tile['file'] for tile in tiles}
    assert len(names) == len(tiles) == manifest['captures']
    for folder in ('images', 'masks'):
        assert {p.name for p in (DATASET / folder).glob('*.png')} == names, folder
    tasks = []
    for tile in tiles:
        name = tile['file']
        image_path, mask_path = (DATASET / 'images' / name), (DATASET / 'masks' / name)
        for path, key in ((image_path, 'image_sha256'), (mask_path, 'mask_sha256')):
            assert hashlib.sha256(path.read_bytes()).hexdigest() == tile[key], path
        with Image.open(image_path) as image, Image.open(mask_path) as mask:
            assert image.size == mask.size == (256, 256), name
            # This export stores original GT alpha as a grayscale PNG.
            if 'A' in mask.getbands():
                values = np.asarray(mask.getchannel('A'))
            else:
                assert mask.mode == 'L', f'Unsupported mask mode: {name}: {mask.mode}'
                values = np.asarray(mask)
            binary = np.where(values > 0, 255, 0).astype(np.uint8)
            assert np.count_nonzero(binary) == tile['gt_label_pixels'], name
            width, height = image.size
        result = {
            'id': hashlib.sha256(name.encode()).hexdigest()[:10],
            'from_name': 'brush', 'to_name': 'image', 'type': 'brushlabels',
            'origin': 'manual', 'original_width': width, 'original_height': height,
            'image_rotation': 0,
            'value': {'format': 'rle', 'rle': formatting.encode_label_studio_rle(binary), 'brushlabels': ['Exposure']},
        }
        tasks.append({
            'data': {'image': '/data/local-files/?d=' + quote('files/P3_72_with_masks/images/' + name, safe='/')},
            'annotations': [{'result': [result]}],
        })
    (DATASET / 'tasks.json').write_text(json.dumps(tasks, ensure_ascii=False, separators=(',', ':')) + '\n')
    (DATASET / 'label_config.xml').write_text(
        '<View>\n  <Image name="image" value="$image"/>\n'
        '  <BrushLabels name="brush" toName="image">\n'
        '    <Label value="Exposure"/>\n  </BrushLabels>\n</View>\n'
    )
    print(f'Created {len(tasks)} editable tasks: {DATASET / "tasks.json"}')


if __name__ == '__main__':
    main()
