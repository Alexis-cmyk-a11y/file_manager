# 📡 API 参考手册

<div align="center">
  <h3>文件管理系统 REST API 完整文档</h3>
  <p>版本: v2.0.0 | 格式: JSON | 协议: HTTP/HTTPS</p>
</div>

## 🌐 基础信息

### 服务端点
```
生产环境: https://your-domain.com/api
开发环境: http://localhost:8888/api
```

### 通用响应格式
```json
{
  "success": boolean,
  "message": "string",
  "data": object | array | null,
  "timestamp": "ISO 8601 时间戳",
  "request_id": "唯一请求ID"
}
```

### 错误响应格式
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": "详细错误信息"
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 通用HTTP状态码

| 状态码 | 含义 | 说明 |
|--------|------|------|
| `200` | OK | 请求成功 |
| `201` | Created | 资源创建成功 |
| `400` | Bad Request | 请求参数错误 |
| `401` | Unauthorized | 未授权访问 |
| `403` | Forbidden | 权限不足 |
| `404` | Not Found | 资源不存在 |
| `413` | Payload Too Large | 文件过大 |
| `429` | Too Many Requests | 请求频率过高 |
| `500` | Internal Server Error | 服务器内部错误 |

## 📁 文件管理 API

### 获取文件列表

**端点**: `GET /api/list`

**描述**: 获取指定目录下的文件和文件夹列表

**参数**:
| 参数名 | 类型 | 必需 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `path` | string | 否 | "/" | 目录路径 |
| `page` | integer | 否 | 1 | 页码 |
| `limit` | integer | 否 | 20 | 每页数量 |
| `sort` | string | 否 | "name" | 排序字段 (name/size/time) |
| `order` | string | 否 | "asc" | 排序方向 (asc/desc) |

**请求示例**:
```bash
curl "http://localhost:8888/api/list?path=/documents&page=1&limit=10"
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "files": [
      {
        "name": "document.pdf",
        "path": "/documents/document.pdf",
        "type": "file",
        "size": 1024000,
        "size_formatted": "1.0 MB",
        "modified": "2024-01-01T10:00:00Z",
        "permissions": "rw-r--r--",
        "is_editable": false,
        "mime_type": "application/pdf"
      },
      {
        "name": "scripts",
        "path": "/documents/scripts",
        "type": "directory",
        "size": 0,
        "modified": "2024-01-01T09:00:00Z",
        "permissions": "rwxr-xr-x",
        "file_count": 5
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 3,
      "total_items": 25,
      "items_per_page": 10,
      "has_next": true,
      "has_prev": false
    },
    "path_info": {
      "current_path": "/documents",
      "parent_path": "/",
      "breadcrumbs": [
        {"name": "根目录", "path": "/"},
        {"name": "documents", "path": "/documents"}
      ]
    }
  }
}
```

### 上传文件

**端点**: `POST /api/upload`

**描述**: 上传一个或多个文件到指定目录

**Content-Type**: `multipart/form-data`

**参数**:
| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| `files` | file[] | 是 | 要上传的文件(支持多个) |
| `path` | string | 否 | 目标目录，默认为根目录 |
| `overwrite` | boolean | 否 | 是否覆盖同名文件 |

**请求示例**:
```bash
curl -X POST \
  -F "files=@document.pdf" \
  -F "files=@image.jpg" \
  -F "path=/uploads" \
  -F "overwrite=false" \
  "http://localhost:8888/api/upload"
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "uploaded_files": [
      {
        "original_name": "document.pdf",
        "saved_name": "document.pdf",
        "path": "/uploads/document.pdf",
        "size": 1024000,
        "mime_type": "application/pdf"
      }
    ],
    "failed_files": [
      {
        "name": "large_file.zip",
        "error": "文件大小超过限制"
      }
    ],
    "summary": {
      "total": 2,
      "success": 1,
      "failed": 1
    }
  }
}
```

### 下载文件

**端点**: `GET /api/download`

**描述**: 下载指定文件

**参数**:
| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| `path` | string | 是 | 文件路径 |
| `inline` | boolean | 否 | 是否在浏览器中直接显示 |

