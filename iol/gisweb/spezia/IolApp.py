from zope.component import adapts
from zope.interface import Interface, implements, Attribute

from plone import api
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFPlomino.interfaces import IPlominoDocument, IPlominoForm
from Products.CMFPlomino.PlominoEvents import PlominoSaveEvent
from zope.event import notify
from zope.component import getGlobalSiteManager
import config
from zope.component import getUtility
from .interfaces import IIolApp
from iol.gisweb.utils.config import USER_CREDITABLE_FIELD,USER_UNIQUE_FIELD,IOL_APPS_FIELD,STATUS_FIELD,IOL_NUM_FIELD,APP_FIELD


class IolApp(object):
    implements(IIolApp)
    adapts(IPlominoForm,IPlominoDocument)
    tipo_app = u""
    security = ClassSecurityInfo()
    security.declareObjectPublic()
    def __init__(self,obj):
        self.document = obj
        self.tipo_app = self.document.getItem(config.APP_FIELD,config.APP_FIELD_DEFAULT_VALUE)

    def __call__(self, *args, **kwargs):
        pass    

    security.declarePublic('cloneFiera')
    def clonaFiera(self,doc,anno,fiera,nuovo_anno):         
        utils = getUtility(IIolApp,self.tipo_app)
        return utils.clonaFiera(doc,anno,fiera,nuovo_anno)

    security.declarePublic('NuovoNumeroPratica')
    def NuovoNumeroPratica(self):
        utils = getUtility(IIolApp,self.tipo_app)
        return utils.NuovoNumeroPratica(self.document)    

    security.declarePublic('numerazione')
    def numerazione(self,doc,item_name,query):
        app = 'default' 
        utils = getUtility(IIolApp,app)
        return utils.numerazione(doc,item_name,query)


         


InitializeClass(IolApp)