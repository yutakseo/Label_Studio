const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');

test('pen context menus are blocked only inside the editor and listener is disposed',()=>{
  const listeners=new Map();
  const context={window:{addEventListener:(type,fn)=>listeners.set(type,fn),removeEventListener:type=>listeners.delete(type)},Date};
  vm.runInNewContext(fs.readFileSync(__dirname+'/pen_input.js','utf8'),context);
  const canvas={};
  const dispose=context.__labelStudioPenInput({props:{item:{containerRef:{contains:target=>target===canvas}}}});
  function menu(pointerType,target){
    const event={pointerType,target,preventDefault(){this.prevented=true;},stopImmediatePropagation(){this.stopped=true;}};
    listeners.get('contextmenu')(event);
    return event;
  }
  const pen=menu('pen',canvas);
  assert.equal(pen.prevented,true);
  assert.equal(pen.stopped,true);
  assert.equal(menu('mouse',canvas).prevented,undefined);
  assert.equal(menu('pen',{}).prevented,undefined);
  dispose();
  assert.equal(listeners.size,0);
});
