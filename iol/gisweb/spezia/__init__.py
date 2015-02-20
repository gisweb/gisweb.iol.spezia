from zope.i18nmessageid import MessageFactory
from AccessControl import allow_module
from zope import component
from .interfaces import IIolApp
from .applications.default import defaultApp
from .applications.fiere import fiereApp

MessageFactory = MessageFactory('iol.gisweb.spezia')
allow_module('iol.gisweb.spezia.IolApp')

gsm = component.getGlobalSiteManager()

app = defaultApp()
gsm.registerUtility(app, IIolApp, 'default')

app = fiereApp()
gsm.registerUtility(app, IIolApp, 'fiere')