import threading
import requests
from django.core.mail import EmailMessage
import os



NIKITA_LOGIN = os.getenv("NIKITA_LOGIN")
NIKITA_PASSWORD = os.getenv("NIKITA_PASSWORD")
NIKITA_SENDER = os.getenv("NIKITA_SENDER")

class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data["email_subject"],
            body=data["email_body"],
            to=[data["to_email"]],
        )
        email.content_subtype = "html"
        EmailThread(email).start()



def send_sms(phone, message, code):
    new_phone = "".join(filter(str.isdigit, phone))
    xml_data = f"""<?xml version="1.0" encoding="UTF-8"?><message><login>{NIKITA_LOGIN}</login><pwd>{NIKITA_PASSWORD}</pwd><sender>{NIKITA_SENDER}</sender><text>{message} {code}</text><phones><phone>{new_phone}</phone></phones></message>"""

    headers = {"Content-Type": "application/xml"}

    url = "https://smspro.nikita.kg/api/message"

    response = requests.post(url, data=xml_data.encode("utf-8"), headers=headers)

    print(f"\n\n{response.text}\n\n")

    with open("test.txt", "a") as file:
        file.write(f"{response.text} - {new_phone}")

    if response.status_code == 200:
        return True
    return False
