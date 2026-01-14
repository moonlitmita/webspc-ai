#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

from app.services.utils import MyJwt
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings

my_jwt = MyJwt(secret=settings.jwt_secret)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token", auto_error=False)
# print('token', {oauth2_scheme})

def verify_token(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="未提供令牌! No token provided!")
    
    # 清理token，移除可能存在的双引号和空格
    token = token.strip()
    if token.startswith('"') and token.endswith('"'):
        token = token[1:-1]
    
    try:
        decoded_token = my_jwt.decode(token)
        userid = decoded_token['data'].get('id') if isinstance(decoded_token['data'], dict) else decoded_token['data']
        if not userid:
            raise HTTPException(status_code=401, detail="无效令牌! Invalid token!")
        return userid
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))