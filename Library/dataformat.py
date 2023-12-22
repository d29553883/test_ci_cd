import datetime
import random, string
import os
import gc



def check_token(request):
    try: 
        token_type, access_token = request.headers.get('Authorization').split(' ')
        if token_type != 'Bearer' or token_type is None:
            return False
        else:
            return access_token
    except:
        return False