// 全局变量
let currentPath = ''; // 当前路径（相对于根目录）
let selectedItem = null; // 当前选中的项目（用于移动/复制操作）
let operationType = ''; // 操作类型（'move' 或 'copy'）
let notificationTimeout = null; // 通知超时ID

// DOM 元素
const uploadBtn = document.getElementById('upload-btn');
const newFolderBtn = document.getElementById('new-folder-btn');
const fileUploadInput = document.getElementById('file-upload');
const fileListElement = document.getElementById('file-list');
const breadcrumbElement = document.getElementById('breadcrumb');
const statusMessage = document.getElementById('status-message');
const notificationContainer = document.getElementById('notification-container');
const loadingIndicator = document.getElementById('loading-indicator');

// 模态框元素
const overlay = document.getElementById('overlay');
const newFolderModal = document.getElementById('new-folder-modal');
const newFolderNameInput = document.getElementById('new-folder-name');
const createFolderBtn = document.getElementById('create-folder-btn');
const cancelFolderBtn = document.getElementById('cancel-folder-btn');
const renameModal = document.getElementById('rename-modal');
const renameInput = document.getElementById('rename-input');
const confirmRenameBtn = document.getElementById('confirm-rename-btn');
const cancelRenameBtn = document.getElementById('cancel-rename-btn');
const moveCopyModal = document.getElementById('move-copy-modal');
const moveCopyTitle = document.getElementById('move-copy-title');
const folderTree = document.getElementById('folder-tree');
const confirmMoveCopyBtn = document.getElementById('confirm-move-copy-btn');
const cancelMoveCopyBtn = document.getElementById('cancel-move-copy-btn');

// 错误处理配置
const ERROR_CONFIG = {
    retryAttempts: 3,
    retryDelay: 1000,
    showDetails: false, // 是否显示详细错误信息
    autoHideDelay: 8000, // 错误通知自动隐藏时间
    maxNotifications: 5 // 最大同时显示的通知数量
};

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM内容加载完成，开始初始化");
    
    // 上传按钮点击事件
    uploadBtn.addEventListener('click', () => {
        fileUploadInput.click();
    });
    
    // 文件上传事件
    fileUploadInput.addEventListener('change', uploadFiles);
    
    // 新建文件夹按钮点击事件
    newFolderBtn.addEventListener('click', showNewFolderModal);
    
    // 创建文件夹按钮点击事件
    createFolderBtn.addEventListener('click', createFolder);
    
    // 取消创建文件夹按钮点击事件
    cancelFolderBtn.addEventListener('click', hideNewFolderModal);
    
    // 确认重命名按钮点击事件
    confirmRenameBtn.addEventListener('click', confirmRename);
    
    // 取消重命名按钮点击事件
    cancelRenameBtn.addEventListener('click', hideRenameModal);
    
    // 确认移动/复制按钮点击事件
    confirmMoveCopyBtn.addEventListener('click', confirmMoveCopy);
    
    // 取消移动/复制按钮点击事件
    cancelMoveCopyBtn.addEventListener('click', hideMoveCopyModal);
    
    // 添加键盘事件监听器
    addKeyboardEventListeners();
    
    // 添加模态框拖动功能
    makeModalsDraggable();
    
    // 初始化面包屑导航事件处理
    initBreadcrumbEvents();
    console.log("面包屑导航事件处理已初始化");
    
    // 页面加载时自动加载文件列表和更新面包屑导航
    loadFileList();
    updateBreadcrumb();
    
    // 显示欢迎通知
    showNotification('欢迎使用文件管理系统', 'info');
    
    console.log("页面初始化完成");
});

// 增强的错误处理函数
function showError(message, details = null, retryFunction = null) {
    const notification = document.createElement('div');
    notification.className = 'notification error';
    
    let content = `<i class="fas fa-exclamation-triangle"></i> ${message}`;
    
    // 添加详细信息（如果启用）
    if (details && ERROR_CONFIG.showDetails) {
        content += `<details><summary>详细信息</summary><pre>${details}</pre></details>`;
    }
    
    // 添加重试按钮（如果提供）
    if (retryFunction) {
        content += `<button class="retry-btn" onclick="this.parentElement.remove(); ${retryFunction.name}()">重试</button>`;
    }
    
    notification.innerHTML = content;
    
    // 添加错误通知的特殊样式
    notification.style.borderLeft = '4px solid #dc3545';
    notification.style.backgroundColor = '#f8d7da';
    notification.style.color = '#721c24';
    
    // 限制通知数量
    const currentNotifications = notificationContainer.querySelectorAll('.notification.error');
    if (currentNotifications.length >= ERROR_CONFIG.maxNotifications) {
        currentNotifications[0].remove();
    }
    
    notificationContainer.appendChild(notification);
    
    // 自动隐藏（错误通知显示时间更长）
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, ERROR_CONFIG.autoHideDelay);
    
    // 记录错误到控制台
    console.error('用户错误:', message, details);
    
    // 记录到日志（如果可用）
    logError(message, details);
}

// 增强的成功通知函数
function showSuccess(message, details = null) {
    const notification = document.createElement('div');
    notification.className = 'notification success';
    
    let content = `<i class="fas fa-check-circle"></i> ${message}`;
    
    if (details && ERROR_CONFIG.showDetails) {
        content += `<details><summary>详细信息</summary><pre>${details}</pre></details>`;
    }
    
    notification.innerHTML = content;
    notification.style.borderLeft = '4px solid #28a745';
    notification.style.backgroundColor = '#d4edda';
    notification.style.color = '#155724';
    
    notificationContainer.appendChild(notification);
    
    // 成功通知显示时间较短
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
    
    console.log('用户成功:', message, details);
}

