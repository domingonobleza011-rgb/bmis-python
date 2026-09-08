from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .database import get_db
from .security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Decodes the JWT. Payload shape: {sub, role, name, exp}
    role is one of: resident, staff, administrator, sk
    (mirrors $_SESSION['userdata']['role'] in the original app)."""
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
    payload["sub"] = int(payload["sub"])  # stored as a string in the JWT per spec; routers compare it to int PKs
    return payload


def require_roles(*roles: str):
    """Usage: Depends(require_roles('staff', 'administrator'))
    Mirrors validate_staff_or_admin() / require_login_or_deny() in main.class.php."""
    def _checker(user: dict = Depends(get_current_user)) -> dict:
        if user.get("role") not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Access denied.")
        return user
    return _checker


require_resident = require_roles("resident")
require_staff_or_admin = require_roles("staff", "administrator")
require_admin = require_roles("administrator")
require_sk = require_roles("sk", "staff", "administrator")
