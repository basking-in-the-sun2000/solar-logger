import smtplib
import ssl
import time
import config

message_str = """\
From: %s <data-logger>
To: <%s>
Subject: %s
MIME-Version: 1.0
Content-Type: text/plain
Date: %s


%s
\r\n
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
        if (config.mail_port == 587):
            server = smtplib.SMTP(host=config.mail_server, port=config.mail_port, timeout=15)
            if config.debug:
                server.set_debuglevel(1)
            sc = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
            sc.options |= ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1
            sc.minimum_version = ssl.TLSVersion.TLSv1_2
            server.starttls(context=sc)
        else:
            server = smtplib.SMTP_SSL(host=config.mail_server, port=config.mail_port, timeout=15)
            if config.debug:
                server.set_debuglevel(1)

        server.ehlo()
        server.login(config.fromaddr, config.mail_pass)
        server.sendmail(config.fromaddr, config.toaddrs, message)
        server.quit
    except Exception as e:
        print("mailing error: %s" % str(e))
