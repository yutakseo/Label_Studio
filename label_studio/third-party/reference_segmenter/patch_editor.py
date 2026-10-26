"""Version-checked native dark-line action registration."""
from pathlib import Path
import argparse

START = '/* DARK_LINE_TOOL_START */'
END = '/* DARK_LINE_TOOL_END */'


def patch(source):
    source = source.replace("Delete Black line", "Delete Reference Segmenter").replace(
        '["Black line","검은 줄","검은줄"]', '["Reference Segmenter","Black line","검은 줄","검은줄"]')
    menu = ('{label:"Delete Reference Segmenter",onClick:()=>{if(window.DarkLine)window.DarkLine.deletePrediction(e.pk);'
            'else window.alert("새로고침 후 다시 실행하세요.")},icon:(0,se.jsx)(wn.Wus,{}),'
            'separator:!0,danger:!0,enabled:T&&["Reference Segmenter","Black line","검은 줄","검은줄"].includes(e.createdBy)},')
    anchor = '{label:"Delete Annotation",onClick:j,'
    if menu not in source:
        if source.count(anchor) != 1:
            raise ValueError('Unsupported prediction tab menu anchor')
        source = source.replace(anchor, menu + anchor, 1)
    guard = 'if(document.querySelector("#dark-line-dialog[open]"))return!1;'
    if guard not in source:
        anchor = 'kn().filter=e=>{var t;'
        if source.count(anchor) != 1:
            raise ValueError('Unsupported editor hotkey filter')
        source = source.replace(anchor, anchor + guard, 1)
    replacement = START + Path(__file__).with_suffix('.js').read_text().strip() + END
    if START in source:
        start, end = source.index(START), source.index(END) + len(END)
        return source[:start] + replacement + source[end:]
    for old, new in [
        ('MaskMerge:()=>MaskMergeTool,', 'MaskMerge:()=>MaskMergeTool,DarkLine:()=>DarkLineTool,'),
        ('/* MASK_MERGE_TOOL_END */,Sc=', '/* MASK_MERGE_TOOL_END */,DarkLineTool=' + replacement + ',Sc='),
        ('toolNames:["Brush","Erase","SimilarErase","GaussianMask","MaskMerge"]',
         'toolNames:["Brush","Erase","SimilarErase","GaussianMask","MaskMerge","DarkLine"]'),
    ]:
        if source.count(old) != 1:
            raise ValueError(f'Unsupported dark-line toolbar anchor: {old}')
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
