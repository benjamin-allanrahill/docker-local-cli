# config.py
import re, os.path

class config(object):
    PKG_NAME        = 'prodcli'
    HERE            = os.path.abspath(os.path.dirname(__file__))
    
    PATTERN         = r'^{target}\s*=\s*([\'"])(.+)\1$'
    AUTHOR          = re.compile(PATTERN.format(target='__author__'), re.M)
    DOCSTRING       = re.compile(r'^([\'"])\1\1(.+)\1\1\1$', re.M)
    VERSION         = re.compile(PATTERN.format(target='__version__'), re.M)
    
    # FIELDSURL = 'https://dashboard.pri.bms.com:8443/rest/api/latest/field'
    # ISSUEURL  = 'https://dashboard.pri.bms.com:8443/rest/api/latest/issue'

    # # JIRA application account credentials
    # JIRA_UN = "purrapp"
    # JIRA_PW = "purrapp123"

    # APP_DIR = "/home01/ec2_user/russom/dev/purr3/"
        
    proxies         = {'http':'proxy-server.bms.com:8080','https':'proxy-server.bms.com:8080'}
    
    # BioGit urls
    BioGitUrl       = 'https://biogit.pri.bms.com'
    BioGitApiUrl    = 'https://biogit.pri.bms.com/api/v3'
    
    # Domino URLs
    DominoUrl       = "https://domino.web.bms.com"
    
    # Script data URL
    #ScriptDataUrl   = "http://bmsrd-rr-web.s3-website-us-east-1.amazonaws.com/prod.json"
    ScriptDataUrl   = "https://biogit.pri.bms.com/russom/prod-cli/blob/master/prod.json"
    
    # Login page
    smlogin         = 'https://smusath.net.bms.com/siteminderagent/forms/login.fcc'
    #smlogin         = 'https://smusath.net.bms.com/siteminderagent/forms/authform.fcc'
    
    # SiteMinder target page
    smtarget        = 'HTTPS://smwinath.bms.com/redirect/redirector.asp?ORIGTARGET=http%3a%2f%2fsiteminder%2ebms%2ecom%2f'
    
    # Match login failure page
    failRegex       = re.compile(r'.*<html.*AUTHENTICATION\s*FAILED.*</html.*', re.S)

    PURR_URL = 'https://tbio-prd.rdcloud.bms.com:9443'