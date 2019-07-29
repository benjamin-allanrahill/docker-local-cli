'''
settings.py
@description: module for config values and default settings 
@author: Benjamin Allan-Rahill
'''

import getpass, os.path, platform, re


class settings():
    PKG_NAME = 'locker'
    HERE = os.path.abspath(os.path.dirname(__file__))

    PATTERN = r'^{target}\s*=\s*([\'"])(.+)\1$'
    AUTHOR = re.compile(PATTERN.format(target='__author__'), re.M)
    DOCSTRING = re.compile(r'^([\'"])\1\1(.+)\1\1\1$', re.M)
    VERSION = re.compile(PATTERN.format(target='__version__'), re.M)

    OS = platform.system()

    USER = getpass.getuser()

    proxies = {
        'http': 'proxy-server.bms.com:8080',
        'https': 'proxy-server.bms.com:8080'
    }

    releaseVersionDate = "2019.07."

    ## DEFAULT SETTINGS ##
    ports = [['22', 2222], ['8787', 8787]]

    device = ["/dev/fuse"]

    capabilities = ["SYS_ADMIN", "DAC_READ_SEARCH"]

    image = 'docker.rdcloud.bms.com:443/rr:Genomics2019-03_base'

    registry = 'docker.rdcloud.bms.com'
