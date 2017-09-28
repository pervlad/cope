__all__ = ('validate_email', 'validate_role', 'validate_password')

def validate_email(email:str)->bool:
    #TODO add this functionality when all other stuff is finished
    return bool(email)

def validate_role(role:str)->bool:
    #quick and dirty fix it
    return role in ('admin', 'manager', 'user')

def validate_password(pwd)->bool:
    return pwd and len(pwd) > 2
