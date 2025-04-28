from ninja import Schema


class LoginPayloadSchema(Schema):
    id: int


class RefreshPayloadSchema(Schema):
    refresh: str


class MyTokenObtainPairOutputSchema(Schema):
    refresh: str
    access: str


class MyTokenRefreshOutputSchema(Schema):
    access: str
