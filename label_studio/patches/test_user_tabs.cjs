const assert = require('node:assert/strict');
require('./user_tabs.js');
const {tabIdentity} = require('../draft_preview/panel.js');
(async () => {
  const users = new Map([[1,{id:1,username:'yutakseo'}],[2,{id:2,username:'duduk7668'}]]);
  const tabs=[
    {pk:'2',createdDate:'2026-10-17T00:00:00Z',modifiedDate:'2026-10-20T02:08:00Z'},
    {pk:'3',createdDate:'2026-10-19T00:00:00Z',modifiedDate:'2026-10-19T01:00:00Z'},
    {pk:'1',createdDate:'2026-10-16T00:00:00Z'},
  ];
  assert.deepEqual(__labelStudioSortTabs(tabs).map(t=>t.pk),['1','3','2']);
  assert.deepEqual(tabs.map(t=>t.pk),['2','3','1']);
  tabs[1].modifiedDate='2026-10-20T03:00:00Z';
  assert.deepEqual(__labelStudioSortTabs(tabs).map(t=>t.pk),['1','2','3']);
  tabs[0].draftSaved='2026-10-20T04:00:00Z';
  assert.deepEqual(__labelStudioSortTabs(tabs).map(t=>t.pk),['1','3','2']);
  assert.deepEqual(__labelStudioSortTabs([{pk:'2'},{pk:'1'}]).map(t=>t.pk),['1','2']);
  // The saved version wins across authors and MERGE, independent of list/draft order.
  const savedTabs = {annotations:[
    {id:'user',pk:'10',draftSaved:'2026-10-26T12:00:00Z'},
    {id:'other-user',pk:'20'}, {id:'merge',pk:'30'}, {id:'cancelled',pk:'40'},
  ]};
  const records = [
    {id:10,updated_at:'2026-10-25T00:00:00Z'},
    {id:20,updated_at:'2026-10-26T01:00:00Z'},
    {id:40,updated_at:'2026-10-26T03:00:00Z',was_cancelled:true},
    {id:30,updated_at:'2026-10-26T00:00:00Z'},
  ];
  assert.equal(__labelStudioLatestSavedTab(savedTabs,records).id,'other-user');
  records[3].updated_at='2026-10-26T02:00:00Z';
  assert.equal(__labelStudioLatestSavedTab(savedTabs,records).id,'merge');
  records[1].updated_at=records[3].updated_at;
  assert.equal(__labelStudioLatestSavedTab(savedTabs,records).id,'merge');
  assert.equal(__labelStudioLatestSavedTab(savedTabs,[]),undefined);
  assert.equal(__labelStudioLatestSavedTab(savedTabs,[records[2]]),undefined);
  const original=[{mask:'original'}], edited=[{mask:'edited'}];
  let visible=edited, submitted=0, flags={};
  const source={id:'source',pk:'525',type:'annotation',user:{id:2},versions:{result:original},draftId:7,
    beforeSend(){},validate:()=>true,serializeAnnotation:()=>visible,
    pauseAutosave(){this.paused=true},dropDraft(){this.draftId=0},
    deleteAllRegions(){visible=[]},deserializeResults(result){visible=result},reinitHistory(){},
    resetSubmission(){this.reset=true},startAutosave(){this.paused=false}};
  const store={store:{user:{id:1}},selected:source,annotations:[source],
    addAnnotationFromPrediction(input){
      const own={id:'own',pk:null,type:'annotation',user:{id:1},result:input._initialAnnotationObj,
        setDraftId(id){this.draftId=id},submissionInProgress(){this.submitting=true}};
      this.annotations.push(own);this.selected=own;return own;
    },selectAnnotation(id){this.selected=this.annotations.find(a=>a.id===id)}};
  const app={annotationStore:store,hasInterface:()=>false,setFlags(value){Object.assign(flags,value)},
    waitForDraftSubmission:()=>Promise.resolve(),submitAnnotation(){submitted++}};
  assert.equal(__labelStudioCanEditAnnotation(store,source),false);
  // A working edit stays in its local draft until the Update action runs.
  assert.equal(store.annotations.length,1);
  assert.equal(__labelStudioForkOnUpdate(app),true);
  assert.equal(store.annotations.length,1);
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal(store.annotations.length,2);
  assert.deepEqual(visible,original);
  assert.deepEqual(store.selected.result,edited);
  assert.equal(store.selected.draftId,7);
  assert.equal(store.selected.user.id,1);
  assert.equal(source.reset,true);
  assert.equal(source.paused,false);
  assert.equal(submitted,1);
  assert.equal(flags.isSubmitting,false);
  assert.equal(__labelStudioForkOnUpdate(app),false);
  assert.equal(store.annotations.length,2);
  const savedOwn=store.selected;
  savedOwn.pk='800';savedOwn.pauseAutosave=()=>{};savedOwn.startAutosave=()=>{};
  savedOwn.deleteAllRegions=()=>{savedOwn.result=[]};savedOwn.deserializeResults=r=>{savedOwn.result=r};savedOwn.reinitHistory=()=>{};
  store.selected=source;source.draftId=8;visible=[{mask:'second edit'}];let updates=0;
  app.updateAnnotation=()=>{updates++};
  assert.equal(__labelStudioForkOnUpdate(app),true);
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal(store.annotations.length,2);
  assert.equal(store.selected,savedOwn);
  assert.deepEqual(savedOwn.result,[{mask:'second edit'}]);
  assert.equal(updates,1);assert.equal(submitted,1);
  const copied=__labelStudioCopyToUserTab(store,{serializeAnnotation:()=>[{mask:'prediction'}]});
  assert.equal(copied,savedOwn);assert.equal(store.annotations.length,2);
  assert.deepEqual(savedOwn.result,[{mask:'prediction'}]);
  const foreign=tabIdentity({id:525,completed_by:2},{selected:true,isDrawing:true},{id:1},[],users);
  assert.equal(foreign.name,'duduk7668');assert.equal(foreign.label,'원본 보존');
  assert.equal(typeof globalThis.__labelStudioOwnTab,'undefined');
  console.log('PASS: ascending modified-time sort and refresh; Update-only fork, draft retention, original preservation');
})().catch(error=>{console.error(error);process.exit(1)});