**请求示例**:
```bash
curl "http://localhost:8888/api/download?path=/documents/file.pdf" -o file.pdf
```

**响应**: 文件二进制流

### 删除文件/目录

**端点**: `POST /api/delete`

**描述**: 删除指定的文件或目录

**Content-Type**: `application/json`

**参数**:
```json
{
  "path": "string",           // 必需：文件或目录路径
  "recursive": boolean,       // 可选：是否递归删除目录
  "force": boolean           // 可选：是否强制删除
}
```

**请求示例**:
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"path": "/temp/old_files", "recursive": true}' \
  "http://localhost:8888/api/delete"
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "deleted_path": "/temp/old_files",
    "type": "directory",
    "files_deleted": 15,
    "size_freed": 10485760
  }
}
```

### 创建文件夹

**端点**: `POST /api/create_folder`

**描述**: 在指定位置创建新文件夹

**Content-Type**: `application/json`

**参数**:
```json
{
  "path": "string",           // 必需：父目录路径
  "name": "string",           // 必需：文件夹名称
  "recursive": boolean        // 可选：是否创建中间目录
}
```

**请求示例**:
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"path": "/projects", "name": "new_project", "recursive": true}' \
  "http://localhost:8888/api/create_folder"
```

### 重命名文件/目录

**端点**: `POST /api/rename`

**描述**: 重命名文件或目录

**Content-Type**: `application/json`

**参数**:
```json
{
  "path": "string",           // 必需：原文件路径
  "new_name": "string"        // 必需：新名称
}
```

**请求示例**:
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"path": "/documents/old_name.txt", "new_name": "new_name.txt"}' \
  "http://localhost:8888/api/rename"
```

### 复制/移动文件

**端点**: `POST /api/copy` 或 `POST /api/move`

**描述**: 复制或移动文件到新位置

**Content-Type**: `application/json`

**参数**:
```json
{
  "source": "string",         // 必需：源路径
  "target": "string",         // 必需：目标路径
  "overwrite": boolean        // 可选：是否覆盖目标文件
}
```

**请求示例**:
```bash
# 复制文件
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"source": "/docs/file.txt", "target": "/backup/file.txt"}' \
  "http://localhost:8888/api/copy"

# 移动文件
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"source": "/temp/file.txt", "target": "/archive/file.txt"}' \
  "http://localhost:8888/api/move"
```

## ✏️ 编辑器 API

### 打开文件编辑

**端点**: `POST /api/editor/open`

**描述**: 打开文件进行编辑，返回文件内容和元信息

**Content-Type**: `application/json`

**参数**:
```json
{
  "path": "string",           // 必需：文件路径
  "encoding": "string"        // 可选：指定编码（utf-8, gbk等）
}
```

**请求示例**:
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"path": "/code/main.py"}' \
  "http://localhost:8888/api/editor/open"
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "content": "#!/usr/bin/env python3\nprint('Hello, World!')",
    "encoding": "utf-8",
    "language": "python",
    "size": 45,
    "lines": 2,
    "file_info": {
      "name": "main.py",
      "path": "/code/main.py",
      "modified": "2024-01-01T10:00:00Z",
      "size_formatted": "45 B"
    },
    "editor_config": {
      "theme": "default",
      "syntax_highlighting": true,
      "line_numbers": true,
      "word_wrap": false
    }
  }
}
```

### 保存文件

**端点**: `POST /api/editor/save`

**描述**: 保存编辑后的文件内容

**Content-Type**: `application/json`

**参数**:
```json
{
  "path": "string",           // 必需：文件路径
  "content": "string",        // 必需：文件内容
  "encoding": "string",       // 可选：保存编码
  "create_backup": boolean    // 可选：是否创建备份
}
```

