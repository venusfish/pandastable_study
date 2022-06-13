# from __future__ import absolute_import

import platform
if platform.system() == 'Darwin':
    import matplotlib
    matplotlib.use('TkAgg')
from core_study import *
from data_study import *

__version__ = '0.13.0' 
