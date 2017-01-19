import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders

class emailSender():
    def __init__(self, server, port, user, passw, ):
        self.user      = user
        self.passw     = passw
        self.server    = server
        self.port      = port
        self.serverObj = smtplib.SMTP(server, port)

    def connect(self):
        self.serverObj.starttls()
        self.serverObj.login(self.user, self.passw)

    def send(self, toAddr, subject, body):
        msg = MIMEMultipart()
        msg['From'] = self.user
        msg['To'] = toAddr
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))
        text = msg.as_string()

        self.serverObj.sendmail(self.user, toAddr, text)
    def disconnect(self):
        self.serverObj.quit()
def main():
    sender = emailSender("smtp.gmail.com",587,"lerko.araya@ug.uchile.cl","pqDVZMbN7")
    sender.connect()
    sender.send("aheit.s.a@gmail.com","Test Mail from python","This is a example mail")
    sender.disconnect()

if __name__ == '__main__':
    main()