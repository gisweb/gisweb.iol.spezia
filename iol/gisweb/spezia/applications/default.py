from zope.interface import implements
from iol.gisweb.spezia.interfaces import IIolApp, IIolPraticaWeb
from plone import api
from zope import component
from AccessControl import ClassSecurityInfo
from Products.Archetypes.utils import make_uuid
from DateTime import DateTime
import time
from zope.event import notify
from zope.component import getGlobalSiteManager
from Products.CMFPlomino.PlominoEvents import PlominoSaveEvent
from Products.CMFPlomino.PlominoUtils import json_loads
from iol.gisweb.utils.config import USER_CREDITABLE_FIELD,USER_UNIQUE_FIELD,IOL_APPS_FIELD,STATUS_FIELD,IOL_NUM_FIELD,APP_FIELD
import os
import simplejson as json


class defaultApp(object):
    implements(IIolApp)
    security = ClassSecurityInfo()
    def __init__(self):
        pass
    def __call__(self, *args, **kwargs):
        pass

    

    security.declarePublic('NuovoNumeroPratica')
    def NuovoNumeroPratica(self,obj):        
        idx = obj.getParentDatabase().getIndex()
        query = dict(IOL_NUM_FIELD = dict(query=0, range='min'))
        brains = idx.dbsearch(query, sortindex=IOL_NUM_FIELD, reverse=1, only_allowed=False)
        if not brains:
            nuovoNumero = 1
        else:
            nuovoNumero = (brains[0].getObject().getItem(IOL_NUM_FIELD,0) or 0) +1

        return nuovoNumero

    security.declarePublic('numerazione')
    def numerazione(self,doc,item_name,query):
        if isinstance(query, basestring):
            query = json_loads(query)
        query.update({item_name: dict(query=0, range='min')})                
        db = doc.getParentDatabase()
        res = db.getIndex().dbsearch(query, sortindex=item_name, reverse=1, only_allowed=False)
        massimo = max([0]+[getattr(i, item_name) for i in res])
        return massimo + 1
    
    security.declarePublic('stampaElencoFattureFile')
    def stampaElencoFattureFile(self,obj,inizio='',fine=''):
        inizio = int(obj.REQUEST.get('inizio'))
        fine = int(obj.REQUEST.get('fine'))
        db = obj.getParentDatabase()
        idx = db.getIndex()
        results = idx.dbsearch({'Form':'frm_posteggio','numero_fattura':{'query':[inizio,fine],'range':'min:max'}})

        campi= ['occupante_cognome','occupante_nome','occupante_indirizzo','occupante_cap','occupante_comune','occupante_cf','occupante_piva','','','numero_fattura','data_fattura ','fattura','fiera_descrizione','quota_perc_iva','','imponibile','','','','','','','','','','']
                          
        header = '''COGNOME;NOME;INDIRIZZO;CAP;CITTA;CODICE_FIS;PARTITAIVA;MOD_PAG;RIF_PROVV;NUM_FATT;DATA_FATT;TOTALE_FAT;
        DESCRIZ;PERC_IVA_1;IMPOSTA_1;IMPONIB_1;PERC_IVA_2;IMPOSTA_2;IMPONIB_2;PERC_IVA_3;IMPOSTA_3;IMPONIB_3;DATA_SCAD;CDR;SEZ_IVA'''
        tot=[]
        for res in results:
            ob = res.getObject()
            docId = ob.getId()
            doc = db.getDocument(docId)
            posteggio = db.getForm('frm_posteggio')
            fiera = db.getForm('frm_fiera')
            row = []
            for indx,campo in enumerate(campi):
                 itemsPosteggio = [i.getId() for i in posteggio.getFormFields(includesubforms=True)]
                 itemsFiera = [i.getId() for i in fiera.getFormFields(includesubforms=True)]
                 if campo in itemsPosteggio:
                     if doc.getItem(campo,'')!=None:    
                         row.append(str(doc.getItem(campo,'')))
                     else:
                         row.append('')      
                 elif campo in itemsFiera:
                     if doc.getItem(campo,'')!=None:    
                         row.append(str(doc.getItem(campo,'')))
                     else:
                         row.append('')   
                 else:
                     row.append('')
            tot.append(row)
        st = '%s\n\r' %(header) 
        for i in tot:    
            st += '%s\n\r' %(';'.join(i))
        doc.REQUEST.RESPONSE.headers['Content-type']='application/vnd.ms-excel' 
        doc.REQUEST.RESPONSE.headers['Content-Disposition']='attachment;filename=elenco_fatture.csv'  
        return st

    #Procedure that search all documents of the selected user, assign him ownership, and move him in iol groups
    security.declarePublic('accreditaUtente')
    def accreditaUtente(self,obj):
        user = obj.getOwner()
        username = user.getUserName()
        apps = obj.getItem(IOL_APPS_FIELD,[])  
                                                                                                                                                                                                                 
        self._assignGroups(obj,username,apps)

        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(portal_type='PlominoDatabase')
        unique = obj.getItem(USER_UNIQUE_FIELD,'')
        cont = 0
        brains = []
        for brain in brains:
            db = brain.getObject()
            idx = db.getIndex()
            req = dict(USER_CREDITABLE_FIELD = unique)
            for br in idx.dbsearch(req,only_allowed=False):
                doc = br.getObject()
                self._assignOwner(doc,user)
                cont += 1
        return cont

    def getConvData(self,json_file):
        fName = "%s/mapping/%s.json" %(os.path.dirname(os.path.abspath(__file__)),json_file)
        
        if os.path.isfile(fName):
            json_data=open(fName)

            try:
                data = json.load(json_data)

            except ValueError, e:
                data = str(e)
                json_data.close()
               
        else:
            return fName
            data = dict()
        return data

    def getConvDataMail(self,json_file):
        fName = "%s/mail/%s.json" %(os.path.dirname(os.path.abspath(__file__)),json_file)
        if os.path.isfile(fName + ".local"):
            json_data=open(fName + ".local")
            try:
                data = json.load(json_data)

            except ValueError, e:
                data = str(e)
                json_data.close()

        elif os.path.isfile(fName):
            json_data=open(fName)

            try:
                data = json.load(json_data)

            except ValueError, e:
                data = str(e)
                json_data.close()
               
        else:
            return fName
            data = dict()
        return data        

    security.declarePublic('createPdf')
    def createPdf(selfself,obj,filename,itemname,overwrite):
        filename = '%s.pdf' % filename or obj.REQUEST.get('filename') or obj.getId()

        try:
            res = obj.restrictedTraverse('@@wkpdf').get_pdf_file()
        except Exception as err:

            msg1 = "%s" % (str(err))
            msg2 = "Attenzione! Non e' stato possibile allegare il file: %s" % filename
            api.portal.show_message(message=msg1, request=obj.REQUEST,type='error')
            api.portal.show_message(message=msg2, request=obj.REQUEST,type='warning')
        else:
            (f,c) = obj.setfile(res,filename=filename,overwrite=overwrite,contenttype='application/pdf')
            if f and c:
                old_item = obj.getItem(itemname, {}) or {}
                old_item[filename] = c
                obj.setItem(itemname, old_item)        
    
    security.declarePublic('updateStatus')
    def updateStatus(self,obj):
        obj.setItem(STATUS_FIELD,api.content.get_state(obj=obj) )
        self.reindex_doc(obj)

    security.declarePublic('reindex_doc')
    def reindex_doc(self,obj):
        db = obj.getParentDatabase()
        # update index
        db.getIndex().indexDocument(obj)
        # update portal_catalog
        if db.getIndexInPortal():
            db.portal_catalog.catalog_object(obj, "/".join(db.getPhysicalPath() + (obj.getId(),)))    