// 增强的警告通知函数
function showWarning(message, details = null) {
    const notification = document.createElement('div');
    notification.className = 'notification warning';
    
    let content = `<i class="fas fa-exclamation-triangle"></i> ${message}`;
    
    if (details && ERROR_CONFIG.showDetails) {
        content += `<details><summary>详细信息</summary><pre>${details}</pre></details>`;
    }
    
    notification.innerHTML = content;
    notification.style.borderLeft = '4px solid #ffc107';
    notification.style.backgroundColor = '#fff3cd';
    notification.style.color = '#856404';
    
    notificationContainer.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 6000);
    
    console.warn('用户警告:', message, details);
}

// 增强的信息通知函数
function showInfo(message, details = null) {
    const notification = document.createElement('div');
    notification.className = 'notification info';
    
    let content = `<i class="fas fa-info-circle"></i> ${message}`;
    
    if (details && ERROR_CONFIG.showDetails) {
        content += `<details><summary>详细信息</summary><pre>${details}</pre></details>`;
    }
    
    notification.innerHTML = content;
    notification.style.borderLeft = '4px solid #17a2b8';
    notification.style.backgroundColor = '#d1ecf1';
    notification.style.color = '#0c5460';
    
    notificationContainer.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 4000);
    
    console.log('用户信息:', message, details);
}

// 统一的通知函数（保持向后兼容）
function showNotification(message, type = 'info', details = null) {
    switch (type.toLowerCase()) {
        case 'error':
            showError(message, details);
            break;
        case 'success':
            showSuccess(message, details);
            break;
        case 'warning':
            showWarning(message, details);
            break;
        case 'info':
        default:
            showInfo(message, details);
            break;
    }
}

// 错误日志记录
function logError(message, details = null) {
    try {
        const errorLog = {
            timestamp: new Date().toISOString(),
            message: message,
            details: details,
            url: window.location.href,
            userAgent: navigator.userAgent,
            stack: new Error().stack
        };
        
        // 发送到服务器（如果可用）
        if (typeof logErrorToServer === 'function') {
            logErrorToServer(errorLog);
        }
        
        // 存储到本地存储
        const errorLogs = JSON.parse(localStorage.getItem('errorLogs') || '[]');
        errorLogs.push(errorLog);
        
        // 只保留最近100条错误记录
        if (errorLogs.length > 100) {
            errorLogs.splice(0, errorLogs.length - 100);
        }
        
        localStorage.setItem('errorLogs', JSON.stringify(errorLogs));
        
    } catch (e) {
        console.error('记录错误日志失败:', e);
    }
}

// 网络请求错误处理
function handleNetworkError(error, operation = '操作') {
    let userMessage = '网络请求失败';
    let technicalDetails = '';
    
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
        userMessage = '无法连接到服务器，请检查网络连接';
        technicalDetails = '网络连接失败或服务器无响应';
    } else if (error.status === 404) {
        userMessage = '请求的资源不存在';
        technicalDetails = `HTTP 404: ${error.statusText}`;
    } else if (error.status === 500) {
        userMessage = '服务器内部错误';
        technicalDetails = `HTTP 500: ${error.statusText}`;
    } else if (error.status >= 400) {
        userMessage = '请求失败';
        technicalDetails = `HTTP ${error.status}: ${error.statusText}`;
    } else if (error.status === 0) {
        userMessage = '网络连接被中断';
        technicalDetails = '请求被取消或网络中断';
    }
    
    showError(`${operation}失败: ${userMessage}`, technicalDetails);
    
    // 记录详细错误信息
    console.error(`${operation}网络错误:`, {
        message: userMessage,
        technical: technicalDetails,
        original: error
    });
}

// 重试机制
function retryOperation(operation, maxAttempts = ERROR_CONFIG.retryAttempts) {
    return function(...args) {
        let attempts = 0;
        
        function attempt() {
            attempts++;
            try {
                return operation.apply(this, args);
            } catch (error) {
                if (attempts < maxAttempts) {
                    console.warn(`操作失败，${ERROR_CONFIG.retryDelay}ms后重试 (${attempts}/${maxAttempts}):`, error);
                    
                    setTimeout(() => {
                        attempt();
                    }, ERROR_CONFIG.retryDelay * attempts); // 递增延迟
                    
                    showWarning(`操作失败，正在重试 (${attempts}/${maxAttempts})...`);
                } else {
                    console.error(`操作失败，已达到最大重试次数 (${maxAttempts}):`, error);
                    showError('操作失败，已达到最大重试次数', error.message);
                    throw error;
                }
            }
        }
        
        return attempt();
    };
}

// 增强的API请求函数
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
        ...options
    };
    
    try {
        const response = await fetch(url, defaultOptions);
        
        // 检查HTTP状态码
        if (!response.ok) {
            const error = new Error(`HTTP ${response.status}: ${response.statusText}`);
            error.status = response.status;
            error.statusText = response.statusText;
            
            // 尝试解析错误响应
            try {
                const errorData = await response.json();
                error.details = errorData;
            } catch (e) {
                // 如果无法解析JSON，使用文本
                error.details = await response.text();
            }
            
            throw error;
        }
        
        // 尝试解析JSON响应
        try {
            return await response.json();
        } catch (e) {
            // 如果不是JSON，返回文本
            return await response.text();
        }
        
    } catch (error) {
        // 网络错误处理
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            handleNetworkError(error, 'API请求');
        } else {
            // HTTP错误处理
            handleNetworkError(error, 'API请求');
        }
        throw error;
    }
}

