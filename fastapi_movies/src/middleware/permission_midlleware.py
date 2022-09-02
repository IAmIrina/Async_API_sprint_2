from core.constants import anonymous
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from utils.user_permission import UserPermission


class PermissionMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next) -> Response:
        access_token = request.headers.get('x-access_token')
        new_headers = {}
        new_headers.update(request.headers)
        if access_token:
            permission = await UserPermission().check_user_permission(access_token)
        else:
            permission = anonymous
        new_headers['x-permission'] = permission
        request._headers = new_headers
        response = await call_next(request)
        return response
