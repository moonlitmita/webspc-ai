#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

import jwt
import os
import datetime
from fastapi import HTTPException
from app.core.config import settings

jwt_secret = os.getenv("JWT_SECRET", settings.jwt_secret)

class MyJwt:
    def __init__(self, secret=jwt_secret):
        self.secret = secret

    def encode(self, userinfo, lifetime=24):
        """
        编码用户信息为JWT token
        :param userinfo: 用户信息字典，必须包含'id'字段
        :param lifetime: token有效期（小时）
        :return: JWT token字符串
        """
        payload = {
            'exp': datetime.datetime.now() + datetime.timedelta(hours=lifetime),
            'data': userinfo
        }
        return jwt.encode(payload, self.secret, algorithm='HS256')

    def decode(self, jwt_str):
        """
        解码JWT token
        :param jwt_str: JWT token字符串
        :return: 解码后的payload
        """
        try:
            payload = jwt.decode(jwt_str, self.secret, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