// 文件操作错误处理
function handleFileOperationError(error, operation, filePath) {
    let userMessage = `${operation}失败`;
    let technicalDetails = '';
    
    if (error.message.includes('权限')) {
        userMessage = `没有权限${operation}文件`;
        technicalDetails = '权限不足或文件被占用';
    } else if (error.message.includes('不存在')) {
        userMessage = `文件不存在`;
        technicalDetails = '文件已被删除或移动';
    } else if (error.message.includes('空间')) {
        userMessage = `磁盘空间不足`;
        technicalDetails = '请清理磁盘空间后重试';
    } else if (error.message.includes('类型')) {
        userMessage = `不支持的文件类型`;
        technicalDetails = '文件类型不在允许列表中';
    } else if (error.message.includes('大小')) {
        userMessage = `文件过大`;
        technicalDetails = '文件大小超过限制';
    }
    
    showError(userMessage, technicalDetails);
    
    // 记录文件操作错误
    logError(`${operation}失败: ${filePath}`, {
        operation: operation,
        filePath: filePath,
        error: error.message
    });
}

// 全局错误处理器
window.addEventListener('error', (event) => {
    const error = event.error || event;
    showError('页面发生错误', error.message);
    logError('页面错误', {
        message: error.message,
        filename: error.filename,
        lineno: error.lineno,
        colno: error.colno,
        stack: error.stack
    });
});

// 未处理的Promise拒绝
window.addEventListener('unhandledrejection', (event) => {
    showError('未处理的异步错误', event.reason);
    logError('未处理的Promise拒绝', {
        reason: event.reason,
        promise: event.promise
    });
});

// 添加键盘事件监听器
function addKeyboardEventListeners() {
    // 在新建文件夹模态框中按Enter键确认
    newFolderNameInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            createFolder();
        } else if (e.key === 'Escape') {
            hideNewFolderModal();
        }
    });
    
    // 在重命名模态框中按Enter键确认
    renameInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            confirmRename();
        } else if (e.key === 'Escape') {
            hideRenameModal();
        }
    });
    
    // 全局快捷键
    document.addEventListener('keydown', (e) => {
        // Ctrl+N: 新建文件夹
        if (e.ctrlKey && e.key === 'n') {
            e.preventDefault();
            showNewFolderModal();
        }
        
        // Ctrl+U: 上传文件
        if (e.ctrlKey && e.key === 'u') {
            e.preventDefault();
            fileUploadInput.click();
        }
        
        // F5: 刷新文件列表
        if (e.key === 'F5') {
            e.preventDefault();
            loadFileList();
        }
        
        // Escape: 关闭所有模态框
        if (e.key === 'Escape') {
            hideAllModals();
        }
    });
}

// 关闭所有模态框
function hideAllModals() {
    hideNewFolderModal();
    hideRenameModal();
    hideMoveCopyModal();
}

// 使模态框可拖动
function makeModalsDraggable() {
    const modals = [newFolderModal, renameModal, moveCopyModal];
    
    modals.forEach(modal => {
        const header = modal.querySelector('h3');
        if (header) {
            header.style.cursor = 'move';
            
            let isDragging = false;
            let offsetX, offsetY;
            
            header.addEventListener('mousedown', (e) => {
                isDragging = true;
                offsetX = e.clientX - modal.getBoundingClientRect().left;
                offsetY = e.clientY - modal.getBoundingClientRect().top;
                
                // 添加临时样式
                modal.style.transition = 'none';
                modal.style.opacity = '0.9';
            });
            
            document.addEventListener('mousemove', (e) => {
                if (isDragging) {
                    const x = e.clientX - offsetX;
                    const y = e.clientY - offsetY;
                    
                    // 确保模态框不会被拖出视口
                    const maxX = window.innerWidth - modal.offsetWidth;
                    const maxY = window.innerHeight - modal.offsetHeight;
                    
                    modal.style.left = Math.max(0, Math.min(x, maxX)) + 'px';
                    modal.style.top = Math.max(0, Math.min(y, maxY)) + 'px';
                    modal.style.transform = 'none';
                }
            });
            
            document.addEventListener('mouseup', () => {
                if (isDragging) {
                    isDragging = false;
                    
                    // 恢复样式
                    modal.style.opacity = '1';
                    modal.style.transition = 'opacity 0.3s ease';
                }
            });
        }
    });
}

// 加载文件列表
async function loadFileList() {
    console.log("开始加载文件列表，当前路径：", currentPath);
    try {
        showLoading(true);
        
        // 添加时间戳参数来破坏浏览器缓存
        const timestamp = Date.now();
        const url = `/api/list?path=${encodeURIComponent(currentPath)}&_t=${timestamp}`;
        console.log("请求URL：", url);
        
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
        });
        console.log("收到响应：", response.status, response.statusText);
        
        const data = await response.json();
        console.log("响应数据：", data);
        
        if (response.ok) {
            console.log("加载成功，渲染文件列表");
            renderFileList(data.items);
        } else {
            console.error("加载失败：", data.message);
            showNotification(data.message, 'error');
        }
    } catch (error) {
        console.error("加载文件列表时发生错误：", error);
        const errorMsg = '加载文件列表时发生错误: ' + error.message;
        showNotification(errorMsg, 'error');
    } finally {
        showLoading(false);
        console.log("文件列表加载完成");
    }
}

