from Products.CMFCore.utils import getToolByName
from plone.dexterity.browser.view import DefaultView
from plone import api
from zope.event import notify
from zope.component import getGlobalSiteManager
from zope.component import getUtility
from iol.gisweb.spezia.IolApp import IolApp
from five import grok
from Products.CMFPlomino.interfaces import IPlominoDocument
from AccessControl import ClassSecurityInfo
from datetime import datetime
import simplejson as json
# 
class clonaFiera(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self,anno='',fiera='',nuovo_anno=''):
        doc = self.aq_parent
        db = doc.getParentDatabase()
        idx = db.getIndex()      
        fiera = self.request.get('fiera')        
        anno = self.request.get('anno')        
        
               
        result = idx.dbsearch({'Form':'frm_fiera','fiera':fiera,'anno':int(anno)})
        
        if len(result)>0:
            nuovo_anno = self.request.get('nuovo_anno') 
            doc_old = result[0].getObject().getId()
                   
            iApp = IolApp(doc)
            doc_old = db.getDocument(doc_old)     
                      
            return iApp.clonaFiera(doc_old,anno,fiera,nuovo_anno)
        else:
            return 'vuoto'

class numerazione(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self,item_name='',query={}):
        doc = self.aq_parent
        item_name = self.request.get('item_name')
        query = self.request.get('query') or {}
        iApp = IolApp(doc)
        return iApp.numerazione(doc,item_name,query)

class stampaFattura(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        doc = self.aq_parent        
        iApp = IolApp(doc)
        return iApp.stampaFattura()


security = ClassSecurityInfo()
security.declarePublic('stampaElencoFattureFile')

class stampaElencoFattureFile(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def __call__(self,inizio,fine):                 
        db = self.aq_parent       
               
        inizio = int(self.request.get('inizio'))
        fine = int(self.request.get('fine'))        
        idx = db.getIndex()
        results = idx.dbsearch({'Form':'frm_posteggio','numero_fattura':{'query':[inizio,fine],'range':'min:max'}},sortindex='numero_fattura')

        campi = ['occupante_cognome','occupante_nome','occupante_indirizzo','occupante_cap','occupante_comune','occupante_cf','occupante_piva','','','numero_fattura','data_fattura','fattura_print','fiera_descrizione','quota_perc_iva_print','iva_print','imponibile_print','quota_esente_posta','','','','','','','','',''] 
                          
        header = '''COGNOME NOME    INDIRIZZO   CAP CITTA   CODICE_FIS  PARTITAIVA  MOD_PAG RIF_PROVV   NUM_FATT    DATA_FATT   TOTALE_FAT  DESCRIZ PERC_IVA_1  IMPORTO_IVA IMPONIB_1   QUOTA_POSTALE   PERC_IVA_2  IMPOSTA_2   IMPONIB_2   PERC_IVA_3  IMPOSTA_3   IMPONIB_3   DATA_SCAD   CDR SEZ_IVA'''
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
                    if doc.getItem(campo,"")!=None:    
                        if campo == 'data_fattura':
                            data_fattura = doc.getItem(campo) 
                            if data_fattura:
                                data_fat = data_fattura.strftime('%d/%m/%Y')  
                            else:
                                data_fat = ""                     
                         
                            row.append(data_fat)
                        else:
                            val = doc.getItem(campo,"")    
                            if isinstance(val,basestring):
                                row.append(val.upper())
                            else: 
                                row.append(str(val))
                    else:
                        row.append("")      
                elif campo in itemsFiera:
                    if doc.getItem(campo,"")!=None:    
                        row.append("%s" %(doc.getItem(campo,"")))
                    else:
                        row.append("")   
                else:
                    row.append("")
            tot.append(row)

        st = '%s\n' %(header)   
        for i in tot:    
            st += '%s\n' %('\t'.join(i))        
        self.request.RESPONSE.headers['Content-type']='application/text' 
        self.request.RESPONSE.headers['Content-Disposition']='attachment;filename=elenco_fatture.txt'  
        return st

class stampaElencoGraduatoria(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def __call__(self,fiera):                 
        db = self.aq_parent
        
        fiera = self.request.get('fiera')
        graduatoria = db.resources.graduatoriaNoProprietari(fiera)
        header = '''Posizione;Nominativo;Presenze;Data inizio attivita'''      
        if graduatoria != dict():
            testo = '%s\n' %(header)
            for row in graduatoria['names']:
                posizione = row['n']
                cognome = row['graduato_cognome']
                nome = row['graduato_nome']
                punteggio = row['punteggio']
                data_registrazione = row['data_registrazione']
                row_text = ['%s;%s %s;%s;%s' %(posizione,cognome,nome,punteggio,data_registrazione)]
                testo += '%s\n' %(';'.join(row_text))
            self.request.RESPONSE.headers['Content-type']='application/vnd.ms-excel'
            self.request.RESPONSE.headers['Content-Disposition']='attachment;filename=graduatoriaFiera%s.csv' %(fiera)   
        return testo    





