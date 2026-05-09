from types import SimpleNamespace

from src.common.application.security import TokenError, decode_access_token


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
            claims = decode_access_token(
                token,
                SimpleNamespace(
                    JWT_SECRET=self._secret,
                    JWT_ALGORITHM=self._algorithm,
                    JWT_TTL=0,
                ),
            )
        except TokenError:
            return None
        subject = claims.get("sub")
        return str(subject) if subject is not None else None
