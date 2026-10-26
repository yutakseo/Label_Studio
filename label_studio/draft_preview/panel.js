(() => {
  function decodeRLE(rle) {
    let bit = 0;
    const read = n => {
      if (bit + n > rle.length * 8) throw new Error('마스크 데이터가 잘렸습니다.');
      let v = 0;
      for (let i = 0; i < n; i++, bit++) v = v * 2 + ((rle[bit >> 3] >> (7 - (bit & 7))) & 1);
      return v;
    };
    const size = read(32), word = read(5) + 1, runs = [read(4)+1,read(4)+1,read(4)+1,read(4)+1];
    if (size > 64000000) throw new Error('미리보기 가능한 마스크 크기를 초과했습니다.');
    const out = new Uint8Array(size);
    let i = 0;
    while (i < size) {
      const repeat = read(1), end = i + 1 + read(runs[read(2)]);
      if (end > size) throw new Error('마스크 길이가 잘못되었습니다.');
      if (repeat) { out.fill(read(word), i, end); i = end; }
      else while (i < end) out[i++] = read(word);
    }
    return out;
  }
  if (typeof module !== 'undefined') module.exports = {decodeRLE};
  if (typeof document === 'undefined') return;
  const button = document.createElement('button');
  button.id = 'draft-preview-launch';
  button.textContent = '자동 저장 초안 보기';
  button.style.cssText = 'position:fixed;right:24px;bottom:24px;z-index:9999;padding:10px 16px;background:#384b92;color:white;border:1px solid #879bff;border-radius:6px';
  const dialog = document.createElement('dialog');
  dialog.style.cssText = 'width:min(1000px,90vw);max-height:90vh;overflow:auto;background:#242424;color:#eee;border:1px solid #888;border-radius:8px';
  dialog.innerHTML = '<h2>자동 저장된 라벨러 초안</h2><p>아직 제출되지 않은 작업입니다.</p><select aria-label="라벨러 초안"></select> <button data-close>닫기</button><p role="status"></p><div style="position:relative"><img data-source style="display:block;width:100%"><canvas style="position:absolute;inset:0;width:100%;height:100%;pointer-events:none"></canvas></div>';
  document.body.append(button, dialog);
  const select = dialog.querySelector('select'), status = dialog.querySelector('[role=status]');
  const image = dialog.querySelector('img'), canvas = dialog.querySelector('canvas');
  dialog.querySelector('[data-close]').onclick = () => dialog.close();
  let drafts = [], generation = 0;
  const api = async url => {
    const response = await fetch(url, {credentials:'same-origin'});
    if (!response.ok) throw new Error(`불러오기 실패 (${response.status})`);
    return response.json();
  };
  function showDraft() {
    const draft = drafts[Number(select.value)];
    if (!draft) return;
    const regions = draft.result.filter(r => r.type === 'brushlabels' && r.value?.rle);
    if (!regions.length) { status.textContent = '이 초안에는 표시할 브러시 마스크가 없습니다.';canvas.width=1;canvas.height=1;return; }
    canvas.width = regions[0].original_width; canvas.height = regions[0].original_height;
    const ctx = canvas.getContext('2d');
    const colors = [[255,77,79],[22,119,255],[250,173,20]];
    const labels = new Map();
    try {
      for (const region of regions) {
        if (region.original_width !== canvas.width || region.original_height !== canvas.height || (region.image_rotation || 0)) throw new Error('회전 또는 서로 다른 크기의 마스크 미리보기는 지원하지 않습니다.');
        const mask = decodeRLE(region.value.rle);
        if (mask.length !== canvas.width*canvas.height*4) throw new Error('마스크와 이미지 크기가 다릅니다.');
        const label = (region.value.brushlabels || []).join(', ');
        if (!labels.has(label)) labels.set(label, colors[labels.size%colors.length]);
        const color = labels.get(label), data = ctx.createImageData(canvas.width,canvas.height);
        for (let p=0;p<mask.length;p+=4) { data.data.set(color,p);data.data[p+3]=Math.round(mask[p+3]*0.5); }
        const layer=document.createElement('canvas');layer.width=canvas.width;layer.height=canvas.height;
        layer.getContext('2d').putImageData(data,0,0);ctx.drawImage(layer,0,0);
      }
      status.textContent = `작업 ${new URL(location.href).searchParams.get('task')} · ${draft.created_username || draft.user} · 자동 저장 ${new Date(draft.updated_at).toLocaleString('ko-KR')} · ${[...labels.keys()].join(', ')} · 미제출`;
    } catch(error) { status.textContent=error.message; }
  }
  select.onchange = showDraft;
  button.onclick = async () => {
    const id = new URL(location.href).searchParams.get('task');
    if (!id || !/^\d+$/.test(id)) { button.textContent='작업을 먼저 선택하세요';return; }
    const current = ++generation;
    if (!dialog.open) dialog.showModal();
    status.textContent='자동 저장된 초안을 불러오는 중…';select.replaceChildren();image.removeAttribute('src');canvas.width=1;canvas.height=1;
    try {
      const [task, response] = await Promise.all([api(`/api/tasks/${id}/`),api(`/api/tasks/${id}/drafts`)]);
      if (current !== generation) return;
      drafts = (Array.isArray(response)?response:response.results||[]).sort((a,b)=>new Date(b.updated_at)-new Date(a.updated_at));
      if (!drafts.length) { status.textContent='이 작업에는 자동 저장된 초안이 없습니다.';return; }
      select.replaceChildren(...drafts.map((d,i)=>new Option(`${d.created_username||d.user} · ${new Date(d.updated_at).toLocaleString('ko-KR')}`,String(i))));
      const region=drafts.flatMap(d=>d.result).find(r=>r.type==='brushlabels');
      const project=await api(`/api/projects/${task.project}/`);
      if (current !== generation) return;
      const config=new DOMParser().parseFromString(project.label_config,'text/xml');
      const tag=[...config.querySelectorAll('Image')].find(t=>t.getAttribute('name')===region?.to_name);
      const url=task.data[tag?.getAttribute('value')?.replace(/^\$/,'')];
      if (!url) throw new Error('초안의 원본 이미지 경로를 찾을 수 없습니다.');
      const resolved=new URL(url,location.href);
      if (!['http:','https:'].includes(resolved.protocol)) throw new Error('지원하지 않는 이미지 주소입니다.');
      image.src=resolved.href;image.onerror=()=>{status.textContent='원본 이미지를 불러올 수 없습니다.';};
      showDraft();
    } catch(error) { if (current===generation)status.textContent=error.message; }
  };
})();

