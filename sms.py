import os
from twilio.rest import Client
from config import numbers

account_sid = os.environ['TWILIO_ACCOUNT_SID']  # stored in activate/postactivate scripts
token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, token)

def send_sms(cell, message):
    client.api.account.messages.create(
        to=cell,
        from_=numbers['twilio_phone'],
        body=message)
