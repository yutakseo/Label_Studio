(() => {
  if (document.getElementById('dark-line-dialog')) return;
  const fields = [['threshold','예측 임계값',0.5,0.01,0.99,0.01,'높이면 대상 픽셀을 더 엄격하게 선택합니다.']];
  const dialog = document.createElement('dialog'); dialog.id = 'dark-line-dialog';
  dialog.setAttribute('aria-label','Reference Segmenter 마스킹');
  dialog.style.cssText = 'position:fixed;inset:0;margin:auto;width:min(1200px,96vw);height:min(900px,94dvh);max-width:none;padding:0;overflow:hidden;background:#242424;color:#eee;border:1px solid #888;border-radius:10px';
  const host = document.createElement('div'); host.style.height = '100%'; dialog.append(host);
  const root = host.attachShadow({mode:'open'});
  root.innerHTML = `<style>
    :host{font:14px/1.5 system-ui,sans-serif;color-scheme:dark}*{box-sizing:border-box}[hidden]{display:none!important}
    .layout{height:100%;display:flex;flex-direction:column}header,footer{padding:16px 22px;flex:none}header{border-bottom:1px solid #555}h2{font-size:22px;margin:0 0 6px}p{margin:0}.muted,small{color:#bbb;font-size:12px}
    main{flex:1;min-height:0;display:grid;grid-template-columns:290px 1fr;overflow:auto}aside{padding:18px;border-right:1px solid #555;overflow:auto}.field{display:block;margin-bottom:12px}.field span{display:block;margin-bottom:3px}input,select,button{font:inherit;color:inherit;background:#303030;border:1px solid #777;border-radius:5px}input,select{width:100%;padding:6px 9px}small{display:block;margin-top:3px}button{cursor:pointer;padding:8px 12px}button:disabled{opacity:.4;cursor:default}button:focus-visible,input:focus-visible,select:focus-visible{outline:2px solid #9aafff;outline-offset:2px}.primary{background:#384b92}
    .previews{padding:18px;min-width:0;overflow:auto}figure{margin:0 0 16px;min-width:0}figcaption{margin-bottom:7px;font-weight:600}canvas,img{display:block;max-width:100%;height:auto;background:#111;margin:auto}canvas{max-height:360px;width:auto;touch-action:none;cursor:crosshair}img{max-height:320px;width:auto}.pair{display:grid;grid-template-columns:1fr 1fr;gap:14px}footer{border-top:1px solid #555;display:flex;align-items:center;gap:15px;justify-content:space-between}.actions{display:flex;gap:8px;flex:none}[role=status]{font-size:13px;overflow-wrap:anywhere}[data-error=true]{color:#ff8383}
    @media(max-width:740px){main{display:block}aside{border-right:0}footer{flex-direction:column;align-items:stretch}.actions{justify-content:flex-end}.pair{grid-template-columns:1fr}}
  </style><div class="layout"><header><h2>Reference Segmenter 마스킹</h2><p class="muted">프로젝트 공용 모델 · 참여자의 학습을 함께 반영 · 64×64 참고 마스크 → 학습 → 예측 → 패치 수정 → 재학습 · 64×64 패치 전용 U-Net · 전체 예측은 패치별 추론 후 합성</p></header>
  <main><aside><label class="field"><span>대상 이미지 · 라벨</span><select data-target></select></label>
  ${fields.map(([key,title,value,min,max,step,hint]) => `<label class="field"><span>${title}</span><input data-param="${key}" type="number" value="${value}" min="${min}" max="${max}" step="${step}" required><small>${hint}</small></label>`).join('')}
  <figure><figcaption>ROI 선택 · 클릭으로 64×64 패치 이동</figcaption><canvas data-source aria-label="참고 패치 선택"></canvas></figure>
  <p data-roi class="muted">선택한 패치 없음</p><button data-reset>ROI 선택 해제</button>
  <label class="field"><span>내가 저장한 마스크</span><select data-annotation></select></label><button data-import>저장 마스크 가져오기</button>
  <small>현재 라벨의 최신 저장 마스크를 자동으로 가져옵니다. 미저장 편집은 먼저 Update로 저장하세요.</small>
  <p data-round>학습 0회</p></aside><section class="previews">
  <figure><figcaption>마스크 그리기 · 64×64 패치 확대</figcaption><canvas data-patch width="64" height="64" style="width:min(512px,100%);height:auto;aspect-ratio:1;image-rendering:pixelated;max-height:none" aria-label="패치 마스크 편집"></canvas></figure>
  <p class="muted">왼쪽 원본에서 ROI를 선택한 뒤 여기서 수정하세요. 빨간색은 대상, 나머지는 배경입니다.</p>
  <label>브러시 크기<input data-brush type="range" min="1" max="16" value="3" style="max-width:240px"></label><button data-mode>모드: 그리기</button><button data-clear>패치 마스크 지우기</button><button data-train>참고 마스크 학습</button>
  <div class="pair" data-results hidden><figure><figcaption>예측 마스크</figcaption><img data-difference alt="어두운 줄 강조 영상"></figure><figure><figcaption>검출 마스크</figcaption><img data-overlay alt="Reference Segmenter 마스크 미리보기"></figure></div>
  <p data-stats class="muted"></p></section></main><footer><p role="status" aria-live="polite"></p><div class="actions"><button data-close>닫기</button><button data-preview>미리보기</button><button data-save class="primary" disabled>Reference Segmenter 탭 저장·갱신</button></div></footer></div>`;
  document.body.append(dialog);
  const el = selector => root.querySelector(selector);
  const select = el('[data-target]'), canvas = el('[data-source]'), ctx = canvas.getContext('2d');
  const preview = el('[data-preview]'), save = el('[data-save]'), close = el('[data-close]'), status = el('[role=status]');
  let task, targets = [], source = null, blob = null, sourceUrl = null, bbox = null, start = null, processed = null, busy = false, saved = false;
  const taskId = () => new URL(location.href).searchParams.get('task');
  const csrf = () => decodeURIComponent(document.cookie.split('; ').find(v => v.startsWith('csrftoken='))?.slice(10) || '');
  function message(text, error = false) { status.textContent = text; status.dataset.error = String(error); }
  async function api(url, options = {}) {
    const r = await fetch(url, {credentials:'same-origin', ...options});
    const data = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(data.error || data.detail || `요청 실패 (${r.status})`);
    return data;
  }
  function lock(value) {
    busy = value; dialog.setAttribute('aria-busy',String(value));
    for (const node of [select, close, el('[data-reset]'), el('[data-train]'), el('[data-mode]'), el('[data-clear]'), el('[data-annotation]'), el('[data-import]'), ...root.querySelectorAll('input')]) node.disabled = value;
    preview.disabled = value || !source;
    save.disabled = value || !processed || saved || !processed.pixels;
  }
  function invalidate() { processed = null; saved = false; el('[data-results]').hidden = true; el('[data-stats]').textContent = ''; save.textContent = 'Reference Segmenter 탭 저장·갱신'; lock(busy); }
  function draw() {
    ctx.clearRect(0,0,canvas.width,canvas.height);
    if (source) ctx.drawImage(source,0,0);
    if (bbox) {ctx.strokeStyle='#69a7ff';ctx.lineWidth=Math.max(2,canvas.width/350);ctx.strokeRect(bbox[0],bbox[1],bbox[2]-bbox[0],bbox[3]-bbox[1]);}
    el('[data-roi]').textContent = bbox ? `ROI: (${bbox[0]}, ${bbox[1]}) ~ (${bbox[2]}, ${bbox[3]})` : '선택한 패치 없음';
  }
  function clearSource() {
    source = null; blob = null;
    if (sourceUrl) {URL.revokeObjectURL(sourceUrl);sourceUrl=null;}
    canvas.width=1;canvas.height=1;
  }
  async function loadSource() {
    invalidate(); clearSource(); bbox=null;selected=false;predictionMask=null;mc.clearRect(0,0,64,64);renderPatch();lock(true);message('원본 이미지를 불러오는 중…');
    try {
      const target=targets[Number(select.value)], url=new URL(task.data[target.field],location.origin);
      if (!['http:','https:'].includes(url.protocol)) throw new Error('HTTP(S) 이미지 경로가 필요합니다.');
      const r=await fetch(url,{credentials:url.origin===location.origin?'same-origin':'omit'});
      if (!r.ok) throw new Error('원본 이미지를 읽을 수 없습니다.');
      blob=await r.blob();sourceUrl=URL.createObjectURL(blob);
      const img=new Image();img.src=sourceUrl;await img.decode();
      if (img.naturalWidth*img.naturalHeight>16000000) throw new Error('최대 1600만 픽셀까지 지원합니다.');
      source=img;canvas.width=img.naturalWidth;canvas.height=img.naturalHeight;predictionMask=document.createElement('canvas');predictionMask.width=canvas.width;predictionMask.height=canvas.height;draw();
      const state=await learning(formFor('status'));el('[data-round]').textContent=`U-Net · 저장된 학습 쌍 ${state.training_pairs||0}개 · 수정 이력 ${state.round}회`;
      const picker=el('[data-annotation]');picker.replaceChildren(...(state.sources||[]).map(a=>new Option(`내 마스크 #${a.id} · ${new Date(a.updated_at).toLocaleString()}`,String(a.id))));
      if(picker.options.length){await importSavedMask();message('저장된 마스크를 가져왔습니다. 왼쪽에서 ROI를 선택하고 오른쪽에서 수정하세요.');}
      else{picker.add(new Option('저장된 마스크 없음',''));message('왼쪽에서 ROI를 선택하고 오른쪽에서 마스크를 그리세요.');}
    } catch(error) {clearSource();message(error.message,true);}
    finally {lock(false);}
  }
  const point = event => {
    const rect=canvas.getBoundingClientRect();return [Math.max(0,Math.min(canvas.width,Math.round((event.clientX-rect.left)*canvas.width/rect.width))),Math.max(0,Math.min(canvas.height,Math.round((event.clientY-rect.top)*canvas.height/rect.height)))];
  };
  const patch = el('[data-patch]'), pc = patch.getContext('2d');
  const maskCanvas = document.createElement('canvas'); maskCanvas.width=maskCanvas.height=64;
  const mc=maskCanvas.getContext('2d');
  let patchX=0,patchY=0,selected=false,erase=false,painting=false,predictionMask=null;
  function renderPatch(){
    pc.clearRect(0,0,64,64);if(!source||!selected)return;
    pc.drawImage(source,patchX,patchY,64,64,0,0,64,64);
    const tint=document.createElement('canvas');tint.width=tint.height=64;const tc=tint.getContext('2d');
    tc.drawImage(maskCanvas,0,0);tc.globalCompositeOperation='source-in';tc.fillStyle='red';tc.fillRect(0,0,64,64);
    pc.globalAlpha=.5;pc.drawImage(tint,0,0);pc.globalAlpha=1;
  }
  canvas.oncontextmenu=e=>{e.preventDefault();e.stopPropagation();};
  canvas.onpointerdown=e=>{
    if(busy||!source)return;
    if(canvas.width<64||canvas.height<64){message('64×64 이상의 이미지가 필요합니다.',true);return;}
    commitPatch();const [x,y]=point(e);patchX=Math.max(0,Math.min(canvas.width-64,x-32));patchY=Math.max(0,Math.min(canvas.height-64,y-32));
    selected=true;mc.globalCompositeOperation='source-over';mc.clearRect(0,0,64,64);
    if(predictionMask)mc.drawImage(predictionMask,patchX,patchY,64,64,0,0,64,64);
    bbox=[patchX,patchY,patchX+64,patchY+64];draw();renderPatch();
  };
  function commitPatch(){
    if(!source||!selected||!predictionMask)return;
    const context=predictionMask.getContext('2d');context.clearRect(patchX,patchY,64,64);context.drawImage(maskCanvas,patchX,patchY);
  }
  async function maskFromURL(url){
    const img=new Image();img.src=url;await img.decode();
    if(img.width!==canvas.width||img.height!==canvas.height)throw new Error('원본과 저장 마스크의 크기가 다릅니다.');
    const c=document.createElement('canvas');c.width=img.width;c.height=img.height;const cx=c.getContext('2d');cx.drawImage(img,0,0);
    const pixels=cx.getImageData(0,0,c.width,c.height);for(let i=0;i<pixels.data.length;i+=4)pixels.data[i+3]=pixels.data[i];cx.putImageData(pixels,0,0);return c;
  }
  async function importSavedMask(){
    if(taskId()!==String(task.id))throw new Error('태스크가 변경되었습니다. 다시 여세요.');
    const id=el('[data-annotation]').value;if(!id)throw new Error('저장된 마스크를 선택하세요.');
    const f=formFor('mask');f.append('annotation',id);const result=await learning(f);predictionMask=await maskFromURL(result.mask);
    if(selected){mc.globalCompositeOperation='source-over';mc.clearRect(0,0,64,64);mc.drawImage(predictionMask,patchX,patchY,64,64,0,0,64,64);renderPatch();}
    invalidate();
  }
  el('[data-import]').onclick=async()=>{if(busy||!source)return;lock(true);try{await importSavedMask();message('저장 마스크를 가져왔습니다. ROI를 선택해 수정하세요.');}catch(e){message(e.message,true);}finally{lock(false);}};
  function paint(e){if(!painting||busy)return;const r=patch.getBoundingClientRect();
    mc.globalCompositeOperation=erase?'destination-out':'source-over';mc.fillStyle='white';mc.beginPath();
    mc.arc((e.clientX-r.left)*64/r.width,(e.clientY-r.top)*64/r.height,Number(el('[data-brush]').value)/2,0,Math.PI*2);mc.fill();renderPatch();}
  patch.oncontextmenu=e=>{e.preventDefault();e.stopPropagation();};
  patch.onpointerdown=e=>{if(busy||!selected||e.button!==0)return;e.preventDefault();painting=true;patch.setPointerCapture(e.pointerId);paint(e);};
  patch.onpointermove=paint;patch.onpointerup=patch.onpointercancel=()=>painting=false;
  el('[data-mode]').onclick=()=>{erase=!erase;el('[data-mode]').textContent=erase?'모드: 지우기':'모드: 그리기';};
  el('[data-clear]').onclick=()=>{if(busy)return;mc.clearRect(0,0,64,64);renderPatch();};
  const png=c=>new Promise(resolve=>c.toBlob(resolve,'image/png'));
  function formFor(action){const f=new FormData();f.append('task',task.id);f.append('action',action);
    for(const key of ['from_name','to_name','label'])f.append(key,targets[Number(select.value)][key]);return f;}
  async function learning(f){return api('/reference-segmenter/learn',{method:'POST',headers:{'X-CSRFToken':csrf()},body:f});}
  el('[data-train]').onclick=async()=>{
    if(busy||!selected)return;lock(true);message('패치 원본과 마스크를 저장하고 U-Net을 추가 학습하는 중…');
    try{if(taskId()!==String(task.id))throw new Error('태스크가 변경되었습니다. 다시 여세요.');
      const crop=document.createElement('canvas');crop.width=crop.height=64;crop.getContext('2d').drawImage(source,patchX,patchY,64,64,0,0,64,64);
      const binary=document.createElement('canvas');binary.width=binary.height=64;const bc=binary.getContext('2d');bc.fillStyle='black';bc.fillRect(0,0,64,64);bc.drawImage(maskCanvas,0,0);
      const f=formFor('train');f.append('patch_x',patchX);f.append('patch_y',patchY);f.append('image',await png(crop),'patch.png');f.append('mask',await png(binary),'mask.png');
      const result=await learning(f);commitPatch();invalidate();el('[data-round]').textContent=`U-Net · 학습 쌍 ${result.training_pairs}개 · 누적 ${result.steps}스텝 · 수정 이력 ${result.round}회`;message('학습 완료. 예측을 실행한 뒤 패치를 선택해 수정하고 다시 학습하세요.');
    }catch(e){message(e.message,true);}finally{lock(false);}
  };
  el('[data-reset]').onclick=()=>{commitPatch();selected=false;bbox=null;mc.clearRect(0,0,64,64);draw();renderPatch();};
  for(const input of root.querySelectorAll('[data-param]'))input.oninput=()=>invalidate();
  select.onchange=loadSource;
  async function open(context={}) {
    if(busy||dialog.open)return;
    const id=taskId();if(!id||!/^\d+$/.test(id)){alert('라벨링할 태스크를 먼저 선택하세요.');return;}
    if(context.taskId&&String(context.taskId)!==id){alert('태스크가 변경되었습니다. 다시 실행하세요.');return;}
    task=null;targets=[];select.replaceChildren();invalidate();clearSource();dialog.showModal();lock(true);message('태스크 설정을 불러오는 중…');
    try {
      task=await api(`/api/tasks/${id}/`);const project=await api(`/api/projects/${task.project}/`);
      if(taskId()!==id)throw new Error('태스크가 변경되었습니다. 창을 닫고 다시 여세요.');
      const config=new DOMParser().parseFromString(project.label_config,'text/xml');
      for(const control of config.querySelectorAll('BrushLabels')) {
        if(control.getAttribute('perRegion')==='true')continue;
        for(const image of config.querySelectorAll('Image')) {
          const field=(image.getAttribute('value')||'').match(/^\$(\w+)$/)?.[1];
          if(!field||typeof task.data[field]!=='string'||control.getAttribute('toName')!==image.getAttribute('name'))continue;
          for(const label of control.querySelectorAll('Label'))targets.push({field,from_name:control.getAttribute('name'),to_name:image.getAttribute('name'),label:label.getAttribute('value')});
        }
      }
      select.replaceChildren(...targets.map((t,i)=>new Option(`${t.to_name} / ${t.label}`,String(i))));
      const chosen=targets.findIndex(t=>t.from_name===context.from_name&&t.to_name===context.to_name);if(chosen>=0)select.value=String(chosen);
      if(!targets.length)throw new Error('Image + BrushLabels 설정이 필요합니다.');
      await loadSource();
    }catch(error){message(error.message,true);}finally{lock(false);}
  }
  preview.onclick=async()=>{
    if(busy||!source)return;invalidate();lock(true);message('학습된 U-Net으로 전체 이미지를 예측하는 중…');
    try{
      if(taskId()!==String(task.id))throw new Error('태스크가 변경되었습니다. 다시 여세요.');
      const f=formFor('predict');f.append('image',blob,'source');f.append('threshold',el('[data-param="threshold"]').value);
      const result=await learning(f);predictionMask=await maskFromURL(result.mask);
      if(selected){mc.globalCompositeOperation='source-over';mc.clearRect(0,0,64,64);mc.drawImage(predictionMask,patchX,patchY,64,64,0,0,64,64);renderPatch();}
      processed=result;el('[data-difference]').src=result.mask;el('[data-overlay]').src=result.preview;el('[data-results]').hidden=false;
      el('[data-stats]').textContent=`학습 ${result.round}회 · ${result.pixels.toLocaleString()}픽셀`;message('원본에서 수정할 패치를 선택하고 마스크를 고친 뒤 다시 학습하세요.');
    }catch(e){message(e.message,true);}finally{lock(false);}
  };
  save.onclick=async()=>{
    if(busy||!processed||saved||!processed.pixels)return;
    lock(true);message('Reference Segmenter 예측 탭을 저장하는 중…');
    try {
      if(taskId()!==String(task.id))throw new Error('태스크가 변경되었습니다. 다시 여세요.');
      const result=await api('/reference-segmenter/predictions/save',{method:'POST',headers:{'Content-Type':'application/json','X-CSRFToken':csrf()},
        body:JSON.stringify({task:task.id,project:task.project,model_version:'Reference Segmenter',result:processed.results})});
      saved=true;save.textContent='저장 완료';message(`Reference Segmenter 예측 #${result.id} 갱신 완료. 기존 탭을 재사용합니다. 새로고침한 뒤 원본·U-Net과 마스크 합치기를 실행하면 MERGE 탭에서 수정할 수 있습니다.`);
    }catch(error){message(`${error.message} 새로고침하여 저장 상태를 확인하거나 다시 저장하세요.`,true);}finally{lock(false);}
  };
  close.onclick=()=>dialog.close();
  dialog.addEventListener('cancel',e=>{if(busy)e.preventDefault();});
  dialog.addEventListener('close',()=>{invalidate();clearSource();bbox=null;start=null;});
  const deleting = new Set();
  async function deletePrediction(id) {
    if (!/^\d+$/.test(String(id)) || deleting.has(id)) return;
    if (!confirm('Reference Segmenter 예측 탭을 삭제할까요? 삭제 후 화면을 새로고침합니다. 편집 중인 내용은 먼저 저장하세요.')) return;
    deleting.add(id);
    try {
      const response = await fetch(`/reference-segmenter/predictions/${id}`, {method:'DELETE', credentials:'same-origin',
        headers:{'X-CSRFToken':csrf()}});
      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || `삭제 실패 (${response.status})`);
      }
      location.reload();
    } catch(error) {alert(error.message);}
    finally {deleting.delete(id);}
  }
  window.DarkLine={open, deletePrediction};
})();