class defaultWsClient(object):
    implements(IIolPraticaWeb)
    security = ClassSecurityInfo()
    def __init__(self):
        pass

    security.declarePublic('getProcedimento')
    def getProcedimento(self,obj):
        pr = obj.client.factory.create('procedimento')
        return pr

    def getSoggetti(self,obj):
        ftype = obj.client.factory.create('soggetto')
        return ftype

    def getIndirizzi(self,obj):
        ftype = obj.client.factory.create('indirizzo')
        return ftype

    def getCT(self,obj):
        ftype = obj.client.factory.create('particella')
        return ftype

    def getCU(self,obj):
        ftype = obj.client.factory.create('particella')
        return ftype
    def getEsecutori(self,obj):
        soggetti = list()
        doc = obj.document
        idoc = IolDocument(doc)
        app = idoc.getIolApp()

        path = os.path.dirname(os.path.abspath(__file__))
        mapping = loadJsonFile("%s/mapping/%s.json" % (path,app)).result

        ruoli = ['richiedente','proprietario','progettista','direttore','esecutore']
        mapfields = mapping['esecutore']
        for r in idoc.getDatagridValue('altri_esecutori_grid'):
            soggetto = obj.client.factory.create('soggetto')
            for i in ruoli:
                soggetto[i] = 0;
            for k, v in mapfields.items():
                if v:
                    if v in r.keys():
                        soggetto[k] = r[v]
                    else:
                        soggetto[k] = ''
            soggetto['esecutore'] = 1
            soggetto['comunicazioni'] = 1
            if soggetto['sesso'] == 'Maschile':
                soggetto['sesso'] = 'M'
            else:
                soggetto['sesso'] = 'F'
            soggetti.append(soggetto)
        return soggetti
            

#############################################################################
app = defaultApp()
gsm = component.getGlobalSiteManager()
gsm.registerUtility(app, IIolApp, 'default')