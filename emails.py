import smtplib
import time
import config

message_str = """\
From: %s <data-logger>
To: <%s>
Subject: %s
MIME-Version: 1.0
Content-Type: text/html
Date: %s


%s
</br>
"""

def send_mail(content):
    global message_str
    if config.email_sent == content:
        return
    
    config.email_sent = content 
    subject = "Solar logger reporting"
    
    if config.mail_server == "":
    	print("mailing not setup");
    	return
        
    message = message_str % (config.fromaddr, config.toaddrs, subject, time.strftime("%a, %-d %b %Y %H:%M:%S %z"), content)
    
    try:
        server = smtplib.SMTP_SSL(host=config.mail_server, port=config.mail_port)
        if config.debug:
            server.set_debuglevel(1)

        server.login(config.fromaddr, config.mail_pass)
        server.sendmail(config.fromaddr, config.toaddrs, message)
        server.quit
    except Exception as e:
        print("mailing error: %s" % str(e))
    
