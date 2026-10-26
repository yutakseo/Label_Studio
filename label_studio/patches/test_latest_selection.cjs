const assert = require('node:assert/strict');
const fs = require('node:fs');
require('./user_tabs.js');
const bundle = fs.readFileSync(`${__dirname}/../overrides/167.js`, 'utf8');
const start = bundle.indexOf('async setAnnotation(');
const end = bundle.indexOf('async loadUserLabels()', start);
const source = bundle.slice(start, end).replace('async setAnnotation(', 'async function(');
const select = new Function('Q', `return (${source})`)(value => value != null);
(async () => {
  const merge = {id:'merge',pk:'30'}, latest = {id:'latest',pk:'20'};
  const store = {annotations:[merge,latest],selectAnnotation(id){this.selected=id},createAnnotation(){return {id:'new'};}};
  let emitted;
  const context = {lsf:{annotationStore:store},annotations:store.annotations,predictions:[],
    task:{annotations:[{id:30,updated_at:'2026-10-23T00:00:00Z'},{id:20,updated_at:'2026-10-26T00:00:00Z'}]},
    project:{},datamanager:{invoke(event,tab){emitted=tab.id}}};
  await select.call(context,'auto');
  assert.equal(store.selected,'latest'); assert.equal(emitted,'latest');
  await select.call(context,undefined);
  assert.equal(store.selected,'latest');
  // Task navigation may carry an old annotation ID; it must still open the latest.
  await select.call(context,'30'); assert.equal(store.selected,'latest');
  context.task.default_selected_annotation=30;
  await select.call(context,30,true); assert.equal(store.selected,'latest');
  context.task.annotations[0].updated_at='2026-10-27T00:00:00Z';
  await select.call(context,'auto'); assert.equal(store.selected,'merge');
  context.task.annotations[0].was_cancelled=true;
  await select.call(context,'auto'); assert.equal(store.selected,'latest');
  const savedFetch=globalThis.fetch;
  let fetched=0;
  globalThis.fetch=async url=>{fetched++;assert.equal(url,'/api/tasks/935/');return {ok:true,json:async()=>({annotations:[{id:20,updated_at:'2026-10-26T00:00:00Z'},{id:30,updated_at:'2026-10-23T00:00:00Z'}]})}};
  context.task={id:935,annotations:[{pk:'30',is_stub:true,created_at:'2026-10-23T00:00:00Z'},{pk:'20',is_stub:true,created_at:'2026-10-21T00:00:00Z'}]};
  await select.call(context,'30');assert.equal(store.selected,'latest');assert.equal(fetched,1);
  globalThis.fetch=savedFetch;
  console.log('PASS: actual Data Manager task selection, latest user/MERGE, cancelled, navigation IDs, server defaults, real stub metadata');
})().catch(error=>{console.error(error);process.exit(1)});