/* Saved annotation attribution, including imported masks without an author. */
(() => {
  function person(value, users) {
    if (value == null) return null;
    const user = typeof value === 'object' ? value : users.get(Number(value));
    if (!user) return `사용자 #${value}`;
    return user.username || [user.first_name, user.last_name].filter(Boolean).join(' ') || user.email || `사용자 #${user.id}`;
  }
  function attribution(annotation, users) {
    const author = person(annotation.completed_by, users);
    const editor = person(annotation.updated_by, users);
    const parts = [`작성자: ${author || '미지정 (가져온 라벨)'}`];
    if (editor) parts.push(`마지막 저장: ${editor}`);
    if (annotation.updated_at) parts.push(new Date(annotation.updated_at).toLocaleString('ko-KR'));
    return parts.join(' · ');
  }
  function tabIdentity(annotation, model, currentUser, drafts, users) {
    const mergeName = annotation.merge_name === 'MERGE' ? 'MERGE' : null;
    const ownerId = annotation.completed_by?.id ?? annotation.completed_by;
    const currentId = currentUser?.id ?? currentUser;
    const own = ownerId != null && currentId != null && String(ownerId) === String(currentId);
    const changed = model?.isDrawing || (model?.history?.hasChanges && model.history.undoIdx > 0);
    if (model?.selected && own && changed && currentUser) {
      return {name: mergeName || person(currentUser.id ?? currentUser, users), role: 'editing', label: '작업 중'};
    }
    const draft = drafts.find(d => String(d.annotation) === String(annotation.id)
      && JSON.stringify(d.result) !== JSON.stringify(annotation.result));
    if (model?.selected && own && draft) {
      const owner = typeof draft.user === 'object' || /^\d+$/.test(String(draft.user))
        ? person(draft.user, users) : person([...users.values()].find(u => u.email === draft.user || u.username === draft.user), users) || String(draft.user);
      return {name: mergeName || owner, role: 'draft', label: '미제출 초안'};
    }
    const author = person(annotation.completed_by, users);
    return {name: mergeName || author || '가져온 라벨', role: mergeName ? 'merge' : author ? 'author' : 'imported', label: own ? '' : '원본 보존'};
  }
  if (typeof module !== 'undefined') Object.assign(module.exports, {person, attribution, tabIdentity});
  if (typeof document === 'undefined') return;
  let users = new Map(), usersLoaded = false, annotations = [], drafts = [], taskId = null;
  let refreshAt = 0, pending = false, generation = 0, submitting = false;
  const api = async url => {
    const response = await fetch(url, {credentials: 'same-origin'});
    if (!response.ok) throw new Error(`작업자 정보 불러오기 실패 (${response.status})`);
    return response.json();
  };
  function syncTabs() {
    const byId = new Map(annotations.map(a => [String(a.id), a]));
    for (const tab of document.querySelectorAll('[data-annotation-id]')) {
      const annotation = byId.get(tab.getAttribute('data-annotation-id'));
      const name = tab.querySelector('.lsf-annotation-button__name');
      if (!annotation || !name) continue;
      const store = window.Htx;
      const model = store?.annotationStore?.annotations?.find(a => String(a.pk) === String(annotation.id));
      if (annotation.updated_at && model?.setModifiedDate && model.modifiedDate !== annotation.updated_at) {
        model.setModifiedDate(annotation.updated_at);
      }
      const identity = tabIdentity(annotation, model, store?.user, drafts, users);
      if (name.textContent !== identity.name) name.textContent = identity.name;
      name.title = identity.label ? `${identity.name} · ${identity.label}` : attribution(annotation, users);
      name.dataset.attributionRole = identity.role;
      const info = tab.querySelector('.lsf-annotation-button__info');
      let badge = tab.querySelector('[data-working-user-label]');
      if (identity.label && info) {
        if (!badge) {
          badge = document.createElement('span');
          badge.dataset.workingUserLabel = '';
          info.append(badge);
        }
        badge.textContent = ` · ${identity.label}`;
      } else badge?.remove();
      tab.querySelector('[data-last-editor-label]')?.remove();
    }
  }
  async function refresh(id) {
    if (pending) return;
    pending = true;
    const current = generation;
    refreshAt = Date.now() + 15000;
    try {
      const [task, people] = await Promise.all([
        api(`/api/tasks/${id}/`),
        usersLoaded ? Promise.resolve(null) : api('/api/users/'),
      ]);
      if (current !== generation) return;
      if (people) {
        users = new Map((Array.isArray(people) ? people : people.results || []).map(u => [u.id, u]));
        usersLoaded = true;
      }
      annotations = (task.annotations || []).map(a => ({...a,
        merge_name:task.meta?.mask_merge_annotations?.[a.id]?.name}));
      globalThis.__labelStudioMergeTabIds = new Set(annotations.filter(a=>a.merge_name === 'MERGE').map(a=>String(a.id)));
      drafts = task.drafts || [];
      syncTabs();
    } catch {
      // Retry metadata on the next refresh without adding a layout element.
    } finally {
      pending = false;
    }
  }
  function update() {
    const store = window.Htx, selection = store?.annotationStore?.selected;
    const id = new URL(location.href).searchParams.get('task');
    const image = selection?.names && [...selection.names.values()].find(n => n.type === 'image' && n.containerRef);
    if (!/^\d+$/.test(id || '') || !image?.containerRef?.isConnected) {
      if (taskId !== null) { taskId = null; generation++; }
      return;
    }
    syncTabs();
    const changedTask = id !== taskId;
    if (changedTask) {
      taskId = id;
      generation++;
      annotations = [];
      drafts = [];
      refreshAt = 0;
    }
    const saved = submitting && !store.isSubmitting;
    submitting = !!store.isSubmitting;
    if (!document.hidden && (saved || Date.now() >= refreshAt)) refresh(id);
  }
  document.addEventListener('label-studio:annotation-saved', () => {
    refreshAt = 0;
  });
  setInterval(update, 1000);
  update();
})();
