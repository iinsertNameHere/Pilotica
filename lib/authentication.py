from sanic import Request, json
from sanic.exceptions import Unauthorized, Forbidden
from sanic.log import logger
from functools import wraps
import jwt
from .error import error_redirect
from datetime import datetime, timedelta
from .models import User, SessionLocal
from .premissions import Premissions

# JWT Configuration
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def authenticated(
    request: Request, 
    permissions: list[Premissions] = None, 
    allow_api_key: bool = False, 
    return_json: bool = False,
    redirect_route: str = "/auth/login"
):
    """Authenticate user based on JWT or API key.

    Args:
        request (Request): Sanic request object.
        permissions (list[Premissions], optional): Required permissions. Defaults to None.
        allow_api_key (bool, optional): Allow authentication using an API key. Defaults to False.
        return_json (bool, optional): Return errors as JSON if True, else raise exceptions. Defaults to False.
    
    Returns:
        User: Authenticated User object or None.

    Raises:
        Unauthorized: If authentication fails.
        Forbidden: If user lacks permissions.
    """
    try:
        if allow_api_key:
            api_key = request.headers.get("Authorization")
            if api_key:
                with SessionLocal() as session:
                    user = session.query(User).filter(User.api_key == api_key).first()
                    if not user:
                        logger.warning(f"Authentication failed: Invalid API key (IP: {request.ip})")
                        if return_json:
                            return json({"error": "Invalid API key!"}, status=401)
                        raise Unauthorized("Invalid API key!")
                    if permissions and not (
                        user.has_permissions(permissions) or user.has_permissions([Premissions.Admin])
                    ):
                        logger.warning(
                            f"Permission denied for user {user.id} (IP: {request.ip}). Required: {permissions}"
                        )
                        if return_json:
                            return json({"error": "Insufficient permissions!"}, status=403)
                        raise Forbidden("Insufficient permissions!")
                    request.ctx.user = {"sub": user.uuid}
                    return None

        token = request.cookies.get("access_token")
        if not token:
            logger.warning(f"Authentication failed: Missing token or API key (IP: {request.ip})")
            if return_json:
                return json({"error": "Authentication token or API key is missing!"}, status=401)
            return error_redirect(request, "Authentication token or API key is missing!", redirect_route)

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_uuid = payload.get("sub")
        if not user_uuid:
            logger.warning(f"Authentication failed: Invalid token payload (IP: {request.ip})")
            if return_json:
                return json({"error": "Invalid token payload!"}, status=401)
            return error_redirect(request, "Invalid token payload!", redirect_route)

        with SessionLocal() as db:
            user = db.query(User).filter(User.uuid == user_uuid).first()
            if not user:
                logger.warning(f"Authentication failed: User not found for token {user_uuid} (IP: {request.ip})")
                if return_json:
                    return json({"error": "User not found!"}, status=401)
                return error_redirect(request, "User not found!", redirect_route)

            if permissions and not (
                user.has_permissions(permissions) or user.has_permissions([Premissions.Admin])
            ):
                logger.warning(
                    f"Permission denied for user {user.id} (IP: {request.ip}). Required: {permissions}"
                )
                if return_json:
                    return json({"error": "Insufficient permissions!"}, status=403)
                return error_redirect(request, "Insufficient permissions!", redirect_route)
            
            request.ctx.user = {"sub": user.uuid}
            return None

    except jwt.ExpiredSignatureError:
        logger.warning(f"Authentication failed: Token expired (IP: {request.ip})")
        if return_json:
            return json({"error": "Token has expired!"}, status=401)
        return error_redirect(request, "Token has expired!", redirect_route)
    except jwt.InvalidTokenError as e:
        logger.warning(f"Authentication failed: Invalid token (IP: {request.ip})")
        if return_json:
            return json({"error": "Invalid token!"}, status=401)
        return error_redirect(request, "Invalid token!", redirect_route)

    return None

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_authenticated_user(request: Request):
    if hasattr(request.ctx, 'user') and request.ctx.user:
        user_uuid = request.ctx.user.get("sub")
        if not user_uuid:
            return None
        with SessionLocal() as db:
            return db.query(User).filter(User.uuid == user_uuid).first()
    return None
