from zope.component import adapts
from zope.interface import Interface, implements, Attribute

from plone import api
import os
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
from iol.gisweb.utils.IolDocument import IolDocument
from iol.gisweb.utils import loadJsonFile,dateEncoder
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
        iDoc = IolDocument(obj)
        self.tipo_app = iDoc.getIolApp()
        self.path = os.path.dirname(os.path.abspath(__file__))

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

    security.declarePublic('invioPraticaweb')
    def invioPraticaweb(self):
        utils = queryUtility(IIolApp,name=self.tipo_app, default=config.APP_FIELD_DEFAULT_VALUE)
        if not 'invioPraticaweb' in dir(utils):
            utils = getUtility(IIolApp,config.APP_FIELD_DEFAULT_VALUE)        
        return utils.invioPraticaweb(self.document)    

    security.declarePublic('accreditaUtente')
    def accreditaUtente(self):
        utils = queryUtility(IIolApp,name=self.tipo_app, default=config.APP_FIELD_DEFAULT_VALUE)
        if not 'accreditaUtente' in dir(utils):
            utils = getUtility(IIolApp,config.APP_FIELD_DEFAULT_VALUE)        
        return utils.accreditaUtente(self.document)

    security.declarePublic('createPdf')
    def createPdf(self,filename,itemname='documento_da_firmare',overwrite=False):
        utils = queryUtility(IIolApp,name=self.tipo_app, default=config.APP_FIELD_DEFAULT_VALUE)
        if not 'createPdf' in dir(utils):
            utils = getUtility(IIolApp,config.APP_FIELD_DEFAULT_VALUE)        
        return utils.createPdf(self.document,filename,itemname,overwrite)
    
    security.declarePublic('getConvData')
    def getConvData(self,json_data):
        utils = getUtility(IIolApp,'default')
        return utils.getConvData(json_data)
    
    security.declarePublic('getConvDataMail')
    def getConvDataMail(self,json_data):
        utils = getUtility(IIolApp,'default')
        return utils.getConvDataMail(json_data)

    security.declarePublic('inviaSmtpMail')
    def inviaSmtpMail(self,ObjectId,to=[],cc=[],bcc=[]):               
        utils = getUtility(IIolApp,self.tipo_app)        
        return utils.inviaSmtpMail(self.document,ObjectId,to=[],cc=[],bcc=[])

    security.declarePublic('sendThisMail')
    def sendThisMail(self,ObjectId,sender='',debug=0,To='',password=''):               
        utils = getUtility(IIolApp,self.tipo_app)        
        return utils.sendThisMail(self.document,ObjectId,sender,debug,To,password)      

    security.declarePublic('updateStatus')
    def updateStatus(self):
        utils = queryUtility(IIolApp,name=self.tipo_app, default=config.APP_FIELD_DEFAULT_VALUE)
        if not 'updateStatus' in dir(utils):
            utils = getUtility(IIolApp,config.APP_FIELD_DEFAULT_VALUE)
        return utils.updateStatus(self.document)

    security.declarePublic('reindex_doc')
    def reindex_doc(self):
        utils = queryUtility(IIolApp,name=self.tipo_app, default=config.APP_FIELD_DEFAULT_VALUE)
        if not 'reindex_doc' in dir(utils):
            utils = getUtility(IIolApp,config.APP_FIELD_DEFAULT_VALUE)
        return utils.reindex_doc(self.document) 

    # Wizard Info
    security.declarePublic('getWizardInfo')

    def getWizardInfo(self):
        doc = self.document
        # Inizializzo il risultato
        result = dict(
            actions=[],
            state="",
            base_url="%s/content_status_modify?workflow_action=" % (doc.absolute_url()),
            forms=[]
        )
        #Istanzio l'oggetto IolDocument

        iDoc = IolDocument(doc)
        info = loadJsonFile("%s/applications/wizard_info/%s.json" % (self.path, self.tipo_app)).result

        wfInfo = iDoc.wfInfo()
        if doc.portal_type == 'PlominoForm':
            result["state"] = info["initial_state"]
            result["actions"] = info["initial_actions"]
        else:
            result["state"] = wfInfo["wf_state"]
            result["actions"] = wfInfo["wf_actions"]
        for v in info["states"]:
            cls_list = list()
            if not iDoc.isActionSupported(v["action"]):
                cls_list.append('link-disabled')
                action = ""
            else:
                action = v["action"]
            if result["state"] == v["state"]:
                cls_list.append("active")

            i = {"label": v["label"], "class": " ".join(cls_list), "action": action}
            result["forms"].append(i)
        return result    

        
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
