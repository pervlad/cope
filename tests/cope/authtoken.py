# BL token
import jwt
import datetime


__all__ = ["encode_session_token", "decode_session_token", 
            "encode_email_token", "decode_email_token"]


def encode_session_token(user_id:int)->bytes:
    expdelta = encode_session_token.expdelta
    payload = { #'iss':'cope', 'aud':'cope',
                'sub': 'authorization',
                'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expdelta),
                'user_id': user_id
              }
    return jwt.encode(payload, encode_session_token.secret)

encode_session_token.secret = 'secret'
encode_session_token.expdelta = 'expdelta'

def decode_session_token(token:bytes):
    return jwt.decode(token, decode_session_token.secret, False, ['HS256'], sub='authorization')
    # return jwt.decode(token, decode_session_token.secret, False)

decode_session_token.secret = 'secret'
decode_session_token.expdelta = 'expdelta'

def encode_email_token(user_id:int, sub:str)->bytes:
    assert sub in ('activation', 'invitation') 
    expdelta = encode_email_token.expdelta
    payload = { #'iss':'cope', 'aud':'cope', 
                'sub': sub,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expdelta),
                'user_id': user_id
              }
    return jwt.encode(payload, encode_email_token.secret)

encode_email_token.secret = 'email_secret'
encode_email_token.expdelta = 'email_delta'

def decode_email_token(token:bytes, sub:str):
    assert sub in ('activation', 'invitation') 
    return jwt.decode(token, decode_email_token.secret, False, ['HS256'], sub=sub)
    # return jwt.decode(token, decode_session_token.secret, False)

decode_email_token.secret = 'email_secret'
decode_email_token.expdelta = 'email_delta'