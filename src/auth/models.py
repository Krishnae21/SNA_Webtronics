from pydantic import BaseModel, EmailStr, Field
import json

# from datetime import datetime


class AuthSchema(BaseModel):
    username: str = Field(min_length=6, max_length=16)
    password: str = Field(min_length=8)


class SignUpSchema(AuthSchema):
    email: EmailStr


class Token(BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None

class Return(BaseModel):
    status: str = None
    details: str = None


class AuthReturn(Return):
    data: Token = None

    def incorrect(self):
        self.status = "Error"
        self.details = "Username or password incorrect."
        return self.dict()

    def correct(self, token: Token = Token()):
        self.status = "Success"
        self.data: Token = token
        return self.dict()

    def registered(self):
        self.status = "Error"
        self.details = "Username or email already registered."
        return self.dict()

    def token_error(self):
        self.status = "Error"
        self.details = "Token is invalid"
        return self.dict()
