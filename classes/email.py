#
# Script para Executar backup do servidor
# Classe de manipulação de email
#
# Autor......: Gustavo Marucci <gustavo@marucciviana.com.br>
# Date.......: 18/03/2024
#

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List

class Email(object):

    # Properties
    template:       str | None = None
    remetente:      str | None = None
    usuario:        str | None = None
    senha:          str | None = None
    servidor:       str | None = None
    porta:          int | None = 587
    destinatarios:  List[str] | str = []


    # Objects
    msg             = MIMEMultipart()
    email_server    = None

    # Methods
    def __init__(
            self, 
            template:       str | None = None,
            remetente:      str | None = None, 
            destinatarios:   List[str] | str = [], 
            servidor:       str | None = None, 
            porta:          int | None = None,
            usuario:        str | None = None,
            senha:          str | None = None
        ):
        '''
        Método construtor
        
        '''
        if remetente:       self.remetente      = remetente
        if destinatarios:    self.destinatarios   = destinatarios
        if servidor:        self.servidor       = servidor
        if porta:           self.porta          = porta
        if usuario:         self.usuario        = usuario
        if senha:           self.senha          = senha

        if template:
            self.template = self.read_template(template)

        if not self.incomplete_config():
            self.config()
                

    def incomplete_config(self) -> bool:
        ''''
        incomplete_config
        Checa se as configurações de email estão vazias

        '''
        return (not self.remetente) | (not self.destinatarios) | (not self.servidor) | (not self.usuario) | (not self.senha)


    def read_template(self, template: str) -> str | None:
        '''
        read_template
        Lê o template HTML para que o email seja enviado nesse formato
        
        '''
        try:
            path            = os.path.dirname(os.path.realpath(__file__))
            template_file   = os.path.join(path, "..", "templates", template)
            with open(template_file, "r") as file:
                return file.read()
            
        except Exception as e:
            print(f"Ops... Alguma coisa deu errada ao ler o template. A mensagem: {str(e)}")
            return None


    def config(self) -> None:
        '''
        config
        Método que configura o serviço com os parâmetros fornecedos

        '''
        self.msg['From']        = self.remetente
        self.msg['To']          = self.destinatarios if isinstance(self.destinatarios, str) else ", ".join(self.destinatarios)


    def send(self, assunto: str, corpo: str = "", pre: str = "",) -> bool:
        '''
        send
        Envia o email com o assunto e o corpo especificado

        '''
        self.msg['Subject'] = assunto

        if self.template:
            text    = self.template.replace("__PRE__", pre)
            text    = text.replace("__BODY__", corpo)
            self.msg.attach(MIMEText(text, 'html'))
            

        else:
            self.msg.attach(MIMEText(corpo, 'plain')) 
        
        try:       
            self.email_server = smtplib.SMTP(self.servidor, self.porta)
            self.email_server.starttls()
            self.email_server.login(self.usuario, self.senha)

            email_payload = self.msg.as_string()
            self.email_server.sendmail(self.remetente, self.destinatarios, email_payload)
            self.email_server.quit()
            return True
        
        except Exception as e:
            print(f"Alguma coisa deu errado no envio do email. Mensagem: {str(e)}")
            return False