**请求示例**:
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"path": "/code/main.py", "content": "print(\"Hello, World!\")"}' \
  "http://localhost:8888/api/editor/save"
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "saved": true,
    "backup_created": "/code/.backup/main.py.2024-01-01-10-00-00",
    "file_info": {
      "size": 22,
      "modified": "2024-01-01T10:05:00Z",
      "checksum": "sha256:abc123..."
    }
  }
}
```

### 文件预览

**端点**: `GET /api/editor/preview`

**描述**: 获取文件内容预览（仅返回前几行）

**参数**:
| 参数名 | 类型 | 必需 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `path` | string | 是 | - | 文件路径 |
| `max_lines` | integer | 否 | 100 | 最大行数 |
| `encoding` | string | 否 | "auto" | 文件编码 |

**请求示例**:
```bash
curl "http://localhost:8888/api/editor/preview?path=/logs/app.log&max_lines=50"
```

### 文件搜索

**端点**: `POST /api/editor/search`

**描述**: 在文件中搜索指定文本

**Content-Type**: `application/json`

**参数**:
```json
{
  "path": "string",           // 必需：文件路径
  "search_term": "string",    // 必需：搜索关键词
  "case_sensitive": boolean,  // 可选：是否区分大小写
  "regex": boolean,          // 可选：是否使用正则表达式
  "max_results": integer     // 可选：最大结果数
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "matches": [
      {
        "line_number": 5,
        "line_content": "def main():",
        "match_start": 4,
        "match_end": 8,
        "context_before": "import os",
        "context_after": "    print('Hello')"
      }
    ],
    "total_matches": 3,
    "search_info": {
      "term": "main",
      "case_sensitive": false,
      "regex": false
    }
  }
}
```

### 检查文件可编辑性

**端点**: `GET /api/editor/check-editability`

**描述**: 检查文件是否可以在线编辑

**参数**:
| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| `path` | string | 是 | 文件路径 |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "editable": true,
    "language": "python",
    "reason": "支持的文件类型",
    "file_size": 1024,
    "max_edit_size": 10485760,
    "encoding": "utf-8",
    "binary": false
  }
}
```

## 📊 系统信息 API

### 获取系统状态

**端点**: `GET /api/info`

**描述**: 获取系统运行状态和基本信息

**请求示例**:
```bash
curl "http://localhost:8888/api/info"
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "system": {
      "os": "Linux",
      "python_version": "3.9.7",
      "flask_version": "3.0.0",
      "uptime": "2 days, 3 hours",
      "timezone": "UTC"
    },
    "storage": {
      "total_space": 107374182400,
      "used_space": 53687091200,
      "free_space": 53687091200,
      "usage_percent": 50.0
    },
    "memory": {
      "total": 8589934592,
      "available": 4294967296,
      "percent": 50.0
    },
    "performance": {
      "cpu_percent": 15.5,
      "load_average": [0.5, 0.7, 0.8],
      "requests_per_minute": 45
    },
    "features": {
      "upload_enabled": true,
      "download_enabled": true,
      "edit_enabled": true,
      "delete_enabled": true
    }
  }
}
```

### 获取磁盘使用情况

**端点**: `GET /api/disk-usage`

**描述**: 获取详细的磁盘使用情况

