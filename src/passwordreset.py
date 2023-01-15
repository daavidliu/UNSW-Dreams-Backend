
import smtplib, ssl
import random
from src.error import InputError, AccessError
from email.message import EmailMessage
from src.data import data, save_data

EMAIL_ADDRESS = 'FRI11ABLINKER@gmail.com'
EMAIL_PASSWORD = 'fri11a_blinker'

def request_reset(email):

    #generate a unique code
    code = generate_code()

    #end code to user
    send_email(email, code)

    #add code to data
    for user in data['users']:
        if email == user['email']:
            user['code'] = code
            save_data()
    

def reset_password(code, new_password):
    if len(new_password) < 6:
        raise InputError (description="password too short")
    print(f"\n\n\n\n\n\n\n{code}\n\n\n\n\n\n\n")
    valid_code = False
    #find user in database
    for user in data['users']:
        try:
            if str(code) == user['code']:
                user['password'] = new_password
                user['code'] = ''
                valid_code = True
        except:
            pass

    save_data()
    
    if not valid_code:
        raise InputError (description="Not a Valid Code")
    


def send_email(user_email, code):

    msg = EmailMessage()
    msg['Subject'] = 'Password Reset Code'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = user_email
    msg.set_content(f'This is your code: {code}')

    smtp_server = "smtp.gmail.com"
    port = 587 

    server = smtplib.SMTP(smtp_server,port)
    server.ehlo()
    server.starttls() 
    server.ehlo() 
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()

def generate_code():
    return str(random.randint(100000,999999))
    