// 渲染文件列表
function renderFileList(items) {
    // 先清空列表，并添加淡出效果
    fileListElement.classList.add('fade-out');
    
    setTimeout(() => {
        fileListElement.innerHTML = '';
        
        if (items.length === 0) {
            // 显示空文件夹提示
            fileListElement.innerHTML = '<tr><td colspan="4" class="empty-message">当前文件夹为空</td></tr>';
        } else {
            // 对项目进行排序：先文件夹，后文件，按名称字母顺序排序
            items.sort((a, b) => {
                if (a.type !== b.type) {
                    return a.type === 'directory' ? -1 : 1;
                }
                return a.name.localeCompare(b.name);
            });
            
            // 计算统计信息
            let totalFiles = 0;
            let totalSize = 0;
            
            items.forEach((item, index) => {
                if (item.type === 'file') {
                    totalFiles++;
                    totalSize += item.size || 0;
                }
                
                const row = document.createElement('tr');
                row.style.animationDelay = `${index * 0.05}s`; // 添加延迟动画效果
                
                // 文件大小格式化
                const sizeText = item.type === 'directory' ? '-' : formatFileSize(item.size);
                
                // 图标类
                const iconClass = item.type === 'directory' ? 'fas fa-folder folder-icon' : getFileIconClass(item.name);
                
                // 获取修改时间
                let modifiedTime = '-';
                if (item.modified) {
                    try {
                        // 处理Unix时间戳（秒）
                        const timestamp = typeof item.modified === 'number' ? item.modified * 1000 : item.modified;
                        const date = new Date(timestamp);
                        
                        // 检查日期是否有效
                        if (!isNaN(date.getTime())) {
                            modifiedTime = date.toLocaleString('zh-CN', {
                                year: 'numeric',
                                month: '2-digit',
                                day: '2-digit',
                                hour: '2-digit',
                                minute: '2-digit',
                                second: '2-digit'
                            });
                        } else {
                            modifiedTime = '无效日期';
                        }
                    } catch (error) {
                        console.warn('日期格式化失败:', error);
                        modifiedTime = '日期错误';
                    }
                }
                
                // 检查文件是否可编辑
                const extension = item.name.split('.').pop().toLowerCase();
                const editableExtensions = [
                    'txt', 'md', 'log', 'py', 'js', 'ts', 'html', 'css', 'scss', 'sass',
                    'java', 'cpp', 'c', 'h', 'hpp', 'cs', 'php', 'rb', 'go', 'rs', 'swift',
                    'kt', 'scala', 'sql', 'xml', 'json', 'yaml', 'yml', 'toml', 'ini', 'cfg',
                    'conf', 'env', 'gitignore', 'dockerignore', 'editorconfig', 'eslintrc',
                    'prettierrc', 'babelrc', 'csv', 'tsv', 'tex', 'bib', 'rst'
                ];
                const isEditable = item.type === 'file' && editableExtensions.includes(extension);
                const editableClass = isEditable ? 'editable' : '';
                
                row.innerHTML = `
                    <td>
                        <a href="#" class="file-name ${editableClass}" data-path="${item.path}" data-type="${item.type}">
                            <i class="${iconClass} file-icon"></i>
                            ${escapeHtml(item.name)}
                        </a>
                    </td>
                    <td>${sizeText}</td>
                    <td>${modifiedTime}</td>
                    <td class="file-actions">
                        ${item.type === 'file' ? `
                            <button class="file-action-btn download-btn" title="下载" data-path="${item.path}">
                                <i class="fas fa-download"></i>
                            </button>
                            <button class="file-action-btn edit-btn" title="编辑" data-path="${item.path}" data-name="${escapeHtml(item.name)}">
                                <i class="fas fa-code"></i>
                            </button>
                        ` : ''}
                        <button class="file-action-btn rename-btn" title="重命名" data-path="${item.path}" data-name="${escapeHtml(item.name)}">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="file-action-btn copy-btn" title="复制" data-path="${item.path}" data-name="${escapeHtml(item.name)}" data-type="${item.type}">
                            <i class="fas fa-copy"></i>
                        </button>
                        <button class="file-action-btn move-btn" title="移动" data-path="${item.path}" data-name="${escapeHtml(item.name)}" data-type="${item.type}">
                            <i class="fas fa-cut"></i>
                        </button>
                        <button class="file-action-btn delete-btn" title="删除" data-path="${item.path}" data-name="${escapeHtml(item.name)}" data-type="${item.type}">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                `;
                
                fileListElement.appendChild(row);
            });
            
            // 更新统计信息
            updateFileStats(items.length, totalSize);
        }
        
        // 添加事件监听器
        addFileListEventListeners();
        
        // 移除淡出效果，添加淡入效果
        fileListElement.classList.remove('fade-out');
        fileListElement.classList.add('fade-in');
        
        // 动画结束后移除淡入类
        setTimeout(() => {
            fileListElement.classList.remove('fade-in');
        }, 500);
    }, 300); // 等待淡出动画完成
}

// 更新文件统计信息
function updateFileStats(totalItems, totalSize) {
    const totalFilesElement = document.getElementById('total-files');
    const totalSizeElement = document.getElementById('total-size');
    
    if (totalFilesElement) {
        totalFilesElement.textContent = totalItems;
    }
    
    if (totalSizeElement) {
        totalSizeElement.textContent = formatFileSize(totalSize);
    }
}

