# configuration class for pandastable

from __future__ import absolute_import, division, print_function # 파이썬 3에서 쓰던 문법을 파이썬 2에서 쓸수있게 해주는 문법
import math, time
import os, types
import string, copy
from collections import OrderedDict
try:
    from tkinter import *
    from tkinter.ttk import *
except:
    from tkinter import *
    from tkinter.ttk import *
try:
    import configparser
except:
    import configparser as configparser # 대문자를 소문자로 수정함

# from pandastable import util, plotting, dialogs # pandastable 추가함
import util_study, plotting_study, dialogs_study # pandastable 추가함

homepath = os.path.join(os.path.expanduser("~")) # Home directory 확인을 위해 os.path 모듈 import, expanduser("~") 함수 사용
configpath = os.path.join(homepath,'.config/testing') # os.path.join() 함수를 사용해도 접근 가능, 수정함
if not os.path.exists(configpath):
    try:
        os.makedirs(configpath, exist_ok=True)
    except:
        os.makedirs(configpath)
default_conf = os.path.join(configpath, 'default.conf')

baseoptions = OrderedDict() # OrderedDict를 사용하면 데이터의 순서를 보장
baseoptions['base'] = {'font': 'Arial','fontsize':12, 'fontstyle':'',
                        'floatprecision':2, 'thousandseparator': '',
                        'rowheight':22,'cellwidth':80, 'linewidth':1,
                        'align':'w',
                        }
baseoptions['colors'] =  {'cellbackgr':'#F4F4F3',
                        'textcolor':'black',
                        'grid_color':'#ABB1AD',
                        'rowselectedcolor':'#E4DED4',
                        'colheadercolor':'gray25'}


def write_default_config(): # Write a default config to users .config folder. Used to add global settings."""

    fname = os.path.join(configpath, 'default.conf')
    if not os.path.exists(fname):
        try:
            
            os.makedirs(configpath) # os.mkdir(config_path), 나중에 문제발생하면 주석 참조
        except:
            pass
        write_config(conffile=fname, defaults=baseoptions)
    return fname

def write_config(conffile='default.conf', defaults={}): #  Write a default config file"""

    if not os.path.exists(conffile):
        cp = create_config_parser_from_dict(defaults)
        cp.write(open(conffile,'w'))
        print ('wrote config file %s' %conffile)
    return conffile

def create_config_parser_from_dict(data=None, sections=baseoptions.keys(), **kwargs):
    """Helper method to create a ConfigParser from a dict of the form shown in
       baseoptions"""

    if data is None:
        data = baseoptions
    #print (data)
    cp = configparser.ConfigParser()
    for s in sections:
        cp.add_section(s)
        if not s in data:
            continue
        for name in sorted(data[s]):
            val = data[s][name]
            if type(val) is list:
                val = ','.join(val)
            cp.set(s, name, str(val))

    #use kwargs to create specific settings in the appropriate section
    for s in cp.sections():
        opts = cp.options(s)
        for k in kwargs:
            if k in opts:
                cp.set(s, k, kwargs[k])
    return cp

def update_config(options):
    cp = create_config_parser_from_dict()
    for section in cp.sections():
        for o in cp[section]:
            cp[section][o] = str(options[o])
    return cp

def parse_config(conffile=None):
    """Parse a configparser file"""

    f = open(conffile,'r')
    cp = configparser.ConfigParser()
    try:
        cp.read(conffile)
    except Exception as e:
        print ('failed to read config file! check format')
        print ('Error returned:', e)
        return
    f.close()
    return cp

def get_options(cp):
    """Makes sure boolean opts are parsed"""

    from collections import OrderedDict
    options = OrderedDict()
    #options = cp._sections['base']
    for section in cp.sections():
        options.update( (cp._sections[section]) )
    for o in options:
        for section in cp.sections():
            try:
                options[o] = cp.getboolean(section, o)
            except:
                pass
            try:
                options[o] = cp.getint(section, o)
            except:
                pass
    return options

def print_options(options):
    """Print option key/value pairs"""

    for key in options:
        print (key, ':', options[key])
    print ()

def check_options(opts):
    """Check for missing default options in dict. Meant to handle
       incomplete config files"""

    sections = list(baseoptions.keys())
    for s in sections:
        defaults = dict(baseoptions[s])
        for i in defaults:
            if i not in opts:
                opts[i] = defaults[i]
    return opts

def load_options():
    if not os.path.exists(default_conf):
        write_config(default_conf, defaults=baseoptions)
    cp = parse_config(default_conf)
    options = get_options(cp)
    options = check_options(options)
    return options

def apply_options(options, table):
    """Apply options to a table"""

    for i in options:
        table.__dict__[i] = options[i]    
    table.setFont()
    table.redraw()
    return

