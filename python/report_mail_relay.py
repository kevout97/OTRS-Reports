import smtplib
import time
from datetime import datetime, date, time, timedelta
import os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

fromaddr = 'Reportes OTRS'
toaddrs  = ['kev.gomez97@gmail.com']
#toaddrs = 'berryrreb@gmail.com'

msg = MIMEMultipart()
msg['Subject'] = "Reporte semanal OTRS"
msg['From'] = "Reportes OTRS"
msg['To'] = ", ".join(toaddrs)

part_pdf = MIMEBase('application', "octet-stream")
part_pdf.set_payload(open(os.getcwd()+"/Reporte_OTRS_"+str(datetime.now().isocalendar()[1])+".pdf", "rb").read())
encoders.encode_base64(part_pdf)

part_pdf.add_header('Content-Disposition', 'attachment; filename="'+os.getcwd()+'/Reporte_OTRS_'+str(datetime.now().isocalendar()[1])+'.pdf"')

msg.attach(part_pdf)

username = 'reportes.ctin.infraestructura@gmail.com'
password = 'UmVwb3J0ZXMuQ1RJTi5JbmZyYWVzdHJ1Y3R1cmEK'
server = smtplib.SMTP('smtp.gmail.com:587')
server.ehlo()
server.starttls()
server.login(username,password)
server.sendmail(fromaddr, toaddrs, msg.as_string())
server.quit()