# -*- coding: utf-8 -*-
import os
from zope.interface import implements

from iol.gisweb.spezia.interfaces import IIolApp,IIolPraticaWeb

from AccessControl import ClassSecurityInfo
import simplejson as json

from DateTime import DateTime

from base64 import b64encode

from iol.gisweb.utils.config import USER_CREDITABLE_FIELD,USER_UNIQUE_FIELD,IOL_APPS_FIELD,STATUS_FIELD,IOL_NUM_FIELD
from iol.gisweb.utils.IolDocument import IolDocument
from iol.gisweb.utils import loadJsonFile,dateEncoder
from iol.gisweb.spezia.IolApp import IolApp

class regolarizzazioneApp(object):
    implements(IIolApp)
    security = ClassSecurityInfo()
    def __init__(self):
        self.file = 'regolarizzazione'
        self.path = os.path.dirname(os.path.abspath(__file__))

    #Returns new number
    security.declarePublic('NuovoNumeroPratica')

    def NuovoNumeroPratica(self, obj):
        idx = obj.getParentDatabase().getIndex()
        query = dict(IOL_NUM_FIELD=dict(query=0, range='min'), iol_tipo_app='regolarizzazione')

        brains = idx.dbsearch(query, sortindex=IOL_NUM_FIELD, reverse=1, only_allowed=False)
        if not brains:
            nuovoNumero = 1
        else:
            nuovoNumero = (brains[0].getObject().getItem(IOL_NUM_FIELD,0) or 0) +1

        return nuovoNumero
    
    security.declarePublic('inviaSmtpMail')
    def inviaSmtpMail(self,obj,ObjectId,to=[],cc=[],bcc=[]):
        
        doc = obj        
        db = doc.getParentDatabase()
        iDoc = IolApp(doc)
        diz_mail = iDoc.getConvDataMail('mail_%s' %('regolarizzazione'))

        try:
            dpres = doc.getItem('data_presentazione','').strftime('%d/%m/%Y')
        except:
            dpres = ''

        try:
            dprot = doc.getItem('data_protocollo','').strftime('%d/%m/%Y')
        except:
            dprot = ''

        msg_info = dict(
            numero_pratica = doc.getItem('numero_pratica',''),
            titolo = doc.Title(),
            now = DateTime().strftime('%d/%m/%Y'),
            istruttore = doc.getItem('istruttore',''),
            numero_protocollo = doc.getItem('numero_protocollo',''),
            data_protocollo = dprot,
            link_pratica = doc.absolute_url(),
            data_presentazione = dpres,
            istruttoria_motivo_sospensione = doc.getItem('istruttoria_motivo_sospensione',''),
            nome_app = doc.getItem('iol_tipo_app',''),
            richiedente_nome = doc.getItem('fisica_nome',''),
            richiedente_cognome = doc.getItem('fisica_cognome','')
        )
        args = dict(to = [doc.getItem('progettista_pec','')])
       
        custom_args = dict()
        bodyMail = diz_mail["mail"][ObjectId]             
        oggetto = bodyMail["object"] %(msg_info)
        testo = bodyMail["text"] %(msg_info)
        allegati = {bodyMail["attach"]}       

        return IolDocument(doc).smtpMail(data = diz_mail['config'],to = args['to'],oggetto = oggetto,testo = testo,cc=[],bcc=[])


    security.declarePublic('sendThisMail')
    def sendThisMail(self,obj,ObjectId, sender='', debug=0,To='',password=''):        
        doc = obj

        db = doc.getParentDatabase()
        iDoc = IolApp(doc)
        diz_mail = iDoc.getConvData('mail_%s' %('regolarizzazione'))
        
        msg_info = dict(numero_pratica = doc.getItem('numero_pratica'),titolo = doc.Title(),
        now = DateTime().strftime('%d/%m/%Y'),istruttore = doc.getItem('istruttore'),numero_protocollo = doc.getItem('numero_protocollo'),data_protocollo = doc.getItem('data_protocollo'),
        link_pratica = doc.absolute_url(), data_pratica = doc.getItem('data_pratica'), istruttoria_motivo_sospensione = doc.getItem('istruttoria_motivo_sospensione'), nome_app = doc.getItem('iol_tipo_app'),richiedente_nome = doc.getItem('fisica_nome'),richiedente_cognome = doc.getItem('fisica_cognome'))
        args = dict(To = doc.getItem('progettista_pec') if To == '' else To,From = sender,as_script = debug)
        custom_args = dict()
        
        if not args['To']:

            plone_tools = getToolByName(doc.getParentDatabase().aq_inner, 'plone_utils')
            msg = ''''ATTENZIONE! Non e' stato possibile inviare la mail perche' non esiste nessun destinatario'''
            plone_tools.addPortalMessage(msg, request=doc.REQUEST)
            
        attach_list = doc.getFilenames()
        
        if ObjectId in diz_mail.keys():
            
            if diz_mail[ObjectId].get('attach') != "":
                msg_info.update(dict(documenti_autorizzazione = doc.getItem('documenti_autorizzazione')))                 
                msg_info.update(dict(attach = diz_mail[ObjectId].get('attach')))

                custom_args = dict(Object = diz_mail[ObjectId].get('object') % msg_info,
                msg = doc.mime_file(file = '' if not msg_info.get('attach') in attach_list else doc[msg_info['attach']], text = diz_mail[ObjectId].get('text') % msg_info, nomefile = diz_mail[ObjectId].get('nomefile')) % msg_info)
            else:                
                custom_args = dict(Object = diz_mail[ObjectId].get('object') % msg_info,
                msg = diz_mail[ObjectId].get('text') % msg_info)

        if custom_args:            
            args.update(custom_args)
            
            return IolDocument(doc).sendMail(**args)
        

