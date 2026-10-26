/* Keep original author tabs read-only and edit in the signed-in user's tab. */
globalThis.__labelStudioCanEditAnnotation = function(store, annotation) {
  const userId = store.store?.user?.id;
  const ownerId = annotation.user?.id ?? annotation.completed_by?.id ?? annotation.completed_by;
  return userId != null && ownerId != null && String(userId) === String(ownerId);
};
globalThis.__labelStudioForkOnUpdate = function(app) {
  const store = app.annotationStore, source = store.selected;
  if (!source?.pk || source.type !== 'annotation' || app.hasInterface('review')
      || source.readonly || globalThis.__labelStudioCanEditAnnotation(store, source)) return false;
  source.beforeSend();
  if (!source.validate()) return true;
  const result = source.serializeAnnotation();
  const original = structuredClone(source.versions.result || []);
  source.pauseAutosave();
  app.setFlags({isSubmitting:true});
  (async () => {
    try {
      // Let an in-flight autosave finish before transferring its draft ID.
      await app.waitForDraftSubmission();
      const existing = store.annotations.find(a=>a.pk && a.type==='annotation'
        && globalThis.__labelStudioCanEditAnnotation(store,a)
        && !globalThis.__labelStudioMergeTabIds?.has(String(a.pk)));
      const own = existing || store.addAnnotationFromPrediction({_initialAnnotationObj:result,pk:source.pk,type:source.type});
      if (existing) {
        existing.pauseAutosave();
        existing.deleteAllRegions({deleteReadOnly:true});
        existing.deserializeResults(result);
        existing.reinitHistory();
      }
      if (source.draftId) own.setDraftId(source.draftId);
      source.dropDraft();
      source.deleteAllRegions({deleteReadOnly:true});
      source.deserializeResults(original);
      source.reinitHistory();
      source.resetSubmission();
      source.startAutosave();
      store.selectAnnotation(own.id,{exitViewAll:true});
      app.setFlags({isSubmitting:false});
      own.submissionInProgress();
      if (existing) {own.startAutosave(); app.updateAnnotation();}
      else app.submitAnnotation();
    } catch (error) {
      app.setFlags({isSubmitting:false});
      source.resetSubmission();
      source.startAutosave();
      console.error(error);
      window.alert('저장하지 못했습니다. 작업 탭의 마스크를 확인한 뒤 다시 저장해 주세요.');
    }
  })();
  return true;
};
// Match ZIP export selection using saved timestamps, never draft autosave times.
globalThis.__labelStudioLatestSavedTab = function(store, records) {
  const candidates = records.filter(record => (record.id ?? record.pk) != null && !record.was_cancelled)
    .map(record => ({record, time: Date.parse(record.updated_at || record.created_at || '') || 0}))
    .sort((a,b) => b.time-a.time || Number(b.record.id ?? b.record.pk)-Number(a.record.id ?? a.record.pk));
  for (const {record} of candidates) {
    const tab = store.annotations.find(tab => String(tab.pk) === String(record.id ?? record.pk));
    if (tab) return tab;
  }
  return undefined;
};
globalThis.__labelStudioLatestTaskTab = async function(store, task) {
  let records = task.annotations || [];
  // Data Manager sends stubs without updated_at; use the same saved data as export.
  if (records.some(record => !record.updated_at)) {
    try {
      const response = await fetch(`/api/tasks/${task.id}/`, {credentials:'same-origin', cache:'no-store'});
      if (response.ok) records = (await response.json()).annotations || [];
    } catch (error) { console.error('Could not load latest saved annotation', error); }
  }
  return globalThis.__labelStudioLatestSavedTab(store, records);
};
globalThis.__labelStudioSortTabs = function(tabs) {
  const timestamp = tab => {
    const date = Date.parse(tab.modifiedDate || tab.createdDate || '');
    const draft = Date.parse(tab.draftSaved || '');
    return Math.max(Number.isFinite(date) ? date : 0, Number.isFinite(draft) ? draft : 0);
  };
  return tabs.map((tab,index) => ({tab,index,time:timestamp(tab)}))
    .sort((a,b) => a.time-b.time || (Number(a.tab.pk)||0)-(Number(b.tab.pk)||0) || a.index-b.index)
    .map(item => item.tab);
};
globalThis.__labelStudioCopyToUserTab = function(store, source) {
  const own = store.annotations.find(a=>a.pk && a.type==='annotation'
    && globalThis.__labelStudioCanEditAnnotation(store,a)
    && !globalThis.__labelStudioMergeTabIds?.has(String(a.pk)));
  if (!own) return store.addAnnotationFromPrediction(source);
  own.pauseAutosave();
  own.deleteAllRegions({deleteReadOnly:true});
  own.deserializeResults(source.serializeAnnotation());
  own.startAutosave();
  return own;
};
globalThis.__labelStudioAnnotationSaved = function() {
  document.dispatchEvent(new Event('label-studio:annotation-saved'));
};
/* End per-user update fork. */