// 添加文件列表事件监听器
function addFileListEventListeners() {
    console.log("开始添加文件列表事件监听器");
    
    // 文件/文件夹点击事件
    document.querySelectorAll('.file-name').forEach(element => {
        element.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            const path = element.getAttribute('data-path');
            const type = element.getAttribute('data-type');
            const fileName = element.textContent.trim();
            
            console.log("文件名点击事件触发:", { path, type, fileName });
            
            if (type === 'directory') {
                // 打开文件夹
                console.log("打开文件夹:", path);
                currentPath = path;
                loadFileList();
                updateBreadcrumb();
            } else {
                // 检查文件是否可编辑
                const extension = fileName.split('.').pop().toLowerCase();
                const editableExtensions = [
                    'txt', 'md', 'log', 'py', 'js', 'ts', 'html', 'css', 'scss', 'sass',
                    'java', 'cpp', 'c', 'h', 'hpp', 'cs', 'php', 'rb', 'go', 'rs', 'swift',
                    'kt', 'scala', 'sql', 'xml', 'json', 'yaml', 'yml', 'toml', 'ini', 'cfg',
                    'conf', 'env', 'gitignore', 'dockerignore', 'editorconfig', 'eslintrc',
                    'prettierrc', 'babelrc', 'csv', 'tsv', 'tex', 'bib', 'rst'
                ];
                
                if (editableExtensions.includes(extension)) {
                    // 可编辑文件，进入编辑器
                    console.log("可编辑文件，进入编辑器:", path, fileName);
                    openFileEditor(path, fileName);
                } else {
                    // 不可编辑文件，下载
                    console.log("不可编辑文件，下载:", path, fileName);
                    downloadFile(path);
                }
            }
        });
    });
    
    // 下载按钮点击事件
    document.querySelectorAll('.download-btn').forEach(button => {
        button.addEventListener('click', () => {
            const path = button.getAttribute('data-path');
            downloadFile(path);
        });
    });
    
    // 编辑按钮点击事件
    document.querySelectorAll('.edit-btn').forEach(button => {
        button.addEventListener('click', () => {
            const path = button.getAttribute('data-path');
            const name = button.getAttribute('data-name');
            openFileEditor(path, name);
        });
    });
    
    // 重命名按钮点击事件
    document.querySelectorAll('.rename-btn').forEach(button => {
        button.addEventListener('click', () => {
            const path = button.getAttribute('data-path');
            const name = button.getAttribute('data-name');
            showRenameModal(path, name);
        });
    });
    
    // 复制按钮点击事件
    document.querySelectorAll('.copy-btn').forEach(button => {
        button.addEventListener('click', () => {
            const path = button.getAttribute('data-path');
            const name = button.getAttribute('data-name');
            const type = button.getAttribute('data-type');
            showMoveCopyModal('copy', path, name, type);
        });
    });
    
    // 移动按钮点击事件
    document.querySelectorAll('.move-btn').forEach(button => {
        button.addEventListener('click', () => {
            const path = button.getAttribute('data-path');
            const name = button.getAttribute('data-name');
            const type = button.getAttribute('data-type');
            showMoveCopyModal('move', path, name, type);
        });
    });
    
    // 删除按钮点击事件
    document.querySelectorAll('.delete-btn').forEach(button => {
        button.addEventListener('click', () => {
            const path = button.getAttribute('data-path');
            const name = button.getAttribute('data-name');
            const type = button.getAttribute('data-type');
            confirmDelete(path, name, type);
        });
    });
    
    // 添加行悬停效果
    document.querySelectorAll('#file-list tr').forEach(row => {
        row.addEventListener('mouseenter', () => {
            row.classList.add('row-hover');
        });
        
        row.addEventListener('mouseleave', () => {
            row.classList.remove('row-hover');
        });
    });
    
    console.log("文件列表事件监听器添加完成");
}

// 初始化面包屑导航事件处理
function initBreadcrumbEvents() {
    // 使用事件委托，将点击事件处理程序绑定到面包屑导航的父元素上
    breadcrumbElement.addEventListener('click', function(e) {
        // 检查点击的是否是链接元素
        if (e.target.tagName === 'A' || e.target.parentElement.tagName === 'A') {
            e.preventDefault();
            e.stopPropagation(); // 阻止事件冒泡
            
            // 获取被点击的链接元素
            const link = e.target.tagName === 'A' ? e.target : e.target.parentElement;
            const clickedPath = link.getAttribute('data-path');
            
            console.log("面包屑点击事件触发，路径：", clickedPath);
            
            // 更新当前路径并加载文件列表
            currentPath = clickedPath;
            console.log("设置当前路径为：", currentPath);
            loadFileList();
            updateBreadcrumb();
        }
    });
    
    console.log("面包屑导航事件处理程序已初始化");
}

// 更新面包屑导航
function updateBreadcrumb() {
    console.log("开始更新面包屑导航，当前路径：", currentPath);
    breadcrumbElement.innerHTML = '';
    
    // 添加根目录
    const homeItem = document.createElement('li');
    homeItem.className = 'breadcrumb-item'; // 添加正确的CSS类
    const homeLink = document.createElement('a');
    homeLink.href = "#";
    homeLink.setAttribute('data-path', '');
    homeLink.innerHTML = `<i class="fas fa-home"></i> 首页`;
    homeItem.appendChild(homeLink);
    breadcrumbElement.appendChild(homeItem);
    
    // 如果当前路径不是根目录，添加路径部分
    if (currentPath) {
        const parts = currentPath.split('/');
        let accumulatedPath = '';
        
        console.log("路径部分：", parts);
        
        parts.forEach((part, index) => {
            // 正确构建累积路径
            accumulatedPath += (accumulatedPath ? '/' : '') + part;
            console.log(`构建路径部分 ${index + 1}/${parts.length}:`, part, "累积路径:", accumulatedPath);
            
            const item = document.createElement('li');
            item.className = 'breadcrumb-item'; // 添加正确的CSS类
            
            if (index === parts.length - 1) {
                // 最后一项不可点击
                item.textContent = part;
                item.classList.add('active');
                console.log("添加最后一项（不可点击）:", part);
            } else {
                // 中间项可点击
                const link = document.createElement('a');
                link.href = "#";
                link.setAttribute('data-path', accumulatedPath);
                link.textContent = part;
                console.log("添加可点击项:", part, "路径:", accumulatedPath);
                item.appendChild(link);
            }
            
            breadcrumbElement.appendChild(item);
        });
    }
    
    console.log("面包屑导航更新完成");
}

