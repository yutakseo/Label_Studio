(() => {
  function hasMask(source, target) {
    return (source.result || []).some(r => r.type === 'brushlabels'
      && r.from_name === target.from_name && r.to_name === target.to_name
      && r.value?.format === 'rle' && (target.label == null ? r.value?.brushlabels?.length > 0 : r.value?.brushlabels?.includes(target.label)));
  }
  function sourceTitle(source) {
    if (source.kind === 'prediction') return `${source.model_version || '예측'} · #${source.id}`;
    if (source.merge_name === 'MERGE') return `MERGE · 라벨 #${source.id}`;
    const author = source.completed_by;
    const name = author && typeof author === 'object'
      ? author.username || [author.first_name, author.last_name].filter(Boolean).join(' ') || author.email || `사용자 #${author.id}`
      : author ? `사용자 #${author}` : '가져온 라벨';
    return `${name} · 라벨 #${source.id}`;
  }
  if (typeof module !== 'undefined') module.exports = {hasMask, sourceTitle};
  if (typeof document === 'undefined' || document.getElementById('mask-merge-dialog')) return;
  document.getElementById('mask-merge-launch')?.remove();
  const launch = document.createElement('button');
  launch.id = 'mask-merge-launch'; launch.textContent = '마스크 합치기';
  const dialog = document.createElement('dialog');
  dialog.id = 'mask-merge-dialog'; dialog.setAttribute('aria-label', '마스크 합치기');
  dialog.style.cssText = 'position:fixed;inset:0;margin:auto;width:min(1000px,94vw);height:min(760px,92dvh);padding:0;overflow:hidden;border:1px solid #888;border-radius:12px;background:var(--color-neutral-background,#242424);color:var(--color-neutral-content,#eee)';
  const host = document.createElement('div');
  host.style.cssText = 'height:100%;width:100%'; dialog.append(host);
  const root = host.attachShadow({mode:'open'});
  root.innerHTML = `<style>
    :host{font:14px/1.5 system-ui,sans-serif}*{box-sizing:border-box}[hidden]{display:none!important}
    .layout{display:flex;flex-direction:column;height:100%}header,footer{padding:18px 22px;flex-shrink:0}header{border-bottom:1px solid #8885}h2{margin:0 0 8px;font-size:22px}p{margin:0}main{display:grid;grid-template-columns:300px 1fr;min-height:0;flex:1;overflow:auto}
    aside{padding:20px;border-right:1px solid #8885;overflow:auto}.field{display:block;margin-bottom:10px}select{width:100%;padding:8px}select,button{font:inherit;background:var(--color-neutral-background,#242424);color:inherit;border:1px solid #888;border-radius:5px}
    button{padding:8px 14px;cursor:pointer}button:disabled{opacity:.5;cursor:default}button:focus-visible,select:focus-visible,input:focus-visible{outline:2px solid #879bff;outline-offset:2px}.primary{background:#384b92;color:white}
    .sources label{display:flex;gap:10px;align-items:flex-start;padding:12px 0;border-bottom:1px solid #8883;cursor:pointer;overflow-wrap:anywhere}.sources input{flex:none;margin-top:4px}.sources small{display:block;opacity:.7}
    .hint{font-size:12px;opacity:.8;margin:12px 0}.preview{padding:20px;display:flex;flex-direction:column;min-width:0;gap:12px}.stage{position:relative;flex:1;min-height:240px;background:#111;border-radius:6px;overflow:hidden}.stage img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain}.placeholder{padding:30px;color:#bbb}.stage.show .placeholder{display:none}.stage:not(.show) img{display:none}
    footer{border-top:1px solid #8885;display:flex;gap:14px;align-items:center;justify-content:space-between}.actions{display:flex;gap:8px;flex-shrink:0}[role=status]{overflow-wrap:anywhere;font-size:13px}[role=status][data-error=true]{color:#ff7373}
    @media(max-width:700px){main{display:block}aside{border-right:0}.stage{height:300px}footer{align-items:stretch;flex-direction:column}.actions{justify-content:flex-end}}
  </style><div class="layout"><header><h2>마스크 합치기</h2><p>선택한 탭의 마스크를 라벨별로 합쳐 새 라벨 탭에 저장합니다.</p></header>
  <main><aside><label class="field" for="merge-target">대상 이미지 · 라벨</label><select id="merge-target"></select><p class="hint">저장된 라벨과 예측 중 2개 이상을 선택하세요. 편집 중인 내용은 먼저 저장한 뒤 이 창을 여세요.</p><div class="sources"></div></aside>
  <section class="preview"><strong>합친 마스크 미리보기</strong><div class="stage"><p class="placeholder">합칠 마스크를 선택하고 미리보기를 누르세요.</p><img data-original alt="원본 이미지"><img data-mask alt="합친 영역"></div><p data-stats class="hint"></p><p class="hint">모든 라벨 유지 시 같은 라벨끼리 합치며, 다른 라벨의 겹친 영역도 각각 유지합니다. 원본 탭은 유지되고, 결과는 MERGE라는 새 라벨 탭에 저장됩니다.</p></section></main>
  <footer><p role="status" aria-live="polite"></p><div class="actions"><button data-close>닫기</button><button data-preview>미리보기</button><button data-save class="primary" disabled>새 라벨로 저장</button></div></footer></div>`;
  document.body.append(dialog);
  const targetSelect = root.querySelector('select'), list = root.querySelector('.sources');
  const preview = root.querySelector('[data-preview]'), save = root.querySelector('[data-save]');
  const close = root.querySelector('[data-close]'), status = root.querySelector('[role=status]');
  const stage = root.querySelector('.stage'), original = root.querySelector('[data-original]');
  const overlay = root.querySelector('[data-mask]'), stats = root.querySelector('[data-stats]');
  let task, targets = [], sources = [], processed = null, snapshot = [], busy = false, saved = false;
  const csrf = () => decodeURIComponent(document.cookie.split('; ').find(v => v.startsWith('csrftoken='))?.slice(10) || '');
  const currentId = () => new URL(location.href).searchParams.get('task');
  function message(text, error = false) { status.textContent = text; status.dataset.error = String(error); }
  async function api(url, options = {}) {
    const response = await fetch(url, {credentials:'same-origin', ...options});
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || data.detail || `요청 실패 (${response.status})`);
    return data;
  }
  function allSources(data) {
    return [...(data.annotations || []).filter(a => !a.was_cancelled).map(a => ({...a, kind:'annotation',
      merge_name:data.meta?.mask_merge_annotations?.[a.id]?.name})),
      ...(data.predictions || []).map(p => ({...p, kind:'prediction'}))];
  }
  function selected() { return [...list.querySelectorAll('input:checked')].map(c => sources[Number(c.value)]); }
  function lock(value) {
    busy = value; dialog.setAttribute('aria-busy', String(value));
    for (const e of [launch, close, targetSelect, ...list.querySelectorAll('input')]) e.disabled = value;
    preview.disabled = value || selected().length < 2;
    save.disabled = value || !processed || saved;
  }
  function invalidate() {
    processed = null; snapshot = []; saved = false; stage.classList.remove('show');
    original.removeAttribute('src'); overlay.removeAttribute('src'); stats.textContent = '';
    save.textContent = '새 라벨로 저장'; lock(busy);
  }
  function renderSources() {
    invalidate(); list.replaceChildren();
    const target = targets[Number(targetSelect.value)];
    sources.forEach((source, index) => {
      if (!target || !hasMask(source, target)) return;
      const row = document.createElement('label'), checkbox = document.createElement('input');
      checkbox.type = 'checkbox'; checkbox.value = String(index);
      const text = document.createElement('span'); text.textContent = sourceTitle(source);
      if (source.updated_at || source.created_at) {
        const time = document.createElement('small');
        time.textContent = new Date(source.updated_at || source.created_at).toLocaleString('ko-KR'); text.append(time);
      }
      checkbox.onchange = () => { invalidate(); message(`${selected().length}개 선택됨`); };
      row.append(checkbox, text); list.append(row);
    });
    lock(false);
    message(list.children.length >= 2 ? '합칠 탭을 2개 이상 선택하세요.' : '합칠 마스크가 부족합니다. U-Net 예측 또는 다른 라벨을 먼저 저장하세요.');
  }
  targetSelect.onchange = renderSources;
  launch.onclick = async (context = {}) => {
    if (busy || dialog.open) return;
    const id = currentId();
    if (!id || !/^\d+$/.test(id)) { alert('라벨링할 태스크를 먼저 선택하세요.'); return; }
    if (context.taskId && String(context.taskId) !== id) { alert('태스크가 변경되었습니다. 다시 실행하세요.'); return; }
    task = null; targets = []; sources = []; targetSelect.replaceChildren(); list.replaceChildren();
    invalidate(); dialog.showModal(); lock(true); message('저장된 마스크를 불러오는 중…');
    try {
      task = await api(`/api/tasks/${id}/`);
      const project = await api(`/api/projects/${task.project}/`);
      if (currentId() !== id) throw new Error('태스크가 변경되었습니다. 창을 닫고 다시 여세요.');
      sources = allSources(task);
      const config = new DOMParser().parseFromString(project.label_config, 'text/xml');
      for (const control of config.querySelectorAll('BrushLabels')) {
        if (control.getAttribute('perRegion') === 'true') continue;
        for (const image of config.querySelectorAll('Image')) {
          if (control.getAttribute('toName') !== image.getAttribute('name')) continue;
          const field = (image.getAttribute('value') || '').match(/^\$(\w+)$/)?.[1];
          if (!field || typeof task.data[field] !== 'string') continue;
          targets.push({field, from_name:control.getAttribute('name'), to_name:image.getAttribute('name'), label:null});
          for (const label of control.querySelectorAll('Label')) targets.push({field,
            from_name:control.getAttribute('name'), to_name:image.getAttribute('name'), label:label.getAttribute('value')});
        }
      }
      targetSelect.replaceChildren(...targets.map((t, i) => new Option(`${t.to_name} / ${t.label ?? '모든 라벨 유지'}`, String(i))));
      const targetIndex = targets.findIndex(t => t.from_name === context.from_name && t.to_name === context.to_name);
      if (targetIndex >= 0) targetSelect.value = String(targetIndex);
      renderSources();
      if (!targets.length) message('Image + BrushLabels 라벨링 설정이 필요합니다.', true);
    } catch (error) { message(error.message, true); }
    finally { lock(false); }
  };
  preview.onclick = async () => {
    if (busy || selected().length < 2) return;
    const chosen = selected(), target = targets[Number(targetSelect.value)];
    invalidate(); lock(true); message('선택한 마스크를 합치는 중…');
    try {
      if (currentId() !== String(task.id)) throw new Error('태스크가 변경되었습니다. 다시 여세요.');
      const imageUrl = new URL(task.data[target.field], location.origin);
      if (!['http:', 'https:'].includes(imageUrl.protocol)) throw new Error('HTTP(S) 이미지 경로가 필요합니다.');
      const merged = await api('/mask-merge/preview', {method:'POST',
        headers:{'Content-Type':'application/json', 'X-CSRFToken':csrf()},
        body:JSON.stringify({...target, sources:chosen.map(s => s.result)})});
      if (currentId() !== String(task.id)) throw new Error('태스크가 변경되었습니다. 다시 여세요.');
      original.src = imageUrl.href;
      await original.decode();
      const region = merged.results[0];
      if (original.naturalWidth !== region.original_width || original.naturalHeight !== region.original_height)
        throw new Error('마스크와 원본 이미지 크기가 다릅니다.');
      if (currentId() !== String(task.id)) throw new Error('태스크가 변경되었습니다. 다시 여세요.');
      snapshot = chosen.map(s => ({id:s.id, kind:s.kind, result:JSON.stringify(s.result)}));
      processed = merged;
      overlay.src = merged.preview; stage.classList.add('show');
      const labels = [...new Set(merged.results.flatMap(r => r.value.brushlabels))];
      stats.textContent = `${labels.join(', ')} · ${merged.stats.sources}개 탭 · ${merged.stats.regions}개 영역 → ${merged.stats.pixels.toLocaleString()}픽셀`;
      message('합친 영역을 확인한 뒤 새 라벨로 저장하세요.');
    } catch (error) { message(error.message, true); }
    finally { lock(false); }
  };
  original.onerror = () => { processed = null; lock(busy); message('원본 이미지를 불러올 수 없습니다. 이미지 경로를 확인하세요.', true); };
  save.onclick = async () => {
    if (busy || !processed || saved) return;
    lock(true); message('새 라벨을 저장하는 중…');
    try {
      if (currentId() !== String(task.id)) throw new Error('태스크가 변경되었습니다. 다시 여세요.');
      const current = await api(`/api/tasks/${task.id}/`), fresh = allSources(current);
      for (const source of snapshot) {
        const match = fresh.find(s => s.kind === source.kind && s.id === source.id);
        if (!match || JSON.stringify(match.result) !== source.result) {
          invalidate(); throw new Error('선택한 원본 마스크가 변경되었습니다. 창을 닫고 다시 여세요.');
        }
      }
      if (currentId() !== String(task.id)) throw new Error('태스크가 변경되었습니다. 다시 여세요.');
      const annotation = await api(`/mask-merge/tasks/${task.id}/annotations`, {method:'POST',
        headers:{'Content-Type':'application/json', 'X-CSRFToken':csrf()},
        body:JSON.stringify({result:processed.results})});
      saved = true; save.textContent = '저장 완료';
      message(`합친 라벨 #${annotation.id} 저장 완료. 창을 닫고 새로고침하면 MERGE 탭에서 수정할 수 있습니다.`);
    } catch (error) {
      // A failed response may follow a committed save; require re-opening before retrying.
      processed = null;
      message(`${error.message} 저장을 시도했다면 새로고침하여 생성 여부를 확인하세요.`, true);
    } finally { lock(false); }
  };
  close.onclick = () => dialog.close();
  dialog.addEventListener('cancel', event => { if (busy) event.preventDefault(); });
  dialog.addEventListener('close', invalidate);
  window.MaskMerge = {open: context => launch.onclick(context)};
})();
