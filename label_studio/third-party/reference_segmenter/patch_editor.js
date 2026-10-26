(() => {
  const View = (0, y.PA)(({item}) => (0, se.jsx)(ms, {
    label:'참고 마스크 학습', ariaLabel:'dark-line', active:false, disabled:false, tool:item,
    icon:(0,se.jsxs)('svg',{width:24,height:24,viewBox:'0 0 24 24',fill:'none',stroke:'currentColor',children:[
      (0,se.jsx)('rect',{x:3,y:3,width:18,height:18,rx:2,strokeWidth:1.5}),
      (0,se.jsx)('path',{d:'M6 9h12M6 15h12',strokeWidth:2.5}),
      (0,se.jsx)('path',{d:'m9 9 2-1 3 2 2-1',strokeWidth:1})
    ]}),onClick:()=>item.openDarkLine()
  }));
  const model=u.gK.model('DarkLineTool',{group:'segmentation',default:false,unselectRegionOnToolChange:false})
    .volatile(()=>({index:9998.7,canInteractWithRegions:false}))
    .views(self=>({get viewClass(){return ()=>(0,se.jsx)(View,{item:self});}}))
    .actions(self=>({openDarkLine(){
      if(!window.DarkLine){alert('참고 마스크 학습 도구를 불러오지 못했습니다. 새로고침하세요.');return;}
      if(self.obj.rotation||self.obj.multiImage){alert('회전하지 않은 단일 이미지에서 사용하세요.');return;}
      window.DarkLine.open({from_name:self.control.name,to_name:self.obj.name,taskId:String((0,u.Zn)(self.control).task.id)});
    }}));
  return u.gK.compose('DarkLineTool',Gl,Cs,model);
})()
