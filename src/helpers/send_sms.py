import custom_env
import requests

def send_sms(phone, message):
    # new_phone = "".join(filter(str.isdigit, phone))
    xml_data = f"""<?xml version="1.0" encoding="UTF-8"?><message><login>{custom_env.NIKITA_LOGIN}</login><pwd>{custom_env.NIKITA_PASSWORD}</pwd><sender>{custom_env.NIKITA_SENDER}</sender><text>{message}</text><phones><phone>{phone}</phone></phones></message>"""
    headers = {"Content-Type": "application/xml"}
    url = "https://smspro.nikita.kg/api/message"
    response = requests.post(url, data=xml_data.encode("utf-8"), headers=headers)
    if response.status_code == 200:
        # with open("nikita.txt", 'a') as file:
        #     file.write(f"{phone} {message} - {response.text} \n")
        return True
    return False

    