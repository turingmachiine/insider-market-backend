from jose import JWTError, jwt


class JwtIdentityExtractor:
    def __init__(self, secret: str, algorithm: str) -> None:
        self._secret = secret
        self._algorithm = algorithm

    @staticmethod
    def _extract_token(authorization: str | None) -> str | None:
        if not authorization or not authorization.lower().startswith("bearer "):
            return None
        return authorization.split(" ", 1)[1]

    def extract_user_id(self, authorization: str | None) -> str | None:
        token = self._extract_token(authorization)
        if token is None:
            return None
        try:
            claims = jwt.decode(
                token,
                self._secret,
                algorithms=[self._algorithm],
                options={"verify_aud": False},
            )
        except JWTError:
            return None
        subject = claims.get("sub")
        return str(subject) if subject is not None else None