// 上传文件
async function uploadFiles() {
    if (fileUploadInput.files.length === 0) {
        return;
    }
    
    try {
        showLoading(true);
        
        const formData = new FormData();
        formData.append('path', currentPath);
        
        // 添加所有选择的文件
        for (let i = 0; i < fileUploadInput.files.length; i++) {
            formData.append('files', fileUploadInput.files[i]);
        }
        
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // 检查是否有部分文件上传失败
            if (data.errors && data.errors.length > 0) {
                // 有错误，显示详细的错误信息
                if (data.total_uploaded > 0) {
                    showNotification(`成功上传 ${data.total_uploaded} 个文件，但有 ${data.errors.length} 个文件失败`, 'warning');
                    // 显示详细错误信息
                    showDetailedErrors(data.errors, '部分文件上传失败');
                } else {
                    showNotification('所有文件上传失败', 'error');
                    // 显示详细错误信息
                    showDetailedErrors(data.errors, '文件上传失败详情');
                    return; // 不刷新文件列表
                }
            } else {
                // 所有文件都上传成功
                showNotification(`成功上传 ${data.total_uploaded || data.files?.length || 0} 个文件`, 'success');
            }
            
            console.log("上传完成，准备刷新文件列表...");
            // 强制刷新文件列表
            await loadFileList();
            console.log("文件列表刷新完成");
        } else {
            // 服务器返回错误
            showNotification(data.message || '上传失败', 'error');
        }
    } catch (error) {
        const errorMsg = '上传文件时发生错误: ' + error.message;
        showNotification(errorMsg, 'error');
    } finally {
        showLoading(false);
        fileUploadInput.value = ''; // 清空文件输入
    }
}

// 显示详细错误信息
function showDetailedErrors(errors, title) {
    // 创建错误详情模态框
    const errorModal = document.createElement('div');
    errorModal.className = 'modal';
    errorModal.id = 'error-details-modal';
    errorModal.style.display = 'block';
    
    errorModal.innerHTML = `
        <div class="modal-header">
            <h3><i class="fas fa-exclamation-triangle"></i> ${title}</h3>
        </div>
        <div class="modal-body">
            <div class="error-list">
                ${errors.map(error => `<div class="error-item">• ${error}</div>`).join('')}
            </div>
        </div>
        <div class="modal-actions">
            <button id="close-error-modal" class="btn-secondary">关闭</button>
        </div>
    `;
    
    // 添加到页面
    document.body.appendChild(errorModal);
    
    // 显示遮罩
    if (overlay) {
        overlay.style.display = 'block';
    }
    
    // 居中显示模态框
    centerModal(errorModal);
    
    // 绑定关闭事件
    document.getElementById('close-error-modal').addEventListener('click', () => {
        document.body.removeChild(errorModal);
        if (overlay) {
            overlay.style.display = 'none';
        }
    });
    
    // 点击遮罩关闭
    if (overlay) {
        overlay.addEventListener('click', () => {
            document.body.removeChild(errorModal);
            overlay.style.display = 'none';
        });
    }
}

// 下载文件
function downloadFile(path) {
    console.log("下载文件:", path);
    window.location.href = `/api/download?path=${encodeURIComponent(path)}`;
}

// 显示新建文件夹模态框
function showNewFolderModal() {
    newFolderNameInput.value = '';
    newFolderModal.style.display = 'block';
    overlay.style.display = 'block';
    newFolderNameInput.focus();
    
    // 居中显示模态框
    centerModal(newFolderModal);
}

// 隐藏新建文件夹模态框
function hideNewFolderModal() {
    newFolderModal.style.display = 'none';
    overlay.style.display = 'none';
}

