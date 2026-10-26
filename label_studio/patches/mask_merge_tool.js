(() => {
  const View = (0, y.PA)(({item}) => (0, se.jsx)(ms, {
    label: '마스크 합치기', ariaLabel: 'mask-merge',
    active: false, disabled: false, tool: item,
    icon: (0, se.jsxs)('svg', {width:24, height:24, viewBox:'0 0 24 24',
      fill:'none', stroke:'currentColor', strokeWidth:1.7, children:[
        (0, se.jsx)('rect', {x:3, y:3, width:12, height:12, rx:2}),
        (0, se.jsx)('rect', {x:9, y:9, width:12, height:12, rx:2}),
        (0, se.jsx)('path', {d:'M15 12v6m-3-3h6'})
      ]}), onClick: () => item.openMerge()
  }));
  const model = u.gK.model('MaskMergeTool', {
    group:'segmentation', default:false, unselectRegionOnToolChange:false
  }).volatile(() => ({index:9998.6, canInteractWithRegions:false}))
    .views(self => ({get viewClass() { return () => (0, se.jsx)(View, {item:self}); }}))
    .actions(self => ({openMerge() {
      if (!window.MaskMerge) { alert('마스크 합치기 도구를 불러오지 못했습니다. 새로고침하세요.'); return; }
      if (self.obj.rotation || self.obj.multiImage) { alert('회전하지 않은 단일 이미지에서 사용하세요.'); return; }
      window.MaskMerge.open({from_name:self.control.name, to_name:self.obj.name,
        taskId:String((0, u.Zn)(self.control).task.id)});
    }}));
  return u.gK.compose('MaskMergeTool', Gl, Cs, model);
})()