class regolarizzazioneWsClient(object):
    implements(IIolPraticaWeb)
    security = ClassSecurityInfo()

    def __init__(self):
        self.resp_proc = 21
        self.resp_uo = 24
        self.file = 'regolarizzazione'
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.mapping = loadJsonFile("%s/mapping/%s.json" % (self.path,self.file)).result
        self.elenchi = loadJsonFile("%s/mapping/elenchi.json" % (self.path)).result

    security.declarePublic('getProcedimento')

    def getProcedimento(self, obj):
        doc = obj.document
        idoc = IolDocument(doc)
        pr = obj.client.factory.create('procedimento')
        pr.tipo = 32000
        pr.oggetto = doc.getItem('descrizione_opere','')
        nn = list()
        if doc.getItem('deroga_parere_estetico_opt',[]):
            nn += idoc.getLabels('deroga_parere_estetico_opt')
        if doc.getItem('deroga_art1_opt',[]):
            nn.append( "%s %s" %(idoc.getLabels('deroga_art1_opt')[0],doc.getItem('deroga_art1','')))
        if doc.getItem('deroga_art19_opt',[]):
            nn.append( "%s %s" %(idoc.getLabels('deroga_art19_opt')[0],doc.getItem('deroga_art19','')))
        if doc.getItem('deroga_art42_opt',[]):
            nn.append( "%s %s" %(idoc.getLabels('deroga_art42_opt')[0],doc.getItem('deroga_art42','')))
        pr.note = '\n'.join(nn)
        pr.protocollo = doc.getItem('numero_protocollo','')
        pr.data_prot = doc.getItem('data_prot',DateTime()).strftime("%d/%m/%Y")
        pr.data_presentazione = doc.getItem('data_presentazione',DateTime().strftime("%d/%m/%Y"))
        pr.online = 1
        pr.resp_proc = self.resp_proc
        pr.resp_uo = self.resp_uo
        pr.data_resp = DateTime().strftime("%d/%m/%Y")
        return pr

    def getSoggetti(self, obj):
        doc = obj.document
        idoc = IolDocument(doc)
        soggetti = list()
        ruoli = ['richiedente','proprietario','progettista','direttore','esecutore']
        # Recupero informazioni sui richiedenti/proprietari
        soggetto = obj.client.factory.create('soggetto')
        for i in ruoli:
            soggetto[i] = 0;
        mapfields = self.mapping['richiedente']
        for k, v in mapfields.items():
            if v:
                soggetto[k] = json.dumps(doc.getItem(v,None), cls=dateEncoder, use_decimal=True)

        soggetto['richiedente'] = 1
        soggetto['comunicazioni'] = 1
        if soggetto['sesso'] == 'Maschile':
            soggetto['sesso'] = 'M'
        else:
            soggetto['sesso'] = 'F'
        # Il richiedente è anche proprietario
        if doc.getItem('fisica_titolo', '').lower() == 'proprietario':
            soggetto['proprietario'] = 1
        soggetti.append(soggetto)
        for r in idoc.getDatagridValue('anagrafica_soggetti'):
            soggetto = obj.client.factory.create('soggetto')
            for i in ruoli:
                soggetto[i] = 0;
            for k, v in mapfields.items():
                if v:
                    if v in r.keys():
                        soggetto[k] = r[v]
                    else:
                        soggetto[k] = ''
            soggetto['richiedente'] = 1
            soggetto['comunicazioni'] = 1
            if soggetto['sesso'] == 'Maschile':
                soggetto['sesso'] = 'M'
            else:
                soggetto['sesso'] = 'F'
            # Il richiedente è anche proprietario
            if 'fisica_titolo' in r.keys():
                titolo = r['fisica_titolo']
            else:
                titolo = ''
            if titolo.lower() == 'proprietario':
                soggetto['proprietario'] = 1
            soggetti.append(soggetto)

        # Recupero informazioni sul progettista
        soggetto = obj.client.factory.create('soggetto')
        for i in ruoli:
            soggetto[i] = 0;
        mapfields = self.mapping['progettista']
        for k, v in mapfields.items():
            if v:
                value = doc.getItem(v,None)
                if isinstance(value,DateTime):
                    soggetto[k] = value.strftime("%d/%m/%Y")
                else:
                    soggetto[k] = value

        soggetto['progettista'] = 1
        soggetto['comunicazioni'] = 1
        if soggetto['sesso'] == 'Maschile':
            soggetto['sesso'] = 'M'
        else:
            soggetto['sesso'] = 'F'

        direttore = doc.getItem('direttore_opt','nodirettore')
        if direttore == 'direttoreesecutore':
            soggetto['direttore'] = 1
        soggetti.append(soggetto)
        # Il progettista è anche direttore lavori
        # Recupero informazioni sul direttore lavori

        if direttore == 'direttore':
            soggetto = obj.client.factory.create('soggetto')
            for i in ruoli:
                soggetto[i] = 0;
            mapfields = self.mapping['direttore']
            for k, v in mapfields.items():
                if v:
                    soggetto[k] = json.dumps(doc.getItem(v,None), cls=dateEncoder, use_decimal=True)
            soggetto['direttore'] = 1
            soggetto['comunicazioni'] = 1
            if soggetto['sesso'] == 'Maschile':
                soggetto['sesso'] = 'M'
            else:
                soggetto['sesso'] = 'F'
            soggetti.append(soggetto)

        # Recupero informazioni sugli esecutori se necessario
        if doc.getItem('lavori_economia_opt','economia') == 'economia':
            pass
        else:
            soggetto = obj.client.factory.create('soggetto')
            for i in ruoli:
                soggetto[i] = 0;
            mapfields = self.mapping['esecutore']
            for k, v in mapfields.items():
                if v:
                    soggetto[k] = json.dumps(doc.getItem(v,None), cls=dateEncoder, use_decimal=True)

            soggetto['esecutore'] = 1
            soggetto['comunicazioni'] = 1
            if soggetto['sesso'] == 'Maschile':
                soggetto['sesso'] = 'M'
            else:
                soggetto['sesso'] = 'F'

            soggetti.append(soggetto)
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

    def getIndirizzi(self, obj):
        doc = obj.document
        idoc = IolDocument(doc)
        results = list()
        elencoVie = dict()
        vie = obj.client.service.elencoVie()[2]
        for via in vie:
            elencoVie[str(via.value)] = str(via.label)

        mapfields = self.mapping['indirizzo']
        for r in idoc.getDatagridValue('elenco_civici'):
            fType = obj.client.factory.create('indirizzo')
            for k, v in mapfields.items():
                if v:
                    if k == 'via':
                        fType[k] = elencoVie[r[v]]
                    else:
                        fType[k] = r[v]
            results.append(fType)
        return results

    def getNCT(self, obj):
        doc = obj.document
        idoc = IolDocument(doc)
        results = list()
        mapfields = self.mapping['nct']
        for r in idoc.getDatagridValue('elenco_nct'):
            fType = obj.client.factory.create('particella')
            for k, v in mapfields.items():
                if v:
                    fType[k] = r[v]
            results.append(fType)
        return results

    def getNCEU(self, obj):
        doc = obj.document
        idoc = IolDocument(doc)
        results = list()
        mapfields = self.mapping['nceu']
        for r in idoc.getDatagridValue('elenco_nceu'):
            fType = obj.client.factory.create('particella')
            for k, v in mapfields.items():
                if v:
                    fType[k] = r[v]
            results.append(fType)
        return results

    def getAllegati(self, obj):
        doc = obj.document
        idoc = IolDocument(doc)
        results = list()
        mapfields = self.mapping['allegato']
        for k, v in mapfields.items():
            allegato = obj.client.factory.create('allegato')
            files_allegati = list()
            for el in v:
                f = idoc.getAttachmentInfo(el)
                if f:
                    for info in f:
                        file_allegato = obj.client.factory.create('file_allegato')
                        file_allegato.nome_file = info['name']
                        file_allegato.tipo_file = info['mimetype']
                        file_allegato.size_file = info['size']
                        #file_allegato.file = ''
                        file_allegato.file = info['b64file']
                        files_allegati.append(file_allegato)
                if doc.getItem('numero_protocollo'):
                    allegato.protocollo = doc.getItem('numero_protocollo')
                if doc.getItem('data_protocollo'):
                    allegato.data_protocollo = doc.getItem('data_protocollo')
                allegato.documento = k
                allegato.allegato = 1
                allegato.files = files_allegati
            if allegato.files and allegato.documento:
                results.append(allegato)
        return results

    def getProgetto(self,obj):
        doc = obj.document
        progetto = obj.client.factory.create('progetto')
        dval = doc.getItem('immobile_destinazione', '')
        progetto.destuso1 = self.elenchi['destuso'][dval]
        return progetto

    def getComunicazioneInizioLavori(self,obj):
        doc = obj.document
        lavori = obj.client.factory.create('lavori')
        doc.getItem('data_inizio_lavori','')
        lavori.il = doc.getItem('data_inizio_lavori')
        lavori.note = doc.getItem('note','')
        return lavori

    def getComunicazioneFineLavori(self,obj):
        doc = obj.document
        lavori = obj.client.factory.create('lavori')
        doc.getItem('data_fine_lavori','')
        lavori.fl = doc.getItem('data_fine_lavori')
        lavori.note = doc.getItem('note','')
        return lavori