**参数**:
| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| `path` | string | 否 | 指定路径，默认为根目录 |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "path": "/",
    "total": 107374182400,
    "used": 53687091200,
    "free": 53687091200,
    "percent": 50.0,
    "breakdown": [
      {
        "name": "documents",
        "size": 10737418240,
        "percent": 10.0
      },
      {
        "name": "images",
        "size": 21474836480,
        "percent": 20.0
      }
    ]
  }
}
```

## 🔐 权限和认证

### 权限级别

| 级别 | 权限 | 说明 |
|------|------|------|
| `read` | 只读 | 只能浏览和下载文件 |
| `write` | 读写 | 可以上传、编辑、重命名文件 |
| `admin` | 管理员 | 完全控制，包括删除和系统设置 |

### 认证头部

```http
Authorization: Bearer <your-token>
X-API-Key: <your-api-key>
```

### 权限检查

**端点**: `GET /api/permissions`

**响应示例**:
```json
{
  "success": true,
  "data": {
    "user": "admin",
    "level": "admin",
    "permissions": {
      "read": true,
      "write": true,
      "delete": true,
      "admin": true
    },
    "rate_limit": {
      "requests_per_minute": 200,
      "remaining": 195,
      "reset_time": "2024-01-01T10:01:00Z"
    }
  }
}
```

## ⚡ 性能和限制

### 速率限制

| 端点类型 | 限制 | 时间窗口 |
|----------|------|----------|
| 文件列表 | 100 请求 | 每分钟 |
| 文件上传 | 10 请求 | 每分钟 |
| 文件下载 | 50 请求 | 每分钟 |
| 编辑器操作 | 200 请求 | 每分钟 |

### 文件大小限制

| 操作 | 限制 |
|------|------|
| 单文件上传 | 100 MB |
| 总上传大小 | 50 GB |
| 编辑器文件 | 10 MB |
| 预览文件 | 1 MB |

### 响应时间

| 操作 | 目标响应时间 |
|------|--------------|
| 文件列表 | < 100ms |
| 文件上传 | < 1s (每MB) |
| 文件下载 | < 500ms |
| 编辑器打开 | < 200ms |
| 搜索操作 | < 300ms |

## 🐛 错误代码

### 文件操作错误

| 错误代码 | HTTP状态 | 说明 |
|----------|----------|------|
| `FILE_NOT_FOUND` | 404 | 文件不存在 |
| `FILE_TOO_LARGE` | 413 | 文件过大 |
| `INVALID_PATH` | 400 | 无效路径 |
| `PERMISSION_DENIED` | 403 | 权限不足 |
| `DISK_FULL` | 507 | 磁盘空间不足 |

### 编辑器错误

| 错误代码 | HTTP状态 | 说明 |
|----------|----------|------|
| `FILE_NOT_EDITABLE` | 400 | 文件不可编辑 |
| `ENCODING_ERROR` | 400 | 编码错误 |
| `FILE_BINARY` | 400 | 二进制文件 |
| `FILE_LOCKED` | 423 | 文件被锁定 |

### 系统错误

| 错误代码 | HTTP状态 | 说明 |
|----------|----------|------|
| `RATE_LIMIT_EXCEEDED` | 429 | 请求频率过高 |
| `SERVICE_UNAVAILABLE` | 503 | 服务不可用 |
| `MAINTENANCE_MODE` | 503 | 维护模式 |

## 📱 SDK 和工具

### Python SDK

```python
from file_manager_client import FileManagerClient

client = FileManagerClient(
    base_url="http://localhost:8888",
    api_key="your-api-key"
)

# 获取文件列表
files = client.list_files("/documents")

# 上传文件
result = client.upload_file("local_file.txt", "/uploads/")

# 编辑文件
content = client.edit_file_open("/code/main.py")
client.edit_file_save("/code/main.py", modified_content)
```

### JavaScript SDK

```javascript
import FileManagerAPI from 'file-manager-api';

const api = new FileManagerAPI({
  baseURL: 'http://localhost:8888',
  apiKey: 'your-api-key'
});

// 获取文件列表
const files = await api.listFiles('/documents');

// 上传文件
const result = await api.uploadFile(fileInput.files[0], '/uploads/');
```

### cURL 示例集合

```bash
# 获取系统信息
curl "http://localhost:8888/api/info"

# 上传文件
curl -X POST -F "files=@file.txt" "http://localhost:8888/api/upload"

# 下载文件
curl "http://localhost:8888/api/download?path=/file.txt" -o file.txt

# 编辑文件
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"path": "/test.py", "content": "print(\"Hello\")"}' \
  "http://localhost:8888/api/editor/save"
```

## 📝 更新日志

### v2.0.0 (2024-01-01)
- ✨ 新增在线编辑器 API
- ✨ 新增文件搜索功能
- 🔧 改进文件上传 API
- 🔧 优化响应格式
- 🐛 修复路径安全问题

### v1.5.0 (2023-12-01)
- ✨ 新增批量文件操作
- ✨ 新增文件预览 API
- 🔧 改进错误处理

---

<div align="center">
  <p><strong>📡 API 文档持续更新中</strong></p>
  <p>如有疑问或建议，欢迎通过 <a href="../../issues">Issues</a> 反馈</p>
  <p><em>最后更新: 2024年</em></p>
</div>