// 创建文件夹
async function createFolder() {
    const folderName = newFolderNameInput.value.trim();
    
    if (!folderName) {
        showNotification('文件夹名称不能为空', 'error');
        return;
    }
    
    try {
        showLoading(true);
        hideNewFolderModal();
        
        const response = await fetch('/api/create_folder', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                path: currentPath,
                name: folderName
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('文件夹创建成功', 'success');
            console.log("文件夹创建成功，准备刷新文件列表...");
            // 强制刷新文件列表
            await loadFileList();
            console.log("文件列表刷新完成");
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        const errorMsg = '创建文件夹时发生错误: ' + error.message;
        showNotification(errorMsg, 'error');
    } finally {
        showLoading(false);
    }
}

// 显示重命名模态框
function showRenameModal(path, name) {
    renameInput.value = name;
    renameInput.setAttribute('data-path', path);
    renameModal.style.display = 'block';
    overlay.style.display = 'block';
    renameInput.focus();
    renameInput.select();
    
    // 居中显示模态框
    centerModal(renameModal);
}

// 隐藏重命名模态框
function hideRenameModal() {
    renameModal.style.display = 'none';
    overlay.style.display = 'none';
}

// 确认重命名
async function confirmRename() {
    const newName = renameInput.value.trim();
    const path = renameInput.getAttribute('data-path');
    
    if (!newName) {
        showNotification('名称不能为空', 'error');
        return;
    }
    
    try {
        showLoading(true);
        hideRenameModal();
        
        const response = await fetch('/api/rename', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                path: path,
                new_name: newName
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('重命名成功', 'success');
            console.log("重命名成功，准备刷新文件列表...");
            // 强制刷新文件列表
            await loadFileList();
            console.log("文件列表刷新完成");
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        const errorMsg = '重命名时发生错误: ' + error.message;
        showNotification(errorMsg, 'error');
    } finally {
        showLoading(false);
    }
}

// 显示移动/复制模态框
async function showMoveCopyModal(type, path, name, itemType) {
    operationType = type;
    selectedItem = { path, name, type: itemType };
    
    // 设置标题
    moveCopyTitle.textContent = type === 'move' ? '移动到' : '复制到';
    
    // 显示模态框
    moveCopyModal.style.display = 'block';
    overlay.style.display = 'block';
    
    // 居中显示模态框
    centerModal(moveCopyModal);
    
    // 加载文件夹树
    await loadFolderTree();
}

// 隐藏移动/复制模态框
function hideMoveCopyModal() {
    moveCopyModal.style.display = 'none';
    overlay.style.display = 'none';
}

// 加载文件夹树
async function loadFolderTree() {
    try {
        folderTree.innerHTML = '<div class="loading-tree">加载中...</div>';
        
        // 获取根目录下的文件夹
        const response = await fetch('/api/list?path=');
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || '加载文件夹失败');
        }
        
        // 过滤出文件夹
        const folders = data.items.filter(item => item.type === 'directory');
        
        // 渲染文件夹树
        folderTree.innerHTML = '';
        
        // 添加根文件夹项
        const rootItem = document.createElement('li');
        rootItem.className = 'folder-item';
        rootItem.innerHTML = `
            <div class="folder-name ${currentPath === '' ? 'selected' : ''}" data-path="">
                <i class="fas fa-home"></i> 根目录
            </div>
            <ul class="subfolder-list"></ul>
        `;
        folderTree.appendChild(rootItem);
        
        // 添加根文件夹点击事件
        rootItem.querySelector('.folder-name').addEventListener('click', function() {
            document.querySelectorAll('.folder-name.selected').forEach(el => {
                el.classList.remove('selected');
            });
            this.classList.add('selected');
        });
        
        // 添加子文件夹
        const subfolderList = rootItem.querySelector('.subfolder-list');
        for (const folder of folders) {
            const folderItem = document.createElement('li');
            folderItem.className = 'folder-item';
            folderItem.innerHTML = `
                <div class="folder-name" data-path="${folder.path}">
                    <i class="fas fa-folder"></i> ${folder.name}
                    <i class="fas fa-chevron-right toggle-icon"></i>
                </div>
                <ul class="subfolder-list" style="display:none"></ul>
            `;
            
            // 添加文件夹点击事件
            const folderNameEl = folderItem.querySelector('.folder-name');
            folderNameEl.addEventListener('click', function() {
                document.querySelectorAll('.folder-name.selected').forEach(el => {
                    el.classList.remove('selected');
                });
                this.classList.add('selected');
            });
            
            // 添加展开/收缩事件
            const toggleIcon = folderItem.querySelector('.toggle-icon');
            const subList = folderItem.querySelector('.subfolder-list');
            toggleIcon.addEventListener('click', async function(e) {
                e.stopPropagation();
                
                if (subList.style.display === 'none') {
                    // 展开子目录
                    toggleIcon.classList.replace('fa-chevron-right', 'fa-chevron-down');
                    subList.style.display = 'block';
                    
                    // 如果子目录为空，则加载
                    if (subList.children.length === 0) {
                        await loadSubFolders(folder.path, subList);
                    }
                } else {
                    // 收缩子目录
                    toggleIcon.classList.replace('fa-chevron-down', 'fa-chevron-right');
                    subList.style.display = 'none';
                }
            });
            
            subfolderList.appendChild(folderItem);
        }
    } catch (error) {
        folderTree.innerHTML = `<div class="error-message">加载文件夹树时发生错误: ${error.message}</div>`;
    }
}

// 加载子文件夹
async function loadSubFolders(parentPath, container) {
    try {
        const loadingItem = document.createElement('li');
        loadingItem.className = 'loading-item';
        loadingItem.textContent = '加载中...';
        container.appendChild(loadingItem);
        
        const response = await fetch(`/api/list?path=${encodeURIComponent(parentPath)}`);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || '加载子文件夹失败');
        }
        
        // 过滤出文件夹
        const folders = data.items.filter(item => item.type === 'directory');
        
        // 移除加载提示
        container.removeChild(loadingItem);
        
        // 添加子文件夹
        for (const folder of folders) {
            const folderItem = document.createElement('li');
            folderItem.className = 'folder-item';
            folderItem.innerHTML = `
                <div class="folder-name" data-path="${folder.path}">
                    <i class="fas fa-folder"></i> ${folder.name}
                    <i class="fas fa-chevron-right toggle-icon"></i>
                </div>
                <ul class="subfolder-list" style="display:none"></ul>
            `;
            
            // 添加文件夹点击事件
            const folderNameEl = folderItem.querySelector('.folder-name');
            folderNameEl.addEventListener('click', function() {
                document.querySelectorAll('.folder-name.selected').forEach(el => {
                    el.classList.remove('selected');
                });
                this.classList.add('selected');
            });
            
            // 添加展开/收缩事件
            const toggleIcon = folderItem.querySelector('.toggle-icon');
            const subList = folderItem.querySelector('.subfolder-list');
            toggleIcon.addEventListener('click', async function(e) {
                e.stopPropagation();
                
                if (subList.style.display === 'none') {
                    // 展开子目录
                    toggleIcon.classList.replace('fa-chevron-right', 'fa-chevron-down');
                    subList.style.display = 'block';
                    
                    // 如果子目录为空，则加载
                    if (subList.children.length === 0) {
                        await loadSubFolders(folder.path, subList);
                    }
                } else {
                    // 收缩子目录
                    toggleIcon.classList.replace('fa-chevron-down', 'fa-chevron-right');
                    subList.style.display = 'none';
                }
            });
            
            container.appendChild(folderItem);
        }
    } catch (error) {
        const errorItem = document.createElement('li');
        errorItem.className = 'error-item';
        errorItem.textContent = `加载失败: ${error.message}`;
        container.appendChild(errorItem);
    }
}

