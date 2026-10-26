"""Fork another annotator's local working result only when Update is pressed."""
from pathlib import Path
import argparse

OLD = 'return!e.viewingAll||o.exitViewAll?r.editable=!0:r.editable=!1,r.setupHotKeys()'
READ_ONLY = 'return!e.viewingAll||o.exitViewAll?r.editable=globalThis.__labelStudioCanEditAnnotation(e,r):r.editable=!1,r.setupHotKeys()'
MARKER = '/* Keep original author tabs read-only and edit in the signed-in user\'s tab. */'
HOOKS = [
    ('const e=r.annotations.at(-1),t=!e&&r.predictions.at(-1);',
     'const e=globalThis.__labelStudioLatestSavedTab(r,[...i,...n])||r.annotations.at(-1),t=!e&&r.predictions.at(-1);'),
    ('const t=r.annotations.at(-1);t&&t.setInitialValues(),e.setHistory(s)',
     'const t=globalThis.__labelStudioLatestSavedTab(r,[...i,...n])||r.annotations.at(-1);t&&(r.selectAnnotation(t.id),t.setInitialValues()),e.setHistory(s)'),
    ('date:e.createdDate}),l&&',
     'date:e.modifiedDate||e.createdDate}),l&&'),
    ('lastUpdated:e.createdDate,annotationId:',
     'lastUpdated:e.modifiedDate||e.createdDate,annotationId:'),
    ('await(0,u._$)(e).events.invoke("updateAnnotation",e,n,t),e.incrementQueuePosition()',
     'await(0,u._$)(e).events.invoke("updateAnnotation",e,n,t),globalThis.__labelStudioAnnotationSaved(),e.incrementQueuePosition()'),
    ('await(0,u._$)(e).events.invoke(n,e,t),e.incrementQueuePosition()',
     'await(0,u._$)(e).events.invoke(n,e,t),globalThis.__labelStudioAnnotationSaved(),e.incrementQueuePosition()'),
    ('const t=r.addAnnotationFromPrediction(e);window.setTimeout',
     'const t=globalThis.__labelStudioCopyToUserTab(r,e);window.setTimeout'),
    ('[null==(i=t.selected)?void 0:i.id,T]),(0,p.useEffect)(()=>{const e=[];',
     '[null==(i=t.selected)?void 0:i.id,T,R]),(0,p.useEffect)(()=>{const e=[];'),
    ('createdDate:u.gK.optional(u.gK.string,Jt.UDate.currentISODate()),createdAgo:',
     'createdDate:u.gK.optional(u.gK.string,Jt.UDate.currentISODate()),modifiedDate:u.gK.maybeNull(u.gK.string),createdAgo:'),
    ('createdDate:(u=e,null!=',
     'modifiedDate:e.updated_at||e.modifiedDate||e.created_at||e.createdDate,createdDate:(u=e,null!='),
    ('setDraftSaved(t){e.draftSaved=t},afterAttach()',
     'setDraftSaved(t){e.draftSaved=t},setModifiedDate(t){e.modifiedDate=t},afterAttach()'),
    ('R=(0,p.useMemo)(()=>(0,M.sortAnnotations)(o),[o]),j=204*R.length',
     'R=(0,p.useMemo)(()=>globalThis.__labelStudioSortTabs(o),[o,JSON.stringify(o.map(e=>[e.modifiedDate,e.draftSaved]))]),j=204*R.length'),
    ('submissionInProgress(){e.submissionStarted=Date.now()},saveDraftImmediately',
     'submissionInProgress(){e.submissionStarted=Date.now()},resetSubmission(){e.submissionStarted=0},saveDraftImmediately'),
    ('updateAnnotation:function(t){if(e.isSubmitting)return;const n=e.annotationStore.selected;',
     'updateAnnotation:function(t){if(e.isSubmitting)return;if(globalThis.__labelStudioForkOnUpdate(e))return;const n=e.annotationStore.selected;'),
    ('submitAnnotation:function(){if(e.isSubmitting)return;const t=e.annotationStore.selected,',
     'submitAnnotation:function(){if(e.isSubmitting)return;if(globalThis.__labelStudioForkOnUpdate(e))return;const t=e.annotationStore.selected,'),
]


def patch(source):
    if READ_ONLY in source:
        source = source.replace(READ_ONLY, OLD)
    if source.count(OLD) != 1:
        raise ValueError('Unsupported annotation selection anchor')
    source = source.replace(
        'if(e.annotation.isReadOnly()){globalThis.__labelStudioSelectForkLabel(e);return}if(t.length>0&&0===n.length)return;',
        'if(e.annotation.isReadOnly())return;if(t.length>0&&0===n.length)return;')
    for old, new in HOOKS:
        if new not in source:
            if source.count(old) != 1:
                raise ValueError('Unsupported annotation save anchor')
            source = source.replace(old, new)
    helper = Path(__file__).with_suffix('.js').read_text()
    start = source.find(MARKER)
    if start >= 0:
        ends = ['/* End per-user update fork. */', '/* End per-user stroke handoff. */']
        marker = next((m for m in ends if m in source[start:]), None)
        if marker:
            end = source.index(marker, start) + len(marker)
        else:
            legacy = source.find('globalThis.__labelStudioOwnTab', start)
            end = source.find('\n};', legacy if legacy >= 0 else start + len(MARKER))
            if end < 0:
                raise ValueError('Unterminated user tab helper')
            end += len('\n};')
        source = source[:start] + source[end:].lstrip('\n')
    if helper not in source:
        source = helper + '\n' + source
    return source


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('bundle', type=Path)
    path = parser.parse_args().bundle
    original = path.read_text()
    updated = patch(original)
    if updated != original:
        path.write_text(updated)
