const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(`${__dirname}/panel.js`, 'utf8');

test('source image and 64 pixel mask editor bind to separate canvases', () => {
  const patch = {width:64, height:64, getContext:()=>({name:'patch'})};
  const original = {width:300, height:150, getContext:()=>({name:'original'})};
  const el = selector => ({'[data-target]':{}, '[data-source]':original, '[data-patch]':patch, canvas:patch})[selector];
  const binding = source.match(/const select = .*?;/)[0];
  const context = {el};
  vm.runInNewContext(`${binding};canvas.width=2048;canvas.height=1024;globalThis.selected=canvas;globalThis.context=ctx;`, context);
  assert.equal(context.selected, original);
  assert.equal(context.context.name, 'original');
  assert.equal(patch.width,64);
  assert.equal(patch.height,64);
  assert.match(source, /<canvas data-source aria-label="참고 패치 선택">/);
});


test('ROI lives in sidebar and mask painting lives in main section', () => {
  const sidebar=source.slice(source.indexOf('<main><aside>'),source.indexOf('</aside>'));
  const main=source.slice(source.indexOf('<section class="previews">'),source.indexOf('</section>'));
  assert.match(sidebar, /canvas data-source/);
  assert.doesNotMatch(sidebar, /canvas data-patch/);
  assert.match(main, /canvas data-patch/);
  assert.match(sidebar, /select data-annotation/);
});


test('saving uses idempotent reference tab API', () => {
  assert.match(source, /api\('\/reference-segmenter\/predictions\/save'/);
  assert.doesNotMatch(source, /api\('\/api\/predictions\/'/);
});
