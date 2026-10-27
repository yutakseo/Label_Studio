"""Offline browser flow: class registration, separate training, preview and save.

Run with Playwright and Chromium installed. All API writes are intercepted.
"""
import base64
import io
import json
from email.parser import BytesParser
from email.policy import default
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright


def run():
    stream=io.BytesIO();Image.new('RGB',(128,128),'#555555').save(stream,format='PNG');png=stream.getvalue()
    mask_url='data:image/png;base64,'+base64.b64encode(png).decode()
    config='<View><Image name="image" value="$image"/><BrushLabels name="brush" toName="image"><Label value="Exposure"/></BrushLabels></View>'
    states={'Exposure':{'round':2,'trained':True,'training_pairs':2,'samples':[],'sources':[]}}
    writes=[]
    task={'id':935,'project':16,'data':{'image':'/source.png'},'annotations':[]}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1400,'height':1000});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        def route(request_route):
            nonlocal config
            request=request_route.request;url=request.url
            if url.endswith('/api/tasks/935/'):
                request_route.fulfill(json=task)
            elif url.endswith('/api/projects/16/'):
                if request.method=='PATCH':
                    config=request.post_data_json['label_config'];writes.append(('config',config))
                request_route.fulfill(json={'label_config':config})
            elif url.endswith('/source.png'):
                request_route.fulfill(body=png,content_type='image/png')
            elif url.endswith('/reference-segmenter/learn'):
                content_type=request.headers['content-type']
                parts=BytesParser(policy=default).parsebytes(('Content-Type: '+content_type+'\r\n\r\n').encode()+request.post_data_buffer)
                form={part.get_param('name',header='content-disposition'):part.get_payload(decode=True) for part in parts.iter_parts()}
                action=form['action'].decode();label=form['label'].decode()
                state=states.setdefault(label,{'round':0,'trained':False,'training_pairs':0,'samples':[],'sources':[]})
                if action=='train':
                    writes.append(('train',label));state.update(round=1,trained=True,training_pairs=1,samples=[{'task_id':935,'user_id':1,'x':0,'y':0}])
                if action=='predict':
                    assert state['trained'];request_route.fulfill(json={**state,'results':[],'pixels':16,'mask':mask_url,'preview':mask_url})
                else:request_route.fulfill(json=state)
            elif url.endswith('/reference-segmenter/predictions/save'):
                data=request.post_data_json;writes.append(('save',data['label']));request_route.fulfill(json={'id':100})
            else:request_route.fulfill(content_type='text/html',body='<html><body></body></html>')
        page.route('http://reference.test/**',route)
        page.goto('http://reference.test/projects/16/data?task=935')
        page.add_script_tag(path=str(Path(__file__).with_name('panel.js').resolve()))
        page.evaluate('window.DarkLine.open()')
        shadow=page.locator('#dark-line-dialog')
        shadow.locator('[data-round]').filter(has_text='Exposure').wait_for()
        shadow.locator('[data-target]').select_option('__add__')
        assert shadow.locator('[data-target]').input_value()=='0'
        assert shadow.locator('[data-new-label]').evaluate('(node)=>node===node.getRootNode().activeElement')
        shadow.locator('[data-new-label]').fill('Dryspot')
        shadow.locator('[data-add-label]').click()
        page.wait_for_function("document.querySelector('#dark-line-dialog > div').shadowRoot.querySelector('[data-round]').textContent.includes('Dryspot · 학습 전')")
        assert 'value="Exposure"' in config and 'value="Dryspot"' in config
        shadow.locator('[data-source]').click(position={'x':25,'y':25})
        shadow.locator('[data-patch]').click(position={'x':40,'y':40})
        shadow.locator('[data-train]').click()
        page.wait_for_function("document.querySelector('#dark-line-dialog > div').shadowRoot.querySelector('[data-round]').textContent.includes('Dryspot · 학습됨')")
        shadow.locator('summary').click()
        shadow.locator('[data-samples] li').filter(has_text='이미지 #935').wait_for()
        shadow.locator('[data-preview]').click()
        shadow.locator('[data-save]').wait_for(state='visible')
        page.wait_for_function("!document.querySelector('#dark-line-dialog > div').shadowRoot.querySelector('[data-save]').disabled")
        shadow.locator('[data-save]').click()
        page.wait_for_function("document.querySelector('#dark-line-dialog > div').shadowRoot.querySelector('[data-save]').textContent==='저장 완료'")
        shadow.locator('[data-target]').select_option('0')
        page.wait_for_function("document.querySelector('#dark-line-dialog > div').shadowRoot.querySelector('[data-round]').textContent.includes('Exposure · 학습됨')")
        assert 'Exposure · 패치 2개' in shadow.locator('[data-dataset]').inner_text()
        assert states['Exposure']['round']==2 and states['Exposure']['training_pairs']==2
        assert shadow.locator('[data-save]').is_disabled()
        assert ('train','Dryspot') in writes and ('save','Dryspot') in writes
        assert not errors,errors
        page.screenshot(path='/tmp/reference-multiclass.png')
        browser.close()
    print('PASS: class registration preserves config; independent sample/training selection; class-specific preview/save; class switch clears preview')


if __name__=='__main__':run()
