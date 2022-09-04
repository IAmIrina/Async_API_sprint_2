from http import HTTPStatus

from core.constants import anonymous
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from utils.user_permission import UserPermission


class PermissionMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next) -> Response:
        access_token = request.headers.get('Authorization')
        if access_token:
            permission, status = await UserPermission().check_user_permission(access_token)
            if status == HTTPStatus.UNAUTHORIZED:
                return JSONResponse(status_code=status, content=permission)
        else:
            permission = anonymous
        request.state.permission = permission
        response = await call_next(request)
        return response
