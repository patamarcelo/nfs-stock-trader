#!/usr/local/bin/python3
import yagmail
try:
    from config import USER, PASSWORD
    user = USER
    password = PASSWORD
except Exception as e:
    user = 'your email'
    password = 'your password'



yag = yagmail.SMTP(user, password)

send_to = {
    "email to send": "sender/'s name",
}

subject = "Esse é o Assunto"
body = "esse é o corpo do e-mail"
html = """

<button> <h1> Clica aqui </h1></button>

"""
img = "teste.png"

anexos = '/Users/marcelopata/Desktop/3383_BOLETO_12_11926703_GDX_LOG_TRANSPORTES_LTDA.pdf'

def send_email_yag(html_formatado, assunto, attachments=None):
    yag = yagmail.SMTP(user, password)
    to = send_to
    
    body = html_formatado
    for email, nome in to.items():
        try:
            yag.send(email, assunto,attachments,[body])
            print(f"Email enviado com sucesso para: {nome}: {email} Subject: {assunto}")
        except:
            print("problema ao enviar e-mail")


# send_email_yag(html,subject)