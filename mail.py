#!/usr/bin/env python

import logging
import os
import smtplib
import email.encoders
import email.mime.base
import email.mime.text
import email.mime.multipart


class Message(object):


    def __init__(self, from_addr, to_addr, subject='', body='No message.', smtp_host='localhost', smtp_port=25):
        self.from_addr = from_addr
        self.to_addr = to_addr
        self.subject = subject
        self.body = body
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.attachments = []

    def attach(self, filename):
        self.attachments.append(filename)

    def build_mail(self):
        # Code inspired by https://github.com/aspineux/pyzmail
        text = email.mime.text.MIMEText(self.body, 'plain', 'utf8')

        multipart = email.mime.multipart.MIMEMultipart('mixed')
        multipart['Subject'] = self.subject
        multipart['From'] = self.from_addr
        multipart['To'] = ', '.join(self.to_addr)

        multipart.attach(text)

        for filename in self.attachments:
            part = email.mime.multipart.MIMEBase('application', 'octet-stream')
            with open(filename, 'rb') as attachment:
                part.set_payload(attachment.read())
                email.encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(filename))
                multipart.attach(part)

        return multipart.as_string()


    def send(self):
        smtp = smtplib.SMTP(self.smtp_host, self.smtp_port)
        smtp.sendmail(self.from_addr, self.to_addr, self.build_mail())
        smtp.quit()

if __name__ == '__main__':
    import argparse
    desc = 'Sends a mail.'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-v', '--verbose', action='store_true', \
        help='Increase output verbosity')
    parser.add_argument('-m', '--message', default='Some message', \
        help='The message to send by mail.')
    parser.add_argument('-s', '--subject', default='Some subject', \
        help='The subject of the message being sent.')
    parser.add_argument('-a', '--attachments', \
        help='Comma-separated list of filenames to attach to the mail.')
    parser.add_argument('-f', '--from-address', required=True, \
        help='The address where the mail is being sent from.')
    parser.add_argument('-t', '--to-address', \
        help='Comma-separated list of the recipients of the mail message.')
    parser.add_argument('-o', '--host', default='0.0.0.0', \
        help='The smtp host that will forward the mail message.')
    parser.add_argument('-p', '--port', default=25, \
        help='The port where the smtp service is listening to.')

    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s::%(levelname)s::%(message)s')
    logging.getLogger().setLevel(getattr(logging, 'INFO'))

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug('Verbose mode activated.')

    m = Message(args.from_address, args.to_address.split(','), args.subject, args.message, args.host, args.port)

    for filename in args.attachments.split(','):
        m.attach(filename)

    m.send()