// 确认移动/复制
async function confirmMoveCopy() {
    // 获取选中的目标文件夹
    const selectedFolder = document.querySelector('.folder-name.selected');
    
    if (!selectedFolder) {
        showNotification('请选择目标文件夹', 'error');
        return;
    }
    
    const targetPath = selectedFolder.getAttribute('data-path');
    
    // 检查是否在移动/复制到自身或子文件夹
    if (operationType === 'move' && (
        selectedItem.path === targetPath || 
        (selectedItem.type === 'directory' && targetPath.startsWith(selectedItem.path + '/'))
    )) {
        showNotification('不能移动到自身或其子文件夹', 'error');
        return;
    }
    
    try {
        showLoading(true);
        hideMoveCopyModal();
        
        const endpoint = operationType === 'move' ? '/api/move' : '/api/copy';
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                source: selectedItem.path,
                target: targetPath
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            const actionText = operationType === 'move' ? '移动' : '复制';
            showNotification(`${actionText}成功`, 'success');
            loadFileList(); // 重新加载文件列表
        } else {
            // 检查是否是目标路径已存在同名文件或目录的错误
            if (response.status === 409 && data.message.includes('目标路径已存在同名文件或目录')) {
                const errorMsg = `目标文件夹中已存在同名的文件或文件夹。请先删除目标位置的同名项，或者选择一个不同的目标文件夹。`;
                showNotification(errorMsg, 'error');
            } else {
                showNotification(data.message, 'error');
            }
        }
    } catch (error) {
        const actionText = operationType === 'move' ? '移动' : '复制';
        const errorMsg = `${actionText}时发生错误: ${error.message}`;
        showNotification(errorMsg, 'error');
    } finally {
        showLoading(false);
    }
}

// 确认删除
async function confirmDelete(path, name, type) {
    const typeText = type === 'directory' ? '文件夹' : '文件';
    
    if (!confirm(`确定要删除${typeText} "${name}" 吗？此操作不可恢复。`)) {
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch('/api/delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                path: path
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('删除成功', 'success');
            console.log("删除成功，准备刷新文件列表...");
            // 强制刷新文件列表
            await loadFileList();
            console.log("文件列表刷新完成");
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        const errorMsg = '删除时发生错误: ' + error.message;
        showNotification(errorMsg, 'error');
    } finally {
        showLoading(false);
    }
}

// 显示加载指示器
function showLoading(show) {
    if (show) {
        loadingIndicator.style.display = 'flex';
    } else {
        loadingIndicator.style.display = 'none';
    }
}

// 显示状态消息
function showStatus(message, type = 'info') {
    statusMessage.textContent = message;
    statusMessage.className = `status-message ${type}`;
    
    // 清除之前的类
    statusMessage.classList.remove('info', 'success', 'error', 'warning');
    statusMessage.classList.add(type);
    
    // 显示状态消息
    statusMessage.style.opacity = '1';
    
    // 如果是成功或错误消息，3秒后淡出
    if (type === 'success' || type === 'error') {
        setTimeout(() => {
            statusMessage.style.opacity = '0';
        }, 3000);
    }
}

// 居中显示模态框
function centerModal(modal) {
    modal.style.top = '50%';
    modal.style.left = '50%';
    modal.style.transform = 'translate(-50%, -50%)';
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// HTML转义
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    
    return text.replace(/[&<>"']/g, m => map[m]);
}

// 获取文件图标类
function getFileIconClass(filename) {
    const extension = filename.split('.').pop().toLowerCase();
    
    // 图片文件
    if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp'].includes(extension)) {
        return 'fas fa-image';
    }
    
    // 文档文件
    if (['doc', 'docx', 'odt', 'rtf'].includes(extension)) {
        return 'fas fa-file-word';
    }
    
    // 电子表格
    if (['xls', 'xlsx', 'ods', 'csv'].includes(extension)) {
        return 'fas fa-file-excel';
    }
    
    // 演示文稿
    if (['ppt', 'pptx', 'odp'].includes(extension)) {
        return 'fas fa-file-powerpoint';
    }
    
    // PDF文件
    if (extension === 'pdf') {
        return 'fas fa-file-pdf';
    }
    
    // 文本文件
    if (['txt', 'md', 'log'].includes(extension)) {
        return 'fas fa-file-alt';
    }
    
    // 代码文件
    if (['html', 'css', 'js', 'php', 'py', 'java', 'c', 'cpp', 'h', 'cs', 'rb', 'go', 'ts', 'json', 'xml'].includes(extension)) {
        return 'fas fa-file-code';
    }
    
    // 压缩文件
    if (['zip', 'rar', '7z', 'tar', 'gz', 'bz2'].includes(extension)) {
        return 'fas fa-file-archive';
    }
    
    // 音频文件
    if (['mp3', 'wav', 'ogg', 'flac', 'aac', 'm4a'].includes(extension)) {
        return 'fas fa-file-audio';
    }
    
    // 视频文件
    if (['mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv', 'webm'].includes(extension)) {
        return 'fas fa-file-video';
    }
    
    // 默认文件图标
    return 'fas fa-file';
}

// 打开文件编辑器
function openFileEditor(filePath, fileName) {
    console.log("打开文件编辑器:", filePath, fileName);
    
    // 检查文件是否支持编辑
    const extension = fileName.split('.').pop().toLowerCase();
    const editableExtensions = [
        'txt', 'md', 'log', 'py', 'js', 'ts', 'html', 'css', 'scss', 'sass',
        'java', 'cpp', 'c', 'h', 'hpp', 'cs', 'php', 'rb', 'go', 'rs', 'swift',
        'kt', 'scala', 'sql', 'xml', 'json', 'yaml', 'yml', 'toml', 'ini', 'cfg',
        'conf', 'env', 'gitignore', 'dockerignore', 'editorconfig', 'eslintrc',
        'prettierrc', 'babelrc', 'csv', 'tsv', 'tex', 'bib', 'rst'
    ];
    
    if (!editableExtensions.includes(extension)) {
        showNotification(`文件类型 .${extension} 不支持编辑`, 'warning');
        return;
    }
    
    // 跳转到编辑器页面
    const editorUrl = `/editor?file=${encodeURIComponent(filePath)}`;
    console.log("跳转到编辑器:", editorUrl);
    window.open(editorUrl, '_blank');
}
