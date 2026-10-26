"""Register the merge action beside the native segmentation tools."""
from pathlib import Path
import argparse

START = '/* MASK_MERGE_TOOL_START */'
END = '/* MASK_MERGE_TOOL_END */'


def patch(source):
    guard = 'if(document.querySelector("#mask-merge-dialog[open]"))return!1;'
    if guard not in source:
        anchor = 'kn().filter=e=>{var t;'
        if source.count(anchor) != 1:
            raise ValueError('Unsupported editor hotkey filter')
        source = source.replace(anchor, anchor + guard, 1)
    tool = Path(__file__).with_suffix('.js').read_text().strip()
    replacement = START + tool + END
    if START in source:
        start, end = source.index(START), source.index(END) + len(END)
        return source[:start] + replacement + source[end:]
    changes = [
        ('GaussianMask:()=>MaskCleanupGaussianTool,',
         'GaussianMask:()=>MaskCleanupGaussianTool,MaskMerge:()=>MaskMergeTool,'),
        ('/* GAUSSIAN_TOOL_END */,Sc=',
         '/* GAUSSIAN_TOOL_END */,MaskMergeTool=' + replacement + ',Sc='),
        ('toolNames:["Brush","Erase","SimilarErase","GaussianMask"]',
         'toolNames:["Brush","Erase","SimilarErase","GaussianMask","MaskMerge"]'),
    ]
    for old, new in changes:
        if source.count(old) != 1:
            raise ValueError(f'Unsupported editor merge tool anchor: {old}')
        source = source.replace(old, new, 1)
    return source


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('bundle', type=Path)
    args = parser.parse_args()
    source = args.bundle.read_text()
    result = patch(source)
    if result != source:
        args.bundle.write_text(result)
