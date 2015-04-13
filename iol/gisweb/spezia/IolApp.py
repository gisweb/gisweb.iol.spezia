from zope.component import adapts
from zope.interface import Interface, implements, Attribute

from plone import api
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFPlomino.interfaces import IPlominoDocument, IPlominoForm
from Products.CMFPlomino.PlominoEvents import PlominoSaveEvent
from zope.event import notify
from zope.component import getGlobalSiteManager
import simplejson as json
import config
import DateTime
import datetime
from iol.gisweb.utils import config

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

    security.declarePublic('stampaFattura')
    def stampaFattura(self):
        utils = getUtility(IIolApp,self.tipo_app)
        return utils.stampaFattura(self.document)

        
    security.declarePublic('printModelli')
    def printModelli(self,db_name='',grp='autorizzazione',field='documenti_autorizzazione', folder='modelli'):
        doc = self.document
        db = db_name.split('_')[-1]
        for obj in doc.getParentDatabase().aq_parent.listFolderContents():
            if obj.getId()==folder:
                folder= obj 
        dizFile={}
        try:
            for i in folder.getFolderContents():
                obj=i.getObject()
                if db in obj.getId():                
                    sub_folders = obj.getFolderContents()                
                    pathFolder = [i.getObject().absolute_url() for i in sub_folders if grp in i.getObject().getId()][0]            
                    fileNames = [i.getObject().keys() for i in sub_folders if grp in i.getObject().getId()][0]   
                    
                    if len(fileNames)>0:                    
                        dizFile={}
                        for fileName in fileNames:
                            diz={}
                            pathModel= '%s/%s' %(pathFolder,fileName)
                            
                            diz['model']= pathModel
                            diz['field']=field                        
                            dizFile[fileName]=diz
                            dizFile['success']=1                          
                    else:
                       
                        dizFile['model']='test'
                        dizFile['field']=field
                        
                    return json.dumps(dizFile,default=DateTime.DateTime.ISO,use_decimal=True)
        except:
            dizFile['success']=0
            return json.dumps(dizFile,default=DateTime.DateTime.ISO,use_decimal=True)
    
         


InitializeClass(IolApp)
