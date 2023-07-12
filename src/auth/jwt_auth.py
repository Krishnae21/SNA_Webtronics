from datetime import datetime, timedelta
from config import JWT_SECRET
from jose import jwt


class JwtAuth:
    @staticmethod
    def create_token(username: str, type_token: str = "auth", expire: timedelta = timedelta(minutes=60)) -> str:
        data: dict
        to_encode: dict = {"username": username, "type": type_token}
        exp = datetime.utcnow() + expire
        to_encode.update({"exp": exp})
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")
        return encoded_jwt

    @staticmethod
    def validate_access_token(jvt_token: str, type_token: str = "auth") -> dict:
        validate: dict = {"status": None, "user": None}
        try:
            payload = jwt.decode(jvt_token, key=JWT_SECRET, algorithms=["HS256"])
            if datetime.utcnow() <= datetime.fromtimestamp(payload["exp"]) and payload["type"] == type_token:
                validate["user"] = payload["username"]
                validate["status"] = True
        except (jwt.JWTError, KeyError):
            validate["status"] = False
        return validate

    @staticmethod
    def refresh_token(jvt_token: str) -> dict:
        validate: dict = {"status": None, "token": None}
        try:
            payload = jwt.decode(jvt_token, key=JWT_SECRET, algorithms=["HS256"])
            if datetime.utcnow() <= datetime.fromtimestamp(payload["exp"]) and payload["type"] == "refresh":
                validate["status"] = True
                validate["token"] = JwtAuth.create_token(payload["username"])
        except (jwt.JWTError, KeyError):
            validate["status"] = False

        return validate
