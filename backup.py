#
# Script para Executar backup do servidor
#
# Autor......: Gustavo Marucci <gustavo@marucciviana.com.br>
# Date.......: 18/03/2024
#

import os
import sys
import json
from time           import time
from classes.email  import Email
from classes.copy   import Copy

start_running   = 0
eml             = None

msg_sucesso     = """
<p>Olá Administrador!</p>
<p>Esse e-mail é para informar que o backup foi realizado com SUCESSO!</p>
<p>Você deve agora retirar o HD do servidor e executar um processo de verificação da cópia para certificar que tudo esteja Ok.</p>
<hr/>
<p>
<b>Tempo de execução do backup:</b> __TIME__
</p>
"""

msg_erro        = """
<p>Olá Administrador!</p>
<p>Esse e-mail é para informar que o backup FALHOU. Você deve tomar as ações necessárias para remediar o incidente</p>
<p>A seguinte mensagem foi apresentada:</p>
<p>"__MSG__"</p>
<hr/>
<p>
<b>Tempo de execução do backup:</b> __TIME__
</p>
"""

def exit(errorlevel, message):
    '''
    exit
    Encerra o script
    
    '''
    time_running = int(time() - start_running)

    if eml:
        if errorlevel == 0:
            subject = "Backup realizado com sucesso"
            msg = msg_sucesso.replace("__TIME__", format_time(time_running))
            eml.send(
                subject, 
                msg,
                subject
            )

        else:
            subject = "Backup falhou"
            msg = msg_erro.replace("__TIME__", format_time(time_running))
            msg = msg.replace("__MSG__", message)
            eml.send(
                subject, 
                msg,
                subject
            )

    print(message)
    print("Fim da execução")
    sys.exit(errorlevel)


def format_time(total_seconds):
    '''
    format_time
    Formata o output do tempo de processamento

    '''
    if total_seconds < 60:
        return f"{total_seconds} segundo(s)"
    
    elif total_seconds < 3600:
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        if seconds == 0:
            return f"{minutes} minuto(s)"
        else:
            return f"{minutes} minuto(s) e {seconds} segundo(s)"
        
    elif total_seconds < 86400:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        if seconds == 0:
            return f"{hours} hora(s)"
        else:
            return f"{hours} hora(s), {minutes} minuto(s) e {seconds} segundo(s)"
        
    else:
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        if minutes == 0 and seconds == 0:
            return f"{days} dias e {hours} hora(s)"
        elif minutes == 0:
            return f"{days} dias, {hours} hora(s) e {seconds} segundos"
        elif seconds == 0:
            return f"{days} dias, {hours} hora(s) e {minutes} minuto(s)"
        else:
            return f"{days} dias, {hours} hora(s), {minutes} minuto(s) e {seconds} segundo(s)"


if __name__ == "__main__":
    '''
    função principal

    '''
    start_running = time()
    print("Iniciando o Script de Backup")

    print("Lendo o arquivo de configuração...")
    try:
        path        = os.path.dirname(os.path.realpath(__file__))
        config_file = os.path.join(path, "etc", "backup.config.json")
        with open('./etc/backup.config.json') as f:
            config = json.loads(f.read())

    except Exception as e:
        exit(2, f"O arquivo de configuração '{config_file}' não pode ser lido. Pode ser que ele não exista ou tenha problemas de permissão. A mensagem foi: {str(e)}")

    print("Configurando o envio de email...")
    try:
        eml = Email(
            remetente       = config['remetente'],
            destinatarios   = config['destinatarios'],
            servidor        = config['smtp_host'],
            porta           = config['smtp_porta'],
            usuario         = config['smtp_user'],
            senha           = config['smtp_senha'],
            template        = config['template']
        )

    except Exception as e:
        eml = None
        exit(1, f"O arquivo de configuração '{config_file}' está mal formado. A mensagem foi: {str(e)}")

    print("Preparando o backup...")
    try:
        copy = Copy(
           drive_letter=config['backup']['drive']
        )

        # Cria um snapshot do disco
        copy.create_snapshot()

    except Exception as e:
        exit(1, f"O arquivo de configuração '{config_file}' está mal formado. A mensagem foi: {str(e)}")


    print("Copiando os arquivos...")
    try:
        copy = Copy(
           drive_letter=config['backup']['drive']
        )

        # Cria um snapshot do disco
        success, msg = copy.run(config['backup']['pasta'], config['backup']['destino'])

        if not success:
            exit(1, msg)

    except Exception as e:
        exit(1, f"A copia falhou. A mensagem foi: {str(e)}")

    exit(0, "Backup realizado com sucesso")
