__all__ = ('build_invitation_mail_body', 'build_activation_mail_body')
import re
from usermodel import User

def email_body_to_line(msg:str)->str:       
    import re #imported here only to keep track of it when moving this to a separate module
    return re.sub('\s+',' ', msg)

def build_invitation_mail_body(url:str, invitation_token:bytes, user:User):
    # To do create body and format
    link = url + '?invitation_tokeapin=' + invitation_token.decode('utf-8')
    return build_invitation_mail_body.template.format(link=link, user=user)


build_invitation_mail_body.template = email_body_to_line(
        '''<header> </header> <body>
            <div><p>Hi {user.first_name} <br>You have been invited</p>
            <p>Please activate your account by visiting<</p></div>
            <div><a href="{link}"></div></body>
        ''')

def build_activation_mail_body(url:str, activation_token:bytes, user:User):
    # To do create body and format
    link = url + '?activation_token=' + activation_token.decode('utf-8')
    return build_activation_mail_body.template.format(link=link, user=user)

build_activation_mail_body.template = email_body_to_line(
        '''<header> </header> <body>
            <div>
                <p>Hi {user.first_name} <br>Please activate your account by visiting</p>
            </div>
            <div><a href="{link}"></div></body>
        ''')
