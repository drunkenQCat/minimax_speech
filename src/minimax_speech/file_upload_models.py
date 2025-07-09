"""
MiniMax File Upload API 数据模型
"""

from pydantic import BaseModel, Field

from .common_models import BaseResponse


class FileInfo(BaseModel):
    """文件信息"""

    file_id: int = Field(description="文件的唯一标识符")
    bytes: int = Field(description="上传文件的大小")
    created_at: int = Field(description="文件创建时的Unix时间戳（秒）")
    filename: str = Field(description="文件名")
    purpose: str = Field(description="文件用途")


class FileUploadResponse(BaseModel):
    """文件上传响应"""

    file: FileInfo = Field(description="文件信息")
    base_resp: BaseResponse = Field(..., description="基本响应信息")
