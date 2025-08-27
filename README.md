# 文件管理系统 (File Manager System)

一个现代化的文件管理系统，支持在线编辑、权限管理、性能监控等功能。

## ✨ 主要特性

- 🗂️ **文件管理**: 浏览、上传、下载、重命名、删除文件
- 📝 **在线编辑**: 基于CodeMirror的代码编辑器，支持50+种编程语言
- 🔐 **用户认证**: 注册、登录、邮箱验证码、权限管理
- 📊 **系统监控**: 磁盘使用、内存状态、性能指标
- 🛡️ **安全防护**: 路径验证、文件类型检查、XSS防护
- 📝 **日志系统**: 结构化日志、JSON格式、自动轮转
- 💾 **数据存储**: MySQL数据库、Redis缓存
- 🌐 **网络下载**: 公网文件下载到服务器
- 🎨 **主题系统**: 多主题支持、自定义样式

## 🚀 快速开始

### 环境要求

- Python 3.8+
- MySQL 5.7+
- Redis 6.0+
- 现代浏览器

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd file_manager
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置数据库**
   - 创建MySQL数据库
   - 配置Redis服务
   - 修改配置文件

4. **启动应用**
   ```bash
   # 使用启动脚本（推荐）
   python scripts/start.py
   
   # 或直接启动
   python main.py
   ```

## ⚙️ 配置系统

### 配置文件结构

```
config/
├── config.yaml              # 主配置文件
├── environment.txt           # 环境配置文件
├── development.yaml         # 开发环境特定配置
├── production.yaml          # 生产环境特定配置
├── testing.yaml            # 测试环境特定配置
└── backups/                # 配置备份目录
```

### 环境配置

系统支持多环境配置，无需环境变量：

- **development**: 开发环境，启用调试功能
- **production**: 生产环境，优化性能和安全
- **testing**: 测试环境，用于测试和验证

### 配置管理

```bash
# 验证配置
python scripts/validate_config.py

# 管理配置
python scripts/manage_config.py info          # 显示配置信息
python scripts/manage_config.py backup        # 创建配置备份
python scripts/manage_config.py restore name  # 恢复配置备份
python scripts/manage_config.py export        # 导出配置
python scripts/manage_config.py import file   # 导入配置
```

## 🏗️ 项目结构

```
file_manager/
├── api/                    # API路由
├── config/                 # 配置文件
├── core/                   # 核心模块
├── services/               # 业务服务
├── static/                 # 静态资源
├── templates/              # 模板文件
├── utils/                  # 工具函数
├── scripts/                # 管理脚本
├── docs/                   # 文档
├── main.py                 # 主程序入口
└── requirements.txt        # 依赖列表
```

## 🔧 核心功能

### 文件管理
- 支持所有文件类型上传（已移除扩展名限制）
- 文件预览和在线编辑
- 批量操作和拖拽上传
- 文件搜索和排序

### 用户系统
- 邮箱验证码注册
- 安全的登录认证
- 权限管理和会话控制
- 操作日志记录

### 系统监控
- 实时性能监控
- 资源使用统计
- 健康检查
- 错误日志记录

## 📱 前端特性

- 响应式设计，支持移动端
- 多主题切换（浅色、深色、蓝色）
- 代码编辑器（语法高亮、自动补全）
- 拖拽上传和文件预览

## 🚀 性能优化

- Redis缓存系统
- 数据库连接池
- 文件分块上传
- 懒加载和虚拟滚动

## 📚 详细文档

- [配置系统文档](docs/CONFIGURATION.md) - 完整的配置说明和管理指南

## 🧪 测试

```bash
# 运行测试
pytest

# 代码覆盖率
pytest --cov=.

# 代码质量检查
flake8
black --check .
mypy .
```

## 📝 更新日志

### v2.0.0 (当前版本)

- ✨ 全新的配置系统，支持多环境配置
- 🚫 移除环境变量依赖，使用配置文件管理
- 🔧 优化配置管理器，支持热重载
- 📱 增强前端配置，支持主题切换
- 🛠️ 添加配置验证和管理工具
- 📚 完善文档和示例
- 🚫 移除文件扩展名上传限制

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

- 项目主页: [GitHub Repository]
- 问题反馈: [Issues]
- 功能建议: [Discussions]
- 邮箱: support@filemanager.local

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和用户！

---

**注意**: 本项目已完全移除环境变量依赖，使用配置文件进行管理。如需配置，请参考 [配置文档](docs/CONFIGURATION.md)。
