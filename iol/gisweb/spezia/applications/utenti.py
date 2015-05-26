from zope.interface import implements
from iol.gisweb.spezia.interfaces import IIolApp
from iol.gisweb.spezia.IolApp import IolApp
from zope import component
from AccessControl import ClassSecurityInfo
from plone import api

from gisweb.iol.permissions import IOL_READ_PERMISSION, IOL_EDIT_PERMISSION, IOL_REMOVE_PERMISSION
from gisweb.utils import  addToDate
from iol.gisweb.utils.config import USER_CREDITABLE_FIELD,USER_UNIQUE_FIELD,IOL_APPS_FIELD,STATUS_FIELD,IOL_NUM_FIELD
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime
from Products.CMFPlomino.PlominoUtils import DateToString, Now, StringToDate
from iol.gisweb.utils.IolDocument import IolDocument

class utentiApp(object):
    implements(IIolApp)
    security = ClassSecurityInfo()
    def __init__(self):
        pass
    def __call__(self, *args, **kwargs):
        pass
    
    security.declarePublic('inviaSmtpMail')
    def inviaSmtpMail(self,obj,ObjectId,to=[],cc=[],bcc=[]):
        
        doc = obj        
        db = doc.getParentDatabase()
        iDoc = IolApp(doc)
        diz_mail = iDoc.getConvDataMail('mail_%s' %('accreditamento'))

        msg_info = dict(numero_pratica = doc.getItem('numero_pratica'),titolo = doc.Title(),
        now = DateTime().strftime('%d/%m/%Y'),istruttore = doc.getItem('istruttore'),numero_protocollo = doc.getItem('numero_protocollo'),data_protocollo = doc.getItem('data_protocollo'),
        link_pratica = doc.absolute_url(), data_pratica = doc.getItem('data_pratica'), istruttoria_motivo_sospensione = doc.getItem('istruttoria_motivo_sospensione'), nome_app = doc.getItem('iol_tipo_app'),richiedente_nome = doc.getItem('fisica_nome'),richiedente_cognome = doc.getItem('fisica_cognome'))
        args = dict(to = [doc.getItem('fisica_email')] if to == [] else to)

        custom_args = dict()
        bodyMail = diz_mail["mail"][ObjectId]             
        oggetto = bodyMail["object"] %(msg_info)
        testo = bodyMail["text"] %(msg_info)
        allegati = {bodyMail["attach"]}       

        return IolDocument(doc).smtpMail(data = diz_mail['config'],to = args['to'],cc=[],bcc=[])

    security.declarePublic('sendThisMail')
    def sendThisMail(self,obj,ObjectId, sender='', debug=0,To='',password=''):
        doc = obj

        db = doc.getParentDatabase()
        iDoc = IolApp(doc)
        diz_mail = iDoc.getConvData('mail_%s' %('accreditamento'))        
        msg_info = dict(nome_app_richiesta = doc.getItem('nome_app_richiesta'),link_pratica = doc.absolute_url())
        args = dict(To = doc.getItem('fisica_email') if To == '' else To,From = sender,as_script = debug)
        custom_args = dict()
        
        if not args['To']:

            plone_tools = getToolByName(doc.getParentDatabase().aq_inner, 'plone_utils')
            msg = ''''ATTENZIONE! Non e' stato possibile inviare la mail perche' non esiste nessun destinatario'''
            plone_tools.addPortalMessage(msg, request=doc.REQUEST)
            
        attach_list = doc.getFilenames()
        
        if ObjectId in diz_mail.keys():
            
            if diz_mail[ObjectId].get('attach') != "":                
                msg_info.update(dict(attach = diz_mail[ObjectId].get('attach')))

                custom_args = dict(Object = diz_mail[ObjectId].get('object') % msg_info,
                msg = doc.mime_file(file = '' if not msg_info.get('attach') in attach_list else doc[msg_info['attach']], text = diz_mail[ObjectId].get('text') % msg_info, nomefile = diz_mail[ObjectId].get('nomefile')) % msg_info)
            else:                
                custom_args = dict(Object = diz_mail[ObjectId].get('object') % msg_info,
                msg = diz_mail[ObjectId].get('text') % msg_info)      
        if custom_args:            
            args.update(custom_args)
            
            return IolDocument(doc).sendMail(**args)