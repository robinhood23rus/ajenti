from ajenti.api import *
from ajenti import version
from ajenti.com import *
from ajenti.ui import *
from ajenti.utils import *

import ajenti.plugmgr


class PluginManager(CategoryPlugin, URLHandler):
    text = 'Plugins'
    icon = '/dl/plugins/icon_small.png'
    folder = 'bottom'

    def on_session_start(self):
        self._tab = 0
        self._mgr = ajenti.plugmgr.PluginInstaller(self.app)
        self._changes = False
        
    def get_ui(self):
        ui = self.app.inflate('plugins:main')
        
        lst = self._mgr.list_plugins()

        for k in lst:
            row = self.app.inflate('plugins:item')
            desc = '<span class="ui-el-label-1" style="padding-left: 5px;">%s</span>'%k.desc
            row.find('name').set('text', k.name)
            row.find('desc').set('text', k.problem or k.desc)
            row.find('icon').set('file', k.icon)
            row.find('version').set('text', k.version)
            row.find('author').set('text', k.author)
            row.find('author').set('url', k.homepage)
            row.append('buttons', UI.WarningMiniButton(
                        text='Uninstall', 
                        id='remove/'+k.id,
                        msg='Completely remove plugin "%s"'%k.name
                    ))
                    
            if k.problem:
                row.find('status').set('file', '/dl/plugins/broken.png')
            else:
                row.find('status').set('file', '/dl/plugins/good.png')
            ui.append('list', row)
            
                
        lst = self._mgr.available
        inst = self._mgr.list_plugins()
        
        btn = UI.Button(text='Check for updates', id='update')
        if len(lst) == 0:
            btn['text'] = 'Download plugin list'
            
        for k in lst:
            same = False
            for p in inst: 
                if k['id'] == p.id and (k['version'] == p.version or p.problem): 
                    same = True
            if same:
                continue
            
            row = self.app.inflate('plugins:item')
            row.find('name').set('text', k['name'])
            row.find('desc').set('text', k['description'])
            row.find('icon').set('file', k['icon'])
            row.find('version').set('text', k['version'])
            row.find('author').set('text', k['author'])
            row.find('author').set('url', k['homepage'])
                    
            row.find('status').set('file', '/dl/plugins/none.png')
            for p in inst: 
                if k['id'] == p.id:
                    row.find('status').set('file', '/dl/plugins/upgrade.png')

            reqd = ajenti.plugmgr.get_deps(self.app.platform, k['deps'])
            req = UI.VContainer(
                    UI.Label(text='Requires:', bold=True),
                    spacing=0
                  )
                  
            ready = True      
            for r in reqd:
                if ajenti.plugmgr.verify_dep(r):
                    continue
                if r[0] == 'app':
                    req.append(UI.Label(text='Application %s (%s)'%r[1:]))
                if r[0] == 'plugin':
                    req.append(UI.Label(text='Plugin %s'%r[1]))
                ready = False    
                    
            url = 'http://%s/view/plugins.php?id=%s' % (
                    self.app.config.get('ajenti', 'update_server'),
                    k['id']
                   )

            if not ready:
                row.append('reqs', req)
            else:                   
                row.append('buttons', UI.WarningMiniButton(
                        text='Install', 
                        id='install/'+k['id'],
                        msg='Download and install plugin "%s"'%k['name']
                    ))

            ui.append('list', row)

        return ui

    def get_ui_upload(self):
        return UI.Uploader(
            url='/upload_plugin',
            text='Install'
        )
    
    @url('^/upload_plugin$')
    def upload(self, req, sr):
        vars = get_environment_vars(req)
        f = vars.getvalue('file', None)
        try:
            self._mgr.install_file(f)
        except:
            pass
        sr('301 Moved Permanently', [('Location', '/')])
        self._changes = True
        return ''
        
    @event('button/click')
    @event('minibutton/click')
    @event('linklabel/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'update':
            self._tab = 1
            self._mgr.update_list()
        if params[0] == 'remove':
            self._tab = 0
            self._mgr.remove(params[1])
            self._changes = True
        if params[0] == 'restart':
            self.app.restart()
        if params[0] == 'install':
            self._tab = 0
            self._mgr.install(params[1])
        
    @event('form/submit')
    @event('dialog/submit')
    def on_submit(self, event, params, vars=None):
        pass
