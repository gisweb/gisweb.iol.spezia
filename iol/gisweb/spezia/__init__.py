from zope.i18nmessageid import MessageFactory
from AccessControl import allow_module
from zope import component
from .interfaces import IIolApp, IIolPraticaWeb
from .applications.default import defaultApp, defaultWsClient
from .applications.fiere import fiereApp
from .applications.sciaSuap import sciaSuapApp
from .applications.autorizzazioneSuap import autorizzazioneSuapApp
from .applications.scia import sciaApp, sciaWsClient
from .applications.cila import cilaApp, cilaWsClient
from .applications.suapcila import suapcilaApp, suapcilaWsClient
from .applications.suapscia import suapsciaApp, suapsciaWsClient
from .applications.parere import parereApp, parereWsClient
from .applications.regolarizzazione import regolarizzazioneApp, regolarizzazioneWsClient
from .applications.utenti import utentiApp

MessageFactory = MessageFactory('iol.gisweb.spezia')
allow_module('iol.gisweb.spezia.IolApp')
allow_module("iol.gisweb.spezia.IolPraticaWeb")

gsm = component.getGlobalSiteManager()

app = defaultApp()
gsm.registerUtility(app, IIolApp, 'default')

app = fiereApp()
gsm.registerUtility(app, IIolApp, 'fiere')

app = sciaApp()
gsm.registerUtility(app, IIolApp, 'scia')

app = cilaApp()
gsm.registerUtility(app, IIolApp, 'cila')

app = suapcilaApp()
gsm.registerUtility(app, IIolApp, 'suapcila')

app = suapsciaApp()
gsm.registerUtility(app, IIolApp, 'suapscia')

app = parereApp()
gsm.registerUtility(app, IIolApp, 'parere')

app = regolarizzazioneApp()
gsm.registerUtility(app, IIolApp, 'regolarizzazione')

app = sciaSuapApp()
gsm.registerUtility(app, IIolApp, 'sciaSuap')

app = autorizzazioneSuapApp()
gsm.registerUtility(app, IIolApp, 'autorizzazioneSuap')

#Register Named Utility For WebService Praticaweb
app = defaultWsClient()
gsm.registerUtility(app, IIolPraticaWeb, config.APP_FIELD_DEFAULT_VALUE)

app = sciaWsClient()
gsm.registerUtility(app, IIolPraticaWeb, 'scia')

app = cilaWsClient()
gsm.registerUtility(app, IIolPraticaWeb, 'cila')

app = suapcilaWsClient()
gsm.registerUtility(app, IIolPraticaWeb, 'suapcila')

app = suapsciaWsClient()
gsm.registerUtility(app, IIolPraticaWeb, 'suapscia')

app = parereWsClient()
gsm.registerUtility(app, IIolPraticaWeb, 'parere')

app = regolarizzazioneWsClient()
gsm.registerUtility(app, IIolPraticaWeb, 'regolarizzazione')

app = utentiApp()
gsm.registerUtility(app, IIolApp, 'utenti')

