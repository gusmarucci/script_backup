# Script para execução de Backup

Este script verifica se existe uma unidade removível no servidor, cria um snapshot do disco de onde os dados estão, copia os dados e então apaga o snapshot criado.
Portanto, não importa se o arquivo estiver aberto, ele fará uma cópia segura.
Após o procedimento de backup, então, o script envia um e-mail informando se os dados foram copiados com sucesso ou não. Caso negativo, ele envia no e-mail a mensagem de erro.


# Configuração

O script é um arquivo Python, portanto, o servidor precisa ter instalado o Python versão 3.10 ou superior bem como as dependências do script,

## Instalando as dependências

Devidamente instalado o Python no servidor, com o serviço PIP devidamente inserido (no processo de instalação você certifica que o PIP será instalado também), basta digitar o seguinte comando na pasta com os arquivos dos script:

    pip install -r requirements.txt
    
Se tudo ocorrer como esperado, o comando irá instalar as dependências automaticamente,

## Configurando o script

### Arquivo backup.config.json

O script possui uma pasta chamada /etc contendo o arquivo backup.config.json. Neste arquivo é possível fazer as configurações de servidor de email, usuário e senha SMTP, remetente, destinatário e parametros do backup



| Parametro | Descrição  | Exemplo
|--|--|--|
| remetente | O endereço de email do remetente  | Script de Backup <suporte@empresa.com>|
|smtp_host|O endereço do servidor SMTP |smtp.empresa.com|
smtp_porta|A porta do endereço do servidor SMTP |587|
smtp_user|O usuário do serviço SMTP |usuario@empresa.com|
smtp_senha|A senha do serviço SMTP |Senha\$up3r\$ecreta|
|destinatários| A lista de destinatários. É possível especificar um ou mais de um destino | `["email@empresa.com", ..., "email_n@empresa.com"]`|
|template| O arquivo de template do e-mail. Se não existir o arquivo ou não for especificado, o script enviará um email de texto puro | "default.html"|
|backup| Aqui são os parâmetros de origem e destino do backup. Sempre deve-se colocar '\\' no lugar de \.| `{"drive": "D:", "pasta": "\\Dados importantes", "destino": "\\Pasta de destino"}`|

## Executar o script

Uma vez devidamente configurado o arquivo de configuração, basta executar o script chamando o interpretador Python seguido do nome do script.

    python backup.py

Se for adicionar no Agendador de Tarefas do Windows, certifique que o script seja executado na pasta onde ele foi salvo. Por exemplo, se foi copiado em C:\Backup, certifique-se que a pasta onde o script for executado seja a mesma. 