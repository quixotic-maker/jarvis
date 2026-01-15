"""
API工具函数
统一的响应构造、异常处理等
"""
from typing import TypeVar, Optional, Any, List
from datetime import datetime
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from app.api.schemas import (
    BaseResponse,
    ResponseStatus,
    ErrorResponse,
    PaginatedResponse,
    PaginationMeta
)

T = TypeVar('T')


# ==================== 响应构造函数 ====================

def success_response(
    data: Optional[T] = None,
    message: str = "操作成功",
    status_code: int = status.HTTP_200_OK
) -> BaseResponse[T]:
    """
    构造成功响应
    
    Args:
        data: 响应数据
        message: 响应消息
        status_code: HTTP状态码
        
    Returns:
        BaseResponse: 统一格式的成功响应
    """
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        message=message,
        data=data,
        timestamp=datetime.now()
    )


def error_response(
    message: str = "操作失败",
    error_code: Optional[str] = None,
    details: Optional[Any] = None,
    status_code: int = status.HTTP_400_BAD_REQUEST
) -> ErrorResponse:
    """
    构造错误响应
    
    Args:
        message: 错误消息
        error_code: 错误代码
        details: 错误详情
        status_code: HTTP状态码
        
    Returns:
        ErrorResponse: 统一格式的错误响应
    """
    return ErrorResponse(
        status=ResponseStatus.ERROR,
        message=message,
        error_code=error_code,
        details=details,
        timestamp=datetime.now()
    )


def paginated_response(
    data: List[T],
    page: int = 1,
    page_size: int = 20,
    total: int = 0,
    message: str = "查询成功"
) -> PaginatedResponse[T]:
    """
    构造分页响应
    
    Args:
        data: 数据列表
        page: 当前页码
        page_size: 每页数量
        total: 总记录数
        message: 响应消息
        
    Returns:
        PaginatedResponse: 统一格式的分页响应
    """
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    
    return PaginatedResponse(
        status=ResponseStatus.SUCCESS,
        message=message,
        data=data,
        meta=PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages
        ),
        timestamp=datetime.now()
    )


# ==================== 异常类 ====================

class APIException(HTTPException):
    """API自定义异常基类"""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: Optional[str] = None,
        details: Optional[Any] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details
        super().__init__(status_code=status_code, detail=message)


class ResourceNotFoundError(APIException):
    """资源不存在异常"""
    def __init__(self, resource: str = "资源", resource_id: Any = None):
        message = f"{resource}不存在"
        if resource_id:
            message = f"{resource} (ID: {resource_id}) 不存在"
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND"
        )


class ValidationError(APIException):
    """数据验证异常"""
    def __init__(self, message: str = "数据验证失败", details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details
        )


class AuthenticationError(APIException):
    """认证异常"""
    def __init__(self, message: str = "认证失败"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_ERROR"
        )


class PermissionDeniedError(APIException):
    """权限不足异常"""
    def __init__(self, message: str = "权限不足"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="PERMISSION_DENIED"
        )


class BusinessLogicError(APIException):
    """业务逻辑异常"""
    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=error_code or "BUSINESS_LOGIC_ERROR"
        )


# ==================== 异常处理器 ====================

async def api_exception_handler(request, exc: APIException):
    """API异常统一处理器"""
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            message=exc.message,
            error_code=exc.error_code,
            details=exc.details
        ).model_dump()
    )


async def generic_exception_handler(request, exc: Exception):
    """通用异常处理器"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(
            message="服务器内部错误",
            error_code="INTERNAL_SERVER_ERROR",
            details=str(exc) if __debug__ else None
        ).model_dump()
    )


# ==================== 工具函数 ====================

def validate_pagination(page: int, page_size: int) -> tuple[int, int]:
    """
    验证分页参数
    
    Args:
        page: 页码
        page_size: 每页数量
        
    Returns:
        tuple: (验证后的page, page_size)
    """
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 20
    if page_size > 100:
        page_size = 100
    return page, page_size


def calculate_pagination(page: int, page_size: int) -> tuple[int, int]:
    """
    计算分页的skip和limit
    
    Args:
        page: 页码（从1开始）
        page_size: 每页数量
        
    Returns:
        tuple: (skip, limit)
    """
    page, page_size = validate_pagination(page, page_size)
    skip = (page - 1) * page_size
    limit = page_size
    return skip, limit


def format_datetime(dt: Optional[datetime]) -> Optional[str]:
    """
    格式化日期时间
    
    Args:
        dt: datetime对象
        
    Returns:
        str: 格式化后的字符串
    """
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def parse_tags(tags: Optional[str]) -> List[str]:
    """
    解析标签字符串
    
    Args:
        tags: 标签字符串，逗号分隔
        
    Returns:
        List[str]: 标签列表
    """
    if not tags:
        return []
    return [tag.strip() for tag in tags.split(",") if tag.strip()]


def serialize_json_field(data: Any) -> Any:
    """
    序列化JSON字段
    
    Args:
        data: 需要序列化的数据
        
    Returns:
        Any: 序列化后的数据
    """
    if isinstance(data, (dict, list)):
        return data
    if isinstance(data, str):
        import json
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return data
    return data