class preferencesDialog(Frame):
    """Preferences dialog from config parser options"""

    def __init__(self, parent, options, table=None):

        self.parent = parent
        self.main = Toplevel()
        self.master = self.main
        x,y,w,h = dialogs_study.getParentGeometry(self.parent)
        self.main.geometry('+%d+%d' %(x+w/2-200,y+h/2-200))
        self.main.title('Preferences')
        self.main.protocol("WM_DELETE_WINDOW", self.quit)
        self.main.grab_set()
        self.main.transient(parent)
        self.main.resizable(width=False, height=False)
        self.createWidgets()
        self.updateFromOptions(options)
        self.options = options
        self.table = table
        return

    def createWidgets(self):
        """create widgets"""

        fonts = util_study.getFonts()

        self.opts = {'rowheight':{'type':'scale','default':18,'range':(5,50),'interval':1,'label':'row height'},
                'cellwidth':{'type':'scale','default':80,'range':(10,300),'interval':5,'label':'cell width'},
                'linewidth':{'type':'scale','default':1,'range':(1,10),'interval':1,'label':'grid line width'},
                'align':{'type':'combobox','default':'w','items':['w','e','center'],'label':'text align'},
                'vertlines':{'type':'checkbutton','default':1,'label':'show vertical lines'},
                'horizlines':{'type':'checkbutton','default':1,'label':'show horizontal lines'},
                'font':{'type':'combobox','default':'Arial','items':fonts},
                'fontstyle':{'type':'combobox','default':'','items':['','bold','italic']},
                'fontsize':{'type':'scale','default':12,'range':(5,40),'interval':1,'label':'font size'},
                'floatprecision':{'type':'entry','default':2,'label':'precision'},
                'thousandseparator':{'type':'combobox','default':'','items':['',','],'label':'thousands separator'},
                'cellbackgr':{'type':'colorchooser','default':'#F4F4F3', 'label':'background color'},
                'textcolor':{'type':'colorchooser','default':'black', 'label':'text color'},
                'grid_color':{'type':'colorchooser','default':'#ABB1AD', 'label':'grid color'},
                'rowselectedcolor':{'type':'colorchooser','default':'#E4DED4','label':'highlight color'},
                'colheadercolor':{'type':'colorchooser','default':'gray25','label':'column header color'},
                'colormap':{'type':'combobox','default':'Spectral','items':plotting_study.colormaps},
                'marker':{'type':'combobox','default':'','items':plotting_study.markers},
                'linestyle':{'type':'combobox','default':'-','items':plotting_study.linestyles},
                'ms':{'type':'scale','default':5,'range':(1,80),'interval':1,'label':'marker size'},
                'grid':{'type':'checkbutton','default':0,'label':'show grid'},
                }
        sections = {'table':['align','floatprecision','thousandseparator','rowheight','cellwidth','linewidth','vertlines','horizlines'],
                    'formats':['font','fontstyle','fontsize','cellbackgr','textcolor',
                               'grid_color','rowselectedcolor','colheadercolor']}
                    #'plotting':['marker','linestyle','ms','grid','colormap']}


        dialog, self.tkvars, self.widgets = dialogs_study.dialogFromOptions(self.main, self.opts, sections)
        dialog.pack(side=TOP,fill=BOTH)
        #d = dialogs.getDictfromTkVars(opts, tkvars, widgets)

        bf = Frame(self.main)
        bf.pack(fill=BOTH,expand=1)
        Button(bf, text='Apply', command=self.apply).pack(side=LEFT,padx=1,pady=1,fill=BOTH,expand=1)
        Button(bf, text='Save as Default',  command=self.save).pack(side=LEFT,padx=1,pady=1,fill=BOTH,expand=1)
        Button(bf, text='Close',  command=self.quit).pack(side=LEFT,padx=1,pady=1,fill=BOTH,expand=1)
        return

    def updateFromOptions(self, options):
        """Update all widget tk vars using dict"""

        if self.tkvars == None:
            return
        #print (options)
        for i in options:
            if i in self.tkvars and self.tkvars[i]:
                try:
                    val = int(options[i])
                except:
                    val = options[i]
                self.tkvars[i].set(val)
        return

    def apply(self):
        """Apply options to current table"""

        table = self.table
        options = dialogs_study.getDictfromTkVars(self.opts, self.tkvars, self.widgets)
        apply_options(options, table)
        return

    def save(self):
        """Save from current dialog settings"""

        options = dialogs_study.getDictfromTkVars(self.opts, self.tkvars, self.widgets)
        #print (options)
        #update configparser and write
        cp = update_config(options)
        cp.write(open(default_conf,'w'))
        return

    def quit(self):
        self.main.destroy()
        return
