// 重构版文件管理系统 JavaScript
let currentPath = '.';  // 初始化为根目录，而不是空字符串
let currentView = 'list';
let currentUser = null;  // 当前用户信息

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log("文件管理系统初始化");
    
    initializeEventListeners();
    initializeSidebar();
    initializeSearch();
    initializeViewControls();
    initializeWebDownload();
    // 通知中心功能已移除
    initializeStorageInfo();
    
    // 检查剪贴板支持情况
    const clipboardSupport = checkClipboardSupport();
    
    // 直接加载文件列表
    currentView = 'files';
    // 获取当前用户信息并设置正确的初始路径
    getCurrentUserInfo().then(() => {
        loadFileList();
        updateBreadcrumb();
    }).catch((error) => {
        console.error('获取用户信息失败:', error);
        currentPath = '.';
        loadFileList();
        updateBreadcrumb();
    });
    
});



// 获取当前用户信息并设置正确的初始路径
async function getCurrentUserInfo() {
    try {
        // 获取当前用户信息
        
        // 尝试获取用户信息
                       const response = await fetch('/api/auth/user/info');
        if (response.ok) {
            const userData = await response.json();
            currentUser = userData;
            // 用户信息获取成功
            
            // 如果不是管理员，设置初始路径为用户目录
            if (currentUser && currentUser.user && currentUser.user.email !== 'admin@system.local') {
                // 从邮箱提取用户名
                const username = currentUser.user.email.split('@')[0];
                currentPath = `home/users/${username}`;
                // 设置普通用户初始路径
                
                // 更新用户显示
                updateUserDisplay(username, '用户');
            } else {
                // 管理员使用根目录，但让后端处理具体的根目录路径
                currentPath = '.';  // 管理员使用根目录
                // 设置管理员初始路径
                
                // 更新用户显示
                updateUserDisplay('admin', '管理员');
            }
        } else {
            console.warn('获取用户信息失败，使用默认路径');
            currentPath = '.';
        }
        
    } catch (error) {
        console.error('获取用户信息失败:', error);
        currentPath = '.';
    }
}

// 更新用户显示
function updateUserDisplay(username, role) {
    const userNameElement = document.getElementById('user-name');
    const userRoleElement = document.getElementById('user-role');
    
    if (userNameElement) {
        userNameElement.textContent = username;
    }
    
    if (userRoleElement) {
        userRoleElement.textContent = role;
    }
}



// 初始化事件监听器
function initializeEventListeners() {
    // 文件操作按钮
    const smartUploadBtn = document.getElementById('smart-upload-btn');
    const newFolderBtn = document.getElementById('new-folder-btn');
    const fileUploadInput = document.getElementById('file-upload');
    
    if (smartUploadBtn) smartUploadBtn.addEventListener('click', () => fileUploadInput?.click());
    if (fileUploadInput) fileUploadInput.addEventListener('change', smartUploadFiles);
    if (newFolderBtn) newFolderBtn.addEventListener('click', showNewFolderModal);
    
    // 模态框事件
    initializeModalEvents();
    
    // 键盘快捷键
    addKeyboardShortcuts();
}

// 初始化侧边栏
function initializeSidebar() {
    const sidebarToggle = document.getElementById('sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }
    
    // 侧边栏导航
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const view = link.dataset.view;
            if (view) switchView(view);
        });
    });
}

// 初始化搜索
function initializeSearch() {
    const searchInput = document.getElementById('global-search');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleSearch, 300));
    }
}

// 初始化视图控制
function initializeViewControls() {
    // 视图控制和排序功能已移除
    // 视图控制和排序功能已禁用
}

// 切换侧边栏
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) sidebar.classList.toggle('open');
}

// 切换视图模式
function switchViewMode(view) {
    // 视图切换功能已移除
    // 视图切换功能已禁用
}

// 处理搜索
function handleSearch(e) {
    const query = e.target.value.trim();
    if (query.length === 0) {
        loadFileList();
        return;
    }
    searchFiles(query);
}

// 搜索文件
async function searchFiles(query) {
    try {
        showLoading();
        // 正在搜索文件
        
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&path=${currentPath}`);
        // 搜索API响应
        
        if (response.status === 401) {
            showNotification('未登录或登录已过期，请先登录', 'warning');
            window.location.href = '/login';
            return;
        }
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        // 搜索API返回结果
        
        // 检查API返回的数据结构
        if (result && result.results && Array.isArray(result.results)) {
            // 后端返回的是 results 数组（当前实现）
            // 搜索成功
            const normalizedItems = normalizeFileItems(result.results);
            displaySearchResults(normalizedItems, query);
        } else if (result && result.items && Array.isArray(result.items)) {
            // API返回的是 items 数组
            // 搜索成功
            const normalizedItems = normalizeFileItems(result.items);
            displaySearchResults(normalizedItems, query);
        } else if (result && result.files && Array.isArray(result.files)) {
            // 兼容旧的API格式
            // 使用兼容格式
            displaySearchResults(result.files, query);
        } else if (result && result.success === false) {
            // API返回了明确的错误
            const errorMsg = result?.message || result?.error || '搜索失败';
            console.error('搜索API返回错误:', errorMsg);
            showNotification('搜索失败: ' + errorMsg, 'error');
        } else {
            // 未知的响应格式
            console.warn('搜索API返回格式不正确:', result);
            showNotification('搜索结果格式错误', 'error');
        }
    } catch (error) {
        console.error('搜索错误:', error);
        
        let errorMessage = '搜索过程中发生错误';
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            errorMessage = '网络连接失败，请检查网络设置';
        } else if (error.message.includes('HTTP')) {
            errorMessage = '服务器响应错误: ' + error.message;
        }
        
        showNotification(errorMessage, 'error');
    } finally {
        hideLoading();
    }
}

// 显示搜索结果
function displaySearchResults(files, query) {
    const fileList = document.getElementById('file-list');
    if (!fileList) return;
    
    fileList.innerHTML = '';
    
    if (files.length === 0) {
        showEmptyState(`未找到包含 "${query}" 的文件`);
        return;
    }
    
    files.forEach(file => {
        const row = createFileRow(file);
        fileList.appendChild(row);
    });
    
    updateFileStats(files);
}

// 添加移除按钮的辅助函数
function removeClearHistoryButton() {
    const existingBtn = document.querySelector('.clear-history-btn');
    if (existingBtn) {
        existingBtn.remove();
    }
}



// 切换视图
function switchView(view) {
    // 切换到视图
    
    // 更新当前视图
    currentView = view;
    
    // 先清除所有可能存在的按钮
    removeClearHistoryButton();
    
    // 移除所有导航项的活跃状态
    document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
    const currentLink = document.querySelector(`[data-view="${view}"]`);
    if (currentLink) currentLink.classList.add('active');
    
    switch (view) {
        case 'files': loadFileList(); break;
        case 'recent': loadRecentFiles(); break;
        case 'favorites': loadFavoriteFiles(); break;
        case 'shared': loadSharedFiles(); break;
    }
}

// 获取最近访问的文件
function getRecentFiles() {
    try {
        const recentFilesData = localStorage.getItem('recentFiles');
        if (recentFilesData) {
            return JSON.parse(recentFilesData);
        }
        return [];
    } catch (error) {
        console.error('获取最近文件失败:', error);
        return [];
    }
}

// 过滤存在的文件
function filterExistingFiles(recentFiles) {
    // 这里可以添加文件存在性检查逻辑
    // 暂时返回所有记录的文件
    return recentFiles;
}

// 记录文件访问
function recordFileAccess(path, name) {
    try {
        const recentFiles = getRecentFiles();
        
        // 移除已存在的相同路径文件
        const existingIndex = recentFiles.findIndex(file => file.path === path);
        if (existingIndex !== -1) {
            recentFiles.splice(existingIndex, 1);
        }
        
        // 添加新的访问记录到开头
        const newRecord = {
            path: path,
            name: name,
            lastAccessed: new Date().toISOString()
        };
        recentFiles.unshift(newRecord);
        
        // 限制最近文件数量为20个
        if (recentFiles.length > 20) {
            recentFiles.splice(20);
        }
        
        // 保存到localStorage
        localStorage.setItem('recentFiles', JSON.stringify(recentFiles));
        
        // 记录文件访问
    } catch (error) {
        console.error('记录文件访问失败:', error);
    }
}

// 清除最近访问历史
function clearRecentHistory() {
    try {
        localStorage.removeItem('recentFiles');
        showNotification('已清除最近访问历史', 'info');
        
        // 如果当前在最近文件视图，刷新显示
        if (currentView === 'recent') {
            loadRecentFiles();
        }
    } catch (error) {
        console.error('清除最近访问历史失败:', error);
        showNotification('清除失败', 'error');
    }
}

// 添加清除历史按钮
function addClearHistoryButton() {
    const clearButton = document.createElement('button');
    clearButton.className = 'action-btn clear-history-btn';
    clearButton.innerHTML = '<i class="fas fa-clock"></i> 清除历史';
    clearButton.title = '清除最近访问历史记录';
    clearButton.onclick = clearRecentHistory;
    
    const buttonContainer = document.querySelector('.file-list-container');
    if (buttonContainer) {
        // 移除已存在的清除按钮
        const existingClearBtn = buttonContainer.querySelector('.clear-history-btn');
        if (existingClearBtn) {
            existingClearBtn.remove();
        }
        
        // 添加新的清除按钮
        buttonContainer.insertBefore(clearButton, buttonContainer.firstChild);
    }
}

// 加载最近文件
async function loadRecentFiles() {
    try {
        showLoading();
        
        const recentFiles = getRecentFiles();
        const existingFiles = filterExistingFiles(recentFiles);
        
        if (existingFiles.length === 0) {
            displayFiles([], true);
            showNotification('暂无最近访问记录', 'info');
        } else {
            displayFiles(existingFiles, true);
            addClearHistoryButton();
            showNotification(`已加载 ${existingFiles.length} 个最近访问的文件`, 'info');
        }
    } catch (error) {
        console.error('加载最近文件错误:', error);
        showNotification('加载最近文件时发生错误', 'error');
    } finally {
        hideLoading();
    }
}

// 获取收藏文件列表
function getFavoriteFiles() {
    try {
        const favoriteFilesData = localStorage.getItem('favoriteFiles');
        if (favoriteFilesData) {
            return JSON.parse(favoriteFilesData);
        }
        return [];
    } catch (error) {
        console.error('获取收藏文件失败:', error);
        return [];
    }
}

// 检查文件是否为收藏
function isFileFavorite(path) {
    try {
        const favoriteFiles = getFavoriteFiles();
        return favoriteFiles.some(file => file.path === path);
    } catch (error) {
        console.error('检查收藏状态失败:', error);
        return false;
    }
}

// 切换收藏状态
function toggleFavorite(path, name, event) {
    event.stopPropagation();
    
    try {
        const favoriteFiles = getFavoriteFiles();
        const existingIndex = favoriteFiles.findIndex(file => file.path === path);
        
        if (existingIndex !== -1) {
            // 取消收藏
            favoriteFiles.splice(existingIndex, 1);
            showNotification(`已取消收藏: ${name}`, 'info');
        } else {
            // 添加收藏
            const newFavorite = {
                path: path,
                name: name,
                addedTime: new Date().toISOString()
            };
            favoriteFiles.unshift(newFavorite);
            showNotification(`已添加到收藏夹: ${name}`, 'success');
        }
        
        // 保存到localStorage
        localStorage.setItem('favoriteFiles', JSON.stringify(favoriteFiles));
        
        // 刷新当前视图
        if (currentView === 'favorites') {
            loadFavoriteFiles();
        } else {
            // 刷新文件列表以更新收藏按钮状态
            loadFileList();
        }
        
    } catch (error) {
        console.error('切换收藏状态失败:', error);
        showNotification('操作失败', 'error');
    }
}

// 加载收藏文件
async function loadFavoriteFiles() {
    try {
        showLoading();
        
        const favoriteFiles = getFavoriteFiles();
        
        if (favoriteFiles.length === 0) {
            // 显示空状态
            const fileList = document.getElementById('file-list');
            if (fileList) {
                fileList.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-star" style="font-size: 48px; color: #9ca3af; margin-bottom: 16px;"></i>
                        <h3 style="color: #6b7280; margin-bottom: 8px;">暂无收藏文件</h3>
                        <p style="color: #9ca3af; font-size: 14px;">点击文件旁的星形图标添加到收藏夹</p>
                    </div>
                `;
            }
            showNotification('暂无收藏文件', 'info');
        } else {
            // 显示收藏文件列表
            displayFiles(favoriteFiles, false, true);
            showNotification(`已加载 ${favoriteFiles.length} 个收藏文件`, 'success');
        }
        
        // 添加清除收藏按钮
        addClearFavoritesButton();
        
    } catch (error) {
        console.error('加载收藏文件错误:', error);
        showNotification('加载收藏文件失败', 'error');
    } finally {
        hideLoading();
    }
}

// 添加清除收藏按钮
function addClearFavoritesButton() {
    const fileList = document.getElementById('file-list');
    if (!fileList || document.getElementById('clear-favorites-btn')) return;
    
    const clearContainer = document.createElement('div');
    clearContainer.className = 'clear-favorites-container';
    clearContainer.style.cssText = `
        display: flex;
        justify-content: center;
        padding: 24px 20px;
        border-top: 1px solid #e5e7eb;
        margin-top: 20px;
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 0 0 12px 12px;
    `;
    
    const clearButton = document.createElement('button');
    clearButton.id = 'clear-favorites-btn';
    clearButton.className = 'action-btn secondary clear-favorites-btn';
    clearButton.innerHTML = `
        <i class="fas fa-star" style="color: #f59e0b;"></i>
        <span>清除所有收藏</span>
        <i class="fas fa-chevron-right" style="font-size: 12px; margin-left: 4px; opacity: 0.7;"></i>
    `;
    clearButton.title = '清除所有收藏的文件';
    
    // 添加点击事件
    clearButton.addEventListener('click', clearAllFavorites);
    
    // 添加提示信息
    const infoText = document.createElement('div');
    infoText.className = 'clear-favorites-info';
    infoText.textContent = '此操作将清除所有收藏的文件';
    
    clearContainer.appendChild(clearButton);
    clearContainer.appendChild(infoText);
    fileList.appendChild(clearContainer);
}

// 清除所有收藏
function clearAllFavorites() {
    try {
        if (confirm('确定要清除所有收藏文件吗？此操作不可恢复。')) {
            localStorage.removeItem('favoriteFiles');
            showNotification('所有收藏文件已清除', 'success');
            
            // 刷新收藏夹显示
            if (currentView === 'favorites') {
                loadFavoriteFiles();
            }
        }
    } catch (error) {
        console.error('清除收藏失败:', error);
        showNotification('清除失败', 'error');
    }
}

// 加载共享文件
async function loadSharedFiles() {
    try {
        showLoading();
        
        // 更新面包屑导航
        updateBreadcrumbForShared();
        
        // 加载共享目录内容
        const response = await fetch('/api/sharing/shared');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            // 显示共享文件列表
            displaySharedFiles(result);
            
            // 更新工具栏按钮状态
            updateToolbarForShared();
            
            showNotification('共享文件加载成功', 'success');
        } else {
            throw new Error(result.message || '加载共享文件失败');
        }
        
    } catch (error) {
        console.error('加载共享文件错误:', error);
        
        let errorMessage = '加载共享文件失败';
        if (error.message.includes('权限不足')) {
            errorMessage = '权限不足，无法访问共享目录';
        } else if (error.message.includes('HTTP')) {
            errorMessage = '服务器响应错误';
        }
        
        showNotification(errorMessage, 'error');
        
        // 显示错误状态
        const fileList = document.getElementById('file-list');
        if (fileList) {
            fileList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-exclamation-triangle" style="font-size: 48px; color: #f59e0b; margin-bottom: 16px;"></i>
                    <h3 style="color: #6b7280; margin-bottom: 8px;">无法访问共享目录</h3>
                    <p style="color: #9ca3af; font-size: 14px;">${errorMessage}</p>
                </div>
            `;
        }
    } finally {
        hideLoading();
    }
}

// 显示共享文件
function displaySharedFiles(result) {
    const fileList = document.getElementById('file-list');
    if (!fileList) return;
    
    // 获取共享文件数据，支持多种数据结构
    const sharedFiles = result.data || result.files || [];
    
    if (!sharedFiles || sharedFiles.length === 0) {
        fileList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-share-alt" style="font-size: 48px; color: #9ca3af; margin-bottom: 16px;"></i>
                <h3 style="color: #6b7280; margin-bottom: 8px;">共享目录为空</h3>
                <p style="color: #9ca3af; font-size: 14px;">暂无共享文件，您可以上传文件或创建文件夹</p>
            </div>
        `;
        return;
    }
    
    // 为共享文件添加所有者信息到文件名中，同时保留原始信息
    const enhancedSharedFiles = sharedFiles.map(file => ({
        ...file,
        originalName: file.name,  // 保存原始文件名
        originalOwner: file.owner,  // 保存原始所有者
        name: `${file.name} (由 ${file.owner} 共享)`
    }));
    
    // 显示文件列表
            displayFiles(enhancedSharedFiles, false, false, true);
    
    // 添加共享信息显示
    if (result.total !== undefined) {
        addSharedInfoDisplay({ total: result.total });
    }
}

// 更新面包屑导航为共享目录
function updateBreadcrumbForShared() {
    const breadcrumb = document.getElementById('breadcrumb');
    if (!breadcrumb) return;
    
    breadcrumb.innerHTML = `
        <li class="breadcrumb-item">
            <a href="#" data-path="/shared" class="breadcrumb-link">
                <i class="fas fa-share-alt"></i>
                                        <span>共享</span>
            </a>
        </li>
    `;
}

// 更新工具栏按钮状态
function updateToolbarForShared(userPermissions) {
    const smartUploadBtn = document.getElementById('smart-upload-btn');
    const newFolderBtn = document.getElementById('new-folder-btn');
    const webDownloadBtn = document.getElementById('web-download-btn');
    
    // 在共享视图中，这些操作应该指向用户个人目录
    if (smartUploadBtn) {
        smartUploadBtn.disabled = false;
        smartUploadBtn.title = '上传文件到个人目录';
    }
    
    if (newFolderBtn) {
        newFolderBtn.disabled = false;
        newFolderBtn.title = '在个人目录中创建文件夹';
    }
    
    if (webDownloadBtn) {
        webDownloadBtn.disabled = false;
        webDownloadBtn.title = '下载网络文件到个人目录';
    }
}

// 添加共享信息显示
function addSharedInfoDisplay(sharedInfo) {
    const fileList = document.getElementById('file-list');
    if (!fileList || !sharedInfo) return;
    
    const infoContainer = document.createElement('div');
    infoContainer.className = 'shared-info-container';
    infoContainer.style.cssText = `
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border: 1px solid #bae6fd;
        border-radius: 8px;
        padding: 16px;
        margin: 16px 0;
        text-align: center;
    `;
    
    infoContainer.innerHTML = `
        <div style="margin-bottom: 12px;">
            <i class="fas fa-share-alt" style="color: #0284c7; font-size: 20px;"></i>
        </div>
        <h4 style="color: #0369a1; margin: 0 0 8px 0; font-size: 16px;">共享文件系统</h4>
        <p style="color: #0c4a6e; margin: 0; font-size: 14px;">
            当前共有 <strong>${sharedInfo.total || 0}</strong> 个共享文件
        </p>
        <p style="color: #0c4a6e; margin: 8px 0 0 0; font-size: 12px;">
            基于硬链接的简化共享系统
        </p>
    `;
    
    fileList.insertBefore(infoContainer, fileList.firstChild);
}

// 获取访问级别显示文本
function getAccessLevelDisplay(accessLevel) {
    const levelMap = {
        'admin': '管理员',
        'editor': '编辑者',
        'contributor': '贡献者',
        'viewer': '查看者',
        'none': '无权限'
    };
    
    return levelMap[accessLevel] || '未知';
}

















// 添加键盘快捷键
function addKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'f') {
            e.preventDefault();
            document.getElementById('global-search')?.focus();
        }
    });
}

// 选择所有文件


// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 显示加载状态
function showLoading() {
    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) loadingIndicator.style.display = 'flex';
}

// 隐藏加载状态
function hideLoading() {
    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) loadingIndicator.style.display = 'none';
}

// 显示通知
function showNotification(message, type = 'info') {
    const container = document.getElementById('notification-container');
    if (!container) return;
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">&times;</button>
    `;
    
    container.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentElement) notification.remove();
    }, 5000);
}

// 显示空状态
function showEmptyState(message = '当前目录为空') {
    const emptyState = document.getElementById('empty-state');
    if (emptyState) {
        emptyState.style.display = 'block';
        const titleElement = emptyState.querySelector('h3');
        if (titleElement) {
            titleElement.textContent = message;
        }
        
        // 如果是加载失败，显示重试按钮
        if (message.includes('失败') || message.includes('错误')) {
            const actionsElement = emptyState.querySelector('.empty-actions');
            if (actionsElement) {
                actionsElement.innerHTML = `
                    <button class="action-btn primary" onclick="retryLoadFileList()">
                        <i class="fas fa-redo"></i>
                        <span>重试</span>
                    </button>
                    <button class="action-btn secondary" onclick="showAPIDiagnostics()">
                        <i class="fas fa-bug"></i>
                        <span>诊断</span>
                    </button>
                `;
            }
        }
    }
}

// 重试加载文件列表
function retryLoadFileList() {
    console.log('重试加载文件列表...');
    showNotification('正在重试...', 'info');
    loadFileList();
}

// 显示API诊断信息
function showAPIDiagnostics() {
    console.log('显示API诊断信息...');
    
    // 测试各个API端点
    Promise.all([
        fetch('/api/health').then(r => ({ endpoint: 'health', status: r.status, ok: r.ok })),
        fetch('/api/list?path=.').then(r => ({ endpoint: 'list', status: r.status, ok: r.ok })),
        fetch('/api/search?q=&path=.').then(r => ({ endpoint: 'search', status: r.status, ok: r.ok }))
    ]).then(results => {
        console.log('API诊断结果:', results);
        
        const failedAPIs = results.filter(r => !r.ok);
        if (failedAPIs.length > 0) {
            const failedList = failedAPIs.map(r => `${r.endpoint} (${r.status})`).join(', ');
            showNotification(`以下API端点异常: ${failedList}`, 'error');
        } else {
            showNotification('所有API端点正常', 'success');
        }
    }).catch(error => {
        console.error('API诊断失败:', error);
        showNotification('API诊断失败: ' + error.message, 'error');
    });
}

// 显示API响应详细信息（用于调试）
function showAPIResponseDetails(response) {
    console.log('=== API响应详细信息 ===');
    console.log('状态码:', response.status, response.statusText);
    console.log('响应头:', Object.fromEntries(response.headers.entries()));
    console.log('响应体:', response);
    console.log('========================');
}

// 隐藏空状态
function hideEmptyState() {
    const emptyState = document.getElementById('empty-state');
    if (emptyState) emptyState.style.display = 'none';
}

// 更新文件统计信息
function updateFileStats(files = null) {
    const fileCount = files ? files.length : document.querySelectorAll('.file-row').length;
    const folderCount = files ? files.filter(f => f.is_directory).length : document.querySelectorAll('.file-row.folder').length;
    
    const fileCountElement = document.getElementById('file-count');
    const folderCountElement = document.getElementById('folder-count');
    
    if (fileCountElement) fileCountElement.textContent = fileCount;
    if (folderCountElement) folderCountElement.textContent = folderCount;
}

// 更新详细的统计信息（从API响应中获取）
function updateDetailedStats(apiResult) {
    if (!apiResult) return;
    
    // 更新文件数量
    const fileCountElement = document.getElementById('file-count');
    if (fileCountElement && apiResult.file_count !== undefined) {
        fileCountElement.textContent = apiResult.file_count;
    }
    
    // 更新文件夹数量
    const folderCountElement = document.getElementById('folder-count');
    if (folderCountElement && apiResult.dir_count !== undefined) {
        folderCountElement.textContent = apiResult.dir_count;
    }
    
    // 更新总大小
    const totalSizeElement = document.getElementById('total-size');
    if (totalSizeElement && apiResult.formatted_size) {
        totalSizeElement.textContent = apiResult.formatted_size;
    }
    
    // 更新最后更新时间
    const lastUpdateElement = document.getElementById('last-update');
    if (lastUpdateElement) {
        lastUpdateElement.textContent = '刚刚';
    }
    
    console.log('已更新详细统计信息:', {
        fileCount: apiResult.file_count,
        dirCount: apiResult.dir_count,
        totalSize: apiResult.formatted_size
    });
}

// 标准化文件项目数据结构
function normalizeFileItems(items) {
    if (!Array.isArray(items)) return [];
    
    return items.map(item => {
        // 根据实际API返回的字段进行标准化
        const normalized = {
            name: item.name || item.filename || item.path?.split('/').pop() || '未知文件',
            path: item.path || item.full_path || item.relative_path || '',
            size: item.size || item.file_size || 0,
            is_directory: item.is_directory || item.type === 'directory' || item.is_dir || false,
            modified_time: item.modified_time || item.mtime || item.last_modified || new Date().toISOString()
        };
        
        // 如果路径为空，使用名称作为路径
        if (!normalized.path && normalized.name) {
            normalized.path = normalized.name;
        }
        
        return normalized;
    });
}

// 创建文件行
function createFileRow(file, isRecentFiles = false, isFavorites = false, isSharedFile = false) {
    const row = document.createElement('tr');
    row.className = `file-row ${file.is_directory ? 'folder' : 'file'}`;
    row.dataset.path = file.path;
    
    // 为共享文件保存原始信息
    if (isSharedFile && file.originalName && file.originalOwner) {
        row.dataset.originalName = file.originalName;
        row.dataset.originalOwner = file.originalOwner;
    }
    
    // 为文件夹添加点击事件类
    if (file.is_directory) {
        row.classList.add('clickable-folder');
    }
    
    // 检查是否为收藏文件
    const isFavorite = isFileFavorite(file.path);
    const favoriteIcon = isFavorite ? 'fas fa-star' : 'far fa-star';
    const favoriteTitle = isFavorite ? '取消收藏' : '添加到收藏夹';
    
    // 在收藏页面中，直接使用file.path；在共享文件页面中，也使用file.path；在其他页面中，使用currentPath构建路径
    const filePath = (isFavorites || isSharedFile) ? file.path : (currentPath && currentPath !== '.') ? currentPath + '/' + file.name : file.name;
    
    row.innerHTML = `
        <td class="name-col">
            <div class="file-info ${file.is_directory ? 'folder-info' : 'file-info'}">
                <button class="action-btn favorite-btn ${isFavorite ? 'favorited' : ''}" onclick="toggleFavorite('${filePath}', '${file.name}', event)" title="${favoriteTitle}">
                    <i class="${favoriteIcon}"></i>
                </button>
                <i class="fas fa-${file.is_directory ? 'folder' : getFileIcon(file.name)} ${file.is_directory ? 'folder-icon' : 'file-icon'}"></i>
                <span class="file-name ${file.is_directory ? 'folder-name' : 'file-name'}">${file.name}</span>
            </div>
        </td>
        <td class="size-col">
            <span class="file-size">${file.is_directory ? '-' : formatFileSize(file.size)}</span>
        </td>
        <td class="type-col">
            <span class="file-type">${file.is_directory ? '文件夹' : getFileType(file.name)}</span>
        </td>
        <td class="date-col">
            <span class="file-date">${isRecentFiles && file.lastAccessed ? formatDate(file.lastAccessed) : formatDate(file.modified_time)}</span>
        </td>
        <td class="actions-col">
            <div class="file-actions">
                ${file.is_directory ? 
                    `<button class="action-btn folder-action" onclick="openFolder('${filePath}')" title="打开文件夹">
                        <i class="fas fa-folder-open"></i>
                    </button>` :
                    `<button class="action-btn" onclick="downloadFile('${filePath}')" title="下载">
                        <i class="fas fa-download"></i>
                    </button>
                    ${!isSharedFile ? `<button class="action-btn" onclick="renameFile('${filePath}', '${file.name}')" title="重命名">
                        <i class="fas fa-edit"></i>
                    </button>` : ''}`
                }
                ${''}
                <button class="action-btn" onclick="showFileMenu('${filePath}', event)" title="更多操作">
                    <i class="fas fa-ellipsis-v"></i>
                </button>
            </div>
        </td>
    `;
    
    // 为文件夹添加整行点击事件
    if (file.is_directory) {
        row.addEventListener('click', (e) => {
            // 如果点击的是按钮或复选框，不触发文件夹打开
            if (e.target.closest('button') || e.target.closest('input')) {
                return;
            }
            // 使用构建的路径
            openFolder(filePath);
        });
        
        // 添加鼠标悬停效果
        row.style.cursor = 'pointer';
    }
    
    return row;
}

// 获取文件图标
function getFileIcon(filename) {
    const ext = filename.split('.').pop()?.toLowerCase();
    const iconMap = {
        // 文档类型
        'pdf': 'file-pdf', 'doc': 'file-word', 'docx': 'file-word',
        'xls': 'file-excel', 'xlsx': 'file-excel', 'ppt': 'file-powerpoint',
        'pptx': 'file-powerpoint', 'txt': 'file-alt', 'rtf': 'file-alt',
        'odt': 'file-alt', 'ods': 'file-excel', 'odp': 'file-powerpoint',
        
        // 压缩文件
        'zip': 'file-archive', 'rar': 'file-archive', '7z': 'file-archive',
        'tar': 'file-archive', 'gz': 'file-archive', 'bz2': 'file-archive',
        
        // 图片文件
        'jpg': 'file-image', 'jpeg': 'file-image', 'png': 'file-image',
        'gif': 'file-image', 'bmp': 'file-image', 'svg': 'file-image',
        'webp': 'file-image', 'ico': 'file-image', 'tiff': 'file-image',
        
        // 音频文件
        'mp3': 'file-audio', 'wav': 'file-audio', 'flac': 'file-audio',
        'aac': 'file-audio', 'ogg': 'file-audio', 'wma': 'file-audio',
        
        // 视频文件
        'mp4': 'file-video', 'avi': 'file-video', 'mkv': 'file-video',
        'mov': 'file-video', 'wmv': 'file-video', 'flv': 'file-video',
        'webm': 'file-video', 'm4v': 'file-video',
        
        // 代码文件
        'js': 'file-code', 'py': 'file-code', 'java': 'file-code',
        'cpp': 'file-code', 'c': 'file-code', 'html': 'file-code',
        'css': 'file-code', 'php': 'file-code', 'sql': 'file-code',
        'json': 'file-code', 'xml': 'file-code', 'yaml': 'file-code',
        'yml': 'file-code', 'md': 'file-code', 'sh': 'file-code',
        'bat': 'file-code', 'ps1': 'file-code',
        
        // 其他常见文件
        'log': 'file-alt', 'ini': 'file-alt', 'cfg': 'file-alt',
        'conf': 'file-alt', 'bak': 'file-alt', 'tmp': 'file-alt',
        'temp': 'file-alt', 'cache': 'file-alt'
    };
    return iconMap[ext] || 'file';
}

// 获取文件类型
function getFileType(filename) {
    const ext = filename.split('.').pop()?.toLowerCase();
    const typeMap = {
        // 文档类型
        'pdf': 'PDF文档', 'doc': 'Word文档', 'docx': 'Word文档',
        'xls': 'Excel表格', 'xlsx': 'Excel表格', 'ppt': 'PowerPoint演示',
        'pptx': 'PowerPoint演示', 'txt': '文本文件', 'rtf': '富文本文件',
        'odt': 'OpenDocument文本', 'ods': 'OpenDocument表格', 'odp': 'OpenDocument演示',
        
        // 压缩文件
        'zip': 'ZIP压缩包', 'rar': 'RAR压缩包', '7z': '7-Zip压缩包',
        'tar': 'TAR压缩包', 'gz': 'GZ压缩包', 'bz2': 'BZ2压缩包',
        
        // 图片文件
        'jpg': 'JPEG图片', 'jpeg': 'JPEG图片', 'png': 'PNG图片',
        'gif': 'GIF图片', 'bmp': 'BMP图片', 'svg': 'SVG矢量图',
        'webp': 'WebP图片', 'ico': '图标文件', 'tiff': 'TIFF图片',
        
        // 音频文件
        'mp3': 'MP3音频', 'wav': 'WAV音频', 'flac': 'FLAC音频',
        'aac': 'AAC音频', 'ogg': 'OGG音频', 'wma': 'WMA音频',
        
        // 视频文件
        'mp4': 'MP4视频', 'avi': 'AVI视频', 'mkv': 'MKV视频',
        'mov': 'MOV视频', 'wmv': 'WMV视频', 'flv': 'FLV视频',
        'webm': 'WebM视频', 'm4v': 'M4V视频',
        
        // 代码文件
        'js': 'JavaScript文件', 'py': 'Python文件', 'java': 'Java文件',
        'cpp': 'C++文件', 'c': 'C文件', 'html': 'HTML文件',
        'css': 'CSS样式表', 'php': 'PHP文件', 'sql': 'SQL文件',
        'json': 'JSON文件', 'xml': 'XML文件', 'yaml': 'YAML文件',
        'yml': 'YAML文件', 'md': 'Markdown文件', 'sh': 'Shell脚本',
        'bat': '批处理文件', 'ps1': 'PowerShell脚本',
        
        // 其他常见文件
        'log': '日志文件', 'ini': '配置文件', 'cfg': '配置文件',
        'conf': '配置文件', 'bak': '备份文件', 'tmp': '临时文件',
        'temp': '临时文件', 'cache': '缓存文件'
    };
    return typeMap[ext] || '未知类型';
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 格式化日期
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return '刚刚';
    if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前';
    if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前';
    if (diff < 2592000000) return Math.floor(diff / 86400000) + '天前';
    return date.toLocaleDateString('zh-CN');
}

// 路径验证和清理函数
function sanitizePath(path) {
    if (!path || typeof path !== 'string') {
        return '';
    }
    
    console.log('原始路径:', path);
    
    // 如果是Windows绝对路径（包含冒号），需要特殊处理
    if (path.includes(':')) {
        console.log('检测到Windows绝对路径，进行转换...');
        
        // 分割路径并过滤空字符串
        // 先统一为反斜杠，然后分割
        const normalizedPath = path.replace(/\\/g, '/');
        const pathParts = normalizedPath.split('/').filter(part => part.trim() !== '');
        console.log('路径分割结果:', pathParts);
        
        // 查找file_manager目录的索引
        const repoIndex = pathParts.findIndex(part => part === 'file_manager');
        console.log('file_manager索引:', repoIndex);
        
        if (repoIndex !== -1) {
            // 如果找到file_manager，使用其后的部分作为相对路径
            const relativeParts = pathParts.slice(repoIndex + 1);
            cleanPath = relativeParts.join('/');
            console.log('提取的相对路径:', cleanPath);
        } else {
            // 如果找不到file_manager，尝试其他策略
            // 1. 查找包含 'repo' 的目录
            const repoIndex2 = pathParts.findIndex(part => part.includes('repo'));
            if (repoIndex2 !== -1) {
                const relativeParts = pathParts.slice(repoIndex2 + 1);
                cleanPath = relativeParts.join('/');
                console.log('使用repo后的路径:', cleanPath);
            } else {
                // 2. 使用最后几级目录，但排除驱动器部分
                const driveIndex = pathParts.findIndex(part => part.includes(':'));
                const startIndex = driveIndex !== -1 ? driveIndex + 1 : 0;
                const relativeParts = pathParts.slice(startIndex);
                cleanPath = relativeParts.join('/');
                console.log('使用驱动器后的路径:', cleanPath);
            }
        }
        
        // 如果清理后的路径仍然包含冒号或其他危险字符，说明转换失败
        if (cleanPath.includes(':') || cleanPath.includes('\\') || cleanPath.includes('..')) {
            console.warn('路径转换失败，包含危险字符:', cleanPath);
            return '';
        }
        
        // 确保路径不为空且有意义
        if (!cleanPath || cleanPath.length === 0) {
            console.warn('路径转换后为空');
            return '';
        }
    } else {
        // 非绝对路径，进行常规清理
        cleanPath = path
            .replace(/[<>:"|?*]/g, '') // 移除Windows非法字符
            .replace(/\.\./g, '') // 移除路径遍历
            .replace(/\\/g, '/') // 统一斜杠
            .replace(/\/+/g, '/') // 移除重复斜杠
            .trim();
        
        // 移除开头和结尾的斜杠
        if (cleanPath.startsWith('/')) {
            cleanPath = cleanPath.substring(1);
        }
        if (cleanPath.endsWith('/')) {
            cleanPath = cleanPath.substring(0, cleanPath.length - 1);
        }
    }
    
    console.log('清理后的路径:', cleanPath);
    return cleanPath;
}

// 文件操作函数
function openFolder(path) {
    console.log('打开文件夹:', path);
    
    // 清理和标准化路径
    const cleanPath = sanitizePath(path);
    console.log('标准化后的路径:', cleanPath);
    
    if (!cleanPath) {
        console.warn('无效的路径:', path);
        showNotification('无法解析文件夹路径，请尝试直接点击文件夹名称', 'error');
        return;
    }
    
    // 额外的安全检查：确保路径不包含危险字符
    if (cleanPath.includes('..') || cleanPath.includes(':')) {
        console.warn('路径包含危险字符:', cleanPath);
        showNotification('路径包含无效字符，无法打开', 'error');
        return;
    }
    
    // 设置当前路径
    currentPath = cleanPath;
    console.log('设置当前路径为:', currentPath);
    
    // 验证路径格式
    if (currentPath.startsWith('/')) {
        currentPath = currentPath.substring(1);
        console.log('移除开头斜杠，当前路径:', currentPath);
    }
    
    // 记录文件夹访问
    const folderName = cleanPath.split('/').pop() || '根目录';
    recordFileAccess(cleanPath, folderName);
    
    // 加载文件列表
    loadFileList();
    updateBreadcrumb();
    
    // 显示文件夹信息
    showFolderInfo(cleanPath);
}

// 显示文件夹信息
function showFolderInfo(path) {
    const folderName = path.split('/').pop() || '根目录';
    showNotification(`已打开文件夹：${folderName}`, 'info');
    
    // 更新侧边栏状态
    updateSidebarState(path);
}

// 更新侧边栏状态
function updateSidebarState(path) {
    // 高亮当前路径对应的侧边栏项
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.dataset.view === 'files') {
            link.classList.add('active');
        }
    });
}

function downloadFile(path) {
    console.log('下载文件，路径:', path);
    console.log('当前路径:', currentPath);
    
    // 检查是否为共享文件（检查路径是否包含_shared）
    if (path.includes('_shared')) {
        // 解析共享文件路径
        const pathParts = path.split('/');
        const owner = pathParts[0].replace('_shared', '');
        const filename = pathParts[1];
        
        console.log('共享文件下载，所有者:', owner, '文件名:', filename);
        console.log('完整下载URL:', `/api/download/shared/${owner}/${filename}`);
        
        // 记录文件访问
        recordFileAccess(path, filename);
        
        window.open(`/api/download/shared/${owner}/${filename}`, '_blank');
    } else {
        console.log('完整下载URL:', `/api/download?path=${encodeURIComponent(path)}`);
        
        // 记录文件访问
        const fileName = path.split('/').pop();
        recordFileAccess(path, fileName);
        
        window.open(`/api/download?path=${encodeURIComponent(path)}`, '_blank');
    }
}

function editFile(path) {
    console.log('编辑文件，路径:', path);
    console.log('当前路径:', currentPath);
    console.log('完整编辑URL:', `/editor?path=${encodeURIComponent(path)}`);
    
    // 记录文件访问
    const fileName = path.split('/').pop();
    recordFileAccess(path, fileName);
    
    window.open(`/editor?path=${encodeURIComponent(path)}`, '_blank');
}

// 智能定位菜单函数
function positionMenuSmartly(menu, event) {
    // 先让菜单可见以获取实际尺寸
    menu.style.visibility = 'visible';
    
    const menuRect = menu.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    const menuWidth = menuRect.width;
    const menuHeight = menuRect.height;
    
    // 获取鼠标位置
    let x = event.clientX;
    let y = event.clientY;
    
    // 水平位置调整
    if (x + menuWidth > viewportWidth) {
        // 如果菜单会超出右边界，向左调整
        x = viewportWidth - menuWidth - 10; // 留10px边距
    }
    if (x < 10) {
        // 确保不会超出左边界
        x = 10;
    }
    
    // 垂直位置调整
    if (y + menuHeight > viewportHeight) {
        // 如果菜单会超出下边界，向上显示
        y = y - menuHeight - 5; // 在鼠标上方显示，留5px间距
    }
    if (y < 10) {
        // 确保不会超出上边界
        y = 10;
    }
    
    // 应用最终位置
    menu.style.left = `${x}px`;
    menu.style.top = `${y}px`;
    
    // 添加平滑动画效果
    menu.style.transition = 'opacity 0.2s ease-out';
    menu.style.opacity = '0';
    
    // 使用 requestAnimationFrame 确保位置设置后再显示
    requestAnimationFrame(() => {
        menu.style.opacity = '1';
    });
}

function showFileMenu(path, event) {
    event.preventDefault();
    console.log('显示文件菜单:', path);
    
    // 移除已存在的菜单
    const existingMenu = document.querySelector('.file-context-menu');
    if (existingMenu) {
        existingMenu.remove();
    }
    
    // 创建上下文菜单
    const menu = document.createElement('div');
    menu.className = 'file-context-menu';
    
    // 先设置基本样式，但不设置位置
    menu.style.cssText = `
        position: fixed;
        background: white;
        border: 1px solid #ddd;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 1000;
        min-width: 180px;
        padding: 8px 0;
        font-size: 14px;
        visibility: hidden;
    `;
    
    // 获取文件信息
    const fileRow = event.target.closest('.file-row');
    const isDirectory = fileRow?.classList.contains('folder');
    const fileName = fileRow?.querySelector('.file-name')?.textContent || '未知文件';
    
    // 检查是否为共享文件（通过检查文件名是否包含"由...共享"）
    const isSharedFile = fileName.includes(' (由 ') && fileName.includes(' 共享)');
    
    // 如果是共享文件，提取原始文件名和所有者
    let originalFileName = fileName;
    let fileOwner = null;
    if (isSharedFile) {
        // 优先从DOM数据属性获取原始信息
        if (fileRow?.dataset.originalName && fileRow?.dataset.originalOwner) {
            originalFileName = fileRow.dataset.originalName;
            fileOwner = fileRow.dataset.originalOwner;
        } else {
            // 备用方案：从文件名解析
            const match = fileName.match(/^(.+?) \(由 (.+?) 共享\)$/);
            if (match) {
                originalFileName = match[1];
                fileOwner = match[2];
            }
        }
    }
    
    // 菜单项配置
    const menuItems = [
        {
            icon: 'fa-eye',
            text: '预览',
            action: () => previewFile(path, originalFileName),
            show: !isDirectory
        },
        {
            icon: 'fa-edit',
            text: '编辑',
            action: () => editFile(path),
            show: !isDirectory && !isSharedFile  // 共享文件不允许编辑
        },
        {
            icon: 'fa-copy',
            text: '复制',
            action: () => copyFile(path, originalFileName),
            show: !isSharedFile  // 共享文件不允许复制
        },
        {
            icon: 'fa-cut',
            text: '剪切',
            action: () => cutFile(path, originalFileName),
            show: !isSharedFile  // 共享文件不允许剪切
        },
        {
            icon: 'fa-share-alt',
            text: '分享到共享',
            action: () => shareToShared(path, originalFileName, isDirectory),
            show: !isSharedFile  // 共享文件不能再分享
        },
        {
            icon: 'fa-trash',
            text: isSharedFile ? '删除共享文件' : '删除',
            action: async () => {
                if (isSharedFile) {
                    await deleteSharedFile(originalFileName, fileOwner);
                } else {
                    await deleteFile(path, originalFileName);
                }
            },
            show: true,
            danger: true
        }
    ];
    
    // 渲染菜单项
    menuItems.forEach(item => {
        if (item.show) {
            const menuItem = document.createElement('div');
            menuItem.className = 'menu-item';
            menuItem.style.cssText = `
                padding: 10px 16px;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 12px;
                transition: background-color 0.2s;
                ${item.danger ? 'color: #dc3545;' : 'color: #333;'}
            `;
            
            menuItem.innerHTML = `
                <i class="fas ${item.icon}" style="width: 16px; text-align: center;"></i>
                <span>${item.text}</span>
            `;
            
            // 悬停效果
            menuItem.addEventListener('mouseenter', () => {
                menuItem.style.backgroundColor = item.danger ? '#fef2f2' : '#f8f9fa';
            });
            
            menuItem.addEventListener('mouseleave', () => {
                menuItem.style.backgroundColor = 'transparent';
            });
            
            // 点击事件
            menuItem.addEventListener('click', () => {
                item.action();
                menu.remove();
            });
            
            menu.appendChild(menuItem);
        }
    });
    
    // 添加到页面
    document.body.appendChild(menu);
    
    // 智能定位菜单，确保完全可见
    positionMenuSmartly(menu, event);
    
    // 点击其他地方关闭菜单
    const closeMenu = (e) => {
        if (!menu.contains(e.target)) {
            menu.remove();
            document.removeEventListener('click', closeMenu);
        }
    };
    
    // 延迟添加事件监听器，避免立即触发
    setTimeout(() => {
        document.addEventListener('click', closeMenu);
    }, 100);
}

// 加载文件列表
async function loadFileList() {
    try {
        showLoading();
        hideEmptyState();
        
        console.log('正在加载文件列表，路径:', currentPath);
        
        // 确保路径格式正确
        let apiPath = currentPath;
        if (apiPath === '' || apiPath === undefined) {
            apiPath = '.';
        }
        
        console.log('API请求路径:', apiPath);
        // 添加多个参数防止缓存
        const timestamp = new Date().getTime();
        const random = Math.random().toString(36).substring(7);
        const apiUrl = `/api/list?path=${encodeURIComponent(apiPath)}&t=${timestamp}&r=${random}&_=${Date.now()}`;
        console.log('API请求URL:', apiUrl);
        
        // 使用强制刷新选项
        const response = await fetch(apiUrl, {
            method: 'GET',
            cache: 'no-cache',
            headers: {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
        });
        console.log('API响应状态:', response.status, response.statusText);
        
        if (response.status === 401) {
            showNotification('未登录或登录已过期，请先登录', 'warning');
            window.location.href = '/login';
            return;
        }
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        console.log('API返回结果:', result);
        
        // 检查API返回的数据结构
        if (result && result.items && Array.isArray(result.items)) {
            // API返回的是 items 数组，不是 files
            console.log('成功获取文件列表，项目数量:', result.items.length);
            console.log('第一个项目示例:', result.items[0]);
            
            // 检查数据结构并标准化
            const normalizedItems = normalizeFileItems(result.items);
            console.log('标准化后的项目:', normalizedItems);
            
            displayFiles(normalizedItems);
            updateFileStats(normalizedItems);
            
            // 更新文件统计信息
            updateDetailedStats(result);
        } else if (result && result.files && Array.isArray(result.files)) {
            // 兼容旧的API格式
            console.log('使用兼容格式，文件数量:', result.files.length);
            displayFiles(result.files);
            updateFileStats(result.files);
        } else {
            console.warn('API返回的文件列表格式不正确:', result);
            showNotification('文件列表格式错误', 'error');
            showEmptyState('数据格式错误');
        }
    } catch (error) {
        console.error('加载文件列表错误:', error);
        
        // 如果是网络错误或API不可用，显示友好的错误信息
        let errorMessage = '加载文件列表时发生错误';
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            errorMessage = '网络连接失败，请检查网络设置';
        } else if (error.message.includes('HTTP')) {
            errorMessage = '服务器响应错误: ' + error.message;
        }
        
        showNotification(errorMessage, 'error');
        showEmptyState('加载失败');
    } finally {
        hideLoading();
    }
}

// 显示文件列表
function displayFiles(files, isRecentFiles = false, isFavorites = false, isSharedFile = false) {
    const fileList = document.getElementById('file-list');
    if (!fileList) return;
    
    fileList.innerHTML = '';
    
    if (files.length === 0) {
        if (isFavorites) {
            // 显示收藏夹空状态
            fileList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-star" style="font-size: 48px; color: #9ca3af; margin-bottom: 16px;"></i>
                    <h3 style="color: #6b7280; margin-bottom: 8px;">暂无收藏文件</h3>
                    <p style="color: #9ca3af; font-size: 14px;">点击文件旁的星形图标添加到收藏夹</p>
                </div>
            `;
        } else if (isRecentFiles) {
            // 显示最近文件空状态
            fileList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-clock" style="font-size: 48px; color: #9ca3af; margin-bottom: 16px;"></i>
                    <h3 style="color: #6b7280; margin-bottom: 8px;">暂无最近访问记录</h3>
                    <p style="color: #9ca3af; font-size: 14px;">访问文件或文件夹后，将自动记录在这里</p>
                </div>
            `;
        } else {
        showEmptyState();
        }
        return;
    }
    
    // 分类文件和文件夹
    const folders = files.filter(f => f.is_directory);
    const regularFiles = files.filter(f => !f.is_directory);
    
    // 先显示文件夹，再显示文件
    [...folders, ...regularFiles].forEach(file => {
        const row = createFileRow(file, isRecentFiles, isFavorites, isSharedFile);
        fileList.appendChild(row);
    });
    
    // 显示文件夹统计信息
    if (folders.length > 0 || regularFiles.length > 0) {
        showFolderStats(folders.length, regularFiles.length);
    }
}

// 显示文件夹统计信息
function showFolderStats(folderCount, fileCount) {
    const statsElement = document.getElementById('folder-stats');
    if (statsElement) {
        let statsText = '';
        if (folderCount > 0 && fileCount > 0) {
            statsText = `包含 ${folderCount} 个文件夹和 ${fileCount} 个文件`;
        } else if (folderCount > 0) {
            statsText = `包含 ${folderCount} 个文件夹`;
        } else if (fileCount > 0) {
            statsText = `包含 ${fileCount} 个文件`;
        }
        
        if (statsText) {
            statsElement.textContent = statsText;
            statsElement.style.display = 'block';
        }
    }
}

// 更新面包屑导航
function updateBreadcrumb() {
    const breadcrumb = document.getElementById('breadcrumb');
    if (!breadcrumb) return;
    
    const paths = currentPath.split('/').filter(Boolean);
    let breadcrumbHTML = '<li class="breadcrumb-item"><a href="#" data-path="." class="breadcrumb-link"><i class="fas fa-home"></i><span>根目录</span></a></li>';
    
    let currentPathStr = '';
    paths.forEach((path, index) => {
        currentPathStr += '/' + path;
        // 使用路径清理函数
        const cleanPath = sanitizePath(currentPathStr);
        // 确保面包屑路径格式正确
        const breadcrumbPath = cleanPath.startsWith('/') ? cleanPath.substring(1) : cleanPath;
        breadcrumbHTML += `
            <li class="breadcrumb-item">
                <a href="#" data-path="${breadcrumbPath}" class="breadcrumb-link">
                    <span>${path}</span>
                </a>
            </li>
        `;
    });
    
    breadcrumb.innerHTML = breadcrumbHTML;
    
    // 添加面包屑点击事件
    breadcrumb.querySelectorAll('.breadcrumb-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const path = link.dataset.path;
            console.log('面包屑点击，路径:', path);
            
            // 处理根目录特殊情况
            if (path === '.') {
                currentPath = '.';
                console.log('点击根目录，设置路径为根目录');
            } else {
                // 使用路径清理函数
                const cleanPath = sanitizePath(path);
                if (!cleanPath) {
                    console.warn('面包屑路径无效:', path);
                    showNotification('无效的导航路径', 'error');
                    return;
                }
                currentPath = cleanPath;
                console.log('面包屑导航到路径:', currentPath);
            }
            
            console.log('设置当前路径:', currentPath);
            loadFileList();
            updateBreadcrumb();
        });
    });
    
    // 更新当前路径显示
    updateCurrentPathDisplay();
}

// 更新当前路径显示
function updateCurrentPathDisplay() {
    const currentPathElement = document.getElementById('current-path');
    if (currentPathElement) {
        if (currentPath === '.' || currentPath === '') {
            currentPathElement.textContent = '当前位置：根目录';
        } else {
            currentPathElement.textContent = `当前位置：${currentPath}`;
        }
    }
    
    // 更新页面标题
    const pageTitle = (currentPath === '.' || currentPath === '') ? '文件管理系统' : `${currentPath} - 文件管理系统`;
    document.title = pageTitle;
}

// 初始化模态框事件
function initializeModalEvents() {
    const createFolderBtn = document.getElementById('create-folder-btn');
    const cancelFolderBtn = document.getElementById('cancel-folder-btn');
    
    if (createFolderBtn) createFolderBtn.addEventListener('click', createFolder);
    if (cancelFolderBtn) cancelFolderBtn.addEventListener('click', hideNewFolderModal);
}

// 显示新建文件夹模态框
function showNewFolderModal() {
    const modal = document.getElementById('new-folder-modal');
    const overlay = document.getElementById('overlay');
    
    if (modal && overlay) {
        modal.style.display = 'block';
        overlay.style.display = 'block';
        document.getElementById('new-folder-name')?.focus();
    }
}

// 隐藏新建文件夹模态框
function hideNewFolderModal() {
    const modal = document.getElementById('new-folder-modal');
    const overlay = document.getElementById('overlay');
    
    if (modal && overlay) {
        modal.style.display = 'none';
        overlay.style.display = 'none';
        document.getElementById('new-folder-name').value = '';
    }
}

// 创建文件夹
async function createFolder() {
    const input = document.getElementById('new-folder-name');
    if (!input) return;
    
    const folderName = input.value.trim();
    if (!folderName) {
        showNotification('请输入文件夹名称', 'error');
        return;
    }
    
    try {
        showLoading();
        
        // 调试信息：检查发送的数据
        const requestData = {
            name: folderName,
            path: currentPath
        };
        console.log('创建文件夹请求数据:', requestData);
        console.log('currentPath类型:', typeof currentPath);
        console.log('currentPath值:', currentPath);
        
        // 根据当前视图选择正确的API
        const apiEndpoint = '/api/create_folder';
        
        const response = await fetch(apiEndpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('文件夹创建成功', 'success');
            hideNewFolderModal();
            loadFileList();
        } else {
            showNotification('创建失败: ' + result.message, 'error');
        }
    } catch (error) {
        console.error('创建文件夹错误:', error);
        showNotification('创建文件夹时发生错误', 'error');
    } finally {
        hideLoading();
    }
}

// 文件上传处理
// 智能上传函数 - 根据文件大小自动选择上传方式
async function smartUploadFiles(event) {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;
    
    // 定义大文件阈值 (50MB)
    const LARGE_FILE_THRESHOLD = 50 * 1024 * 1024; // 50MB
    
    // 检查是否有大文件
    const largeFiles = files.filter(file => file.size > LARGE_FILE_THRESHOLD);
    const smallFiles = files.filter(file => file.size <= LARGE_FILE_THRESHOLD);
    
    console.log('智能上传分析:', {
        totalFiles: files.length,
        largeFiles: largeFiles.length,
        smallFiles: smallFiles.length,
        largeFileThreshold: LARGE_FILE_THRESHOLD
    });
    
    // 如果只有小文件，使用普通上传
    if (largeFiles.length === 0) {
        console.log('使用普通上传方式');
        await uploadFilesNormal(files);
        return;
    }
    
    // 如果只有大文件，使用分块上传
    if (smallFiles.length === 0) {
        console.log('使用分块上传方式');
        await uploadFilesChunked(files);
        return;
    }
    
    // 如果混合文件，分别处理
    console.log('使用混合上传方式');
    
    // 先上传小文件
    if (smallFiles.length > 0) {
        showNotification(`正在上传文件...`, 'info');
        await uploadFilesNormal(smallFiles);
    }
    
    // 再上传大文件
    if (largeFiles.length > 0) {
        showNotification(`正在上传文件...`, 'info');
        await uploadFilesChunked(largeFiles);
    }
}

// 普通上传函数
async function uploadFilesNormal(files) {
    try {
        showLoading();
        
        const formData = new FormData();
        files.forEach(file => formData.append('files', file));
        const targetDir = (currentPath && currentPath !== '') ? currentPath : '.';
        formData.append('target_directory', targetDir);
        
        console.log('普通上传文件信息:', {
            fileCount: files.length,
            targetDirectory: targetDir,
            files: files.map(f => ({ name: f.name, size: f.size, type: f.type }))
        });
        
        const response = await fetch('/api/upload_multiple', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            const uploadedCount = result.uploaded_count || result.success_count || result.uploaded_files?.length || 0;
            const failedCount = result.failed_count || result.failed_files?.length || 0;
            
            let successMessage = `上传成功`;
            if (uploadedCount > 1) {
                successMessage = `成功上传 ${uploadedCount} 个文件`;
            }
            if (failedCount > 0) {
                successMessage += `，${failedCount} 个文件失败`;
            }
            
            showNotification(successMessage, 'success');
            console.log('普通上传成功，准备刷新文件列表，当前路径:', currentPath);
            
            // 延迟一点时间确保服务器端文件已写入
            setTimeout(() => {
                console.log('延迟刷新文件列表，当前路径:', currentPath);
                loadFileList();
            }, 500);
        } else {
            throw new Error(result.message || '上传失败');
        }
        
    } catch (error) {
        console.error('普通上传失败:', error);
        showNotification(`上传失败: ${error.message}`, 'error');
    } finally {
        hideLoading();
        // 清空文件输入
        const fileInput = document.getElementById('file-upload');
        if (fileInput) fileInput.value = '';
    }
}

// 分块上传函数
async function uploadFilesChunked(files) {
    try {
        // 显示分块上传模态框
        const modal = document.getElementById('chunked-upload-modal');
        modal.style.display = 'flex';
        
        // 初始化分块上传UI
        if (!window.chunkedUploadUI) {
            window.chunkedUploadUI = new ChunkedUploadUI('chunked-upload-container', {
                maxFileSize: 1024 * 1024 * 1024, // 1GB
                showProgress: true,
                showDetails: true,
                autoStart: true,
                targetDirectory: (currentPath && currentPath !== '') ? currentPath : '.'
            });
        }
        
        // 设置文件到分块上传器
        window.chunkedUploadUI.setFiles(files);
        
    } catch (error) {
        console.error('分块上传失败:', error);
        showNotification(`上传失败: ${error.message}`, 'error');
    }
}

async function uploadFiles(event) {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;
    
    try {
        showLoading();
        showNotification(`正在上传 ${files.length} 个文件...`, 'info');
        
        const formData = new FormData();
        files.forEach(file => formData.append('files', file));
        // 确保目标目录不为空，空字符串时使用当前工作目录
        const targetDir = (currentPath && currentPath !== '') ? currentPath : '.';
        formData.append('target_directory', targetDir);
        
        console.log('上传文件信息:', {
            fileCount: files.length,
            targetDirectory: targetDir,
            currentPath: currentPath,
            files: files.map(f => ({ name: f.name, size: f.size, type: f.type }))
        });
        
        // 根据当前视图选择正确的API
        const apiEndpoint = '/api/upload_multiple';
        
        const response = await fetch(apiEndpoint, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        console.log('上传API返回结果:', result);
        
        if (result.success) {
            // 使用正确的字段名，兼容不同的后端响应格式
            const uploadedCount = result.uploaded_count || result.success_count || result.uploaded_files?.length || 0;
            const failedCount = result.failed_count || result.failed_files?.length || 0;
            
            let successMessage = `成功上传 ${uploadedCount} 个文件`;
            if (failedCount > 0) {
                successMessage += `，${failedCount} 个文件上传失败`;
            }
            
            showNotification(successMessage, 'success');
            loadFileList();
        } else {
            throw new Error(result.message || '上传失败');
        }
    } catch (error) {
        console.error('文件上传错误:', error);
        
        let errorMessage = '文件上传时发生错误';
        if (error.message.includes('HTTP')) {
            errorMessage = '服务器响应错误: ' + error.message;
        } else if (error.message.includes('fetch')) {
            errorMessage = '网络连接失败，请检查网络设置';
        } else if (error.message.includes('系统找不到指定的路径')) {
            errorMessage = '目标目录路径无效，请检查当前路径设置';
        } else if (error.message.includes('WinError 3')) {
            errorMessage = '目标目录不存在或无法访问，请检查路径权限';
        } else {
            errorMessage = error.message;
        }
        
        showNotification(errorMessage, 'error');
    } finally {
        hideLoading();
        event.target.value = '';
    }
}

// 初始化网络下载功能
function initializeWebDownload() {
    const webDownloadBtn = document.getElementById('web-download-btn');
    const webDownloadModal = document.getElementById('web-download-modal');
    const overlay = document.getElementById('overlay');
    
    if (webDownloadBtn && webDownloadModal) {
        webDownloadBtn.addEventListener('click', () => {
            webDownloadModal.style.display = 'block';
            if (overlay) overlay.style.display = 'block';
        });
    }
    
    // 绑定开始/取消下载事件
    const startBtn = document.getElementById('start-download-btn');
    const cancelBtn = document.getElementById('cancel-download-btn');
    if (startBtn) {
        startBtn.addEventListener('click', async () => {
            const urlInput = document.getElementById('web-download-url');
            const nameInput = document.getElementById('web-download-filename');
            const url = urlInput ? urlInput.value.trim() : '';
            const filename = nameInput ? nameInput.value.trim() : '';
            
            if (!url || !(url.startsWith('http://') || url.startsWith('https://'))) {
                showNotification('请输入有效的下载链接（http/https）', 'error');
                if (urlInput) urlInput.focus();
                return;
            }
            
            // 显示进度条（后端为同步下载，这里展示提交与完成两阶段）
            const progress = document.getElementById('download-progress');
            const progressFill = document.getElementById('progress-fill');
            const progressPercent = document.getElementById('progress-percentage');
            const progressText = document.getElementById('progress-text');
            if (progress) progress.style.display = 'block';
            if (progressFill) progressFill.style.width = '15%';
            if (progressPercent) progressPercent.textContent = '15%';
            if (progressText) progressText.textContent = '正在提交下载请求...';
            
            try {
                const response = await fetch('/api/download_web_file', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url, filename })
                });
                
                if (!response.ok) {
                    const err = await response.json().catch(() => ({}));
                    throw new Error(err.message || `HTTP ${response.status}`);
                }
                
                // 伪装进度直至完成
                if (progressFill) progressFill.style.width = '70%';
                if (progressPercent) progressPercent.textContent = '70%';
                if (progressText) progressText.textContent = '正在下载文件到服务器...';
                
                const result = await response.json();
                if (result && result.success) {
                    if (progressFill) progressFill.style.width = '100%';
                    if (progressPercent) progressPercent.textContent = '100%';
                    if (progressText) progressText.textContent = '下载完成';
                    showNotification(`下载成功: ${result.filename || '文件'}`, 'success');
                    // 清空输入并关闭模态框
                    if (urlInput) urlInput.value = '';
                    if (nameInput) nameInput.value = '';
                    setTimeout(() => hideWebDownloadModal(), 600);
                } else {
                    throw new Error((result && result.message) || '下载失败');
                }
            } catch (error) {
                console.error('网络下载失败:', error);
                if (progressFill) progressFill.style.width = '0%';
                if (progressPercent) progressPercent.textContent = '0%';
                if (progressText) progressText.textContent = '下载失败';
                showNotification(`网络下载失败: ${error.message}`, 'error');
            }
        });
    }
    if (cancelBtn) {
        cancelBtn.addEventListener('click', () => hideWebDownloadModal());
    }
    
    // 关闭按钮事件
    const closeBtns = document.querySelectorAll('.modal-close');
    closeBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const modal = e.target.closest('.modal');
            if (modal) {
                modal.style.display = 'none';
                if (overlay) overlay.style.display = 'none';
            }
        });
    });
    
    // 点击遮罩层关闭模态框
    if (overlay) {
        overlay.addEventListener('click', () => {
            const modals = document.querySelectorAll('.modal');
            modals.forEach(modal => {
                modal.style.display = 'none';
            });
            overlay.style.display = 'none';
        });
    }
}

// 系统设置功能已移除

// 通知中心功能已移除

// 初始化存储信息
function initializeStorageInfo() {
    // 模拟存储信息更新
    setTimeout(() => {
        const storageUsed = document.getElementById('storage-used');
        const storageTotal = document.getElementById('storage-total');
        const storageProgress = document.getElementById('storage-progress');
        
        if (storageUsed) storageUsed.textContent = '15.2 GB';
        if (storageTotal) storageTotal.textContent = '100 GB';
        if (storageProgress) storageProgress.style.width = '15.2%';
    }, 2000);
}

// 检查剪贴板支持情况
function checkClipboardSupport() {
    const support = {
        modern: false,
        fallback: false,
        share: false
    };
    
    // 检查现代剪贴板API
    if (navigator.clipboard && navigator.clipboard.writeText) {
        support.modern = true;
        console.log('✅ 支持现代剪贴板API');
    } else {
        console.log('❌ 不支持现代剪贴板API');
    }
    
    // 检查execCommand支持
    if (document.queryCommandSupported && document.queryCommandSupported('copy')) {
        support.fallback = true;
        console.log('✅ 支持execCommand复制');
    } else {
        console.log('❌ 不支持execCommand复制');
    }
    
    // 检查Web Share API
    if (navigator.share && navigator.canShare) {
        support.share = true;
        console.log('✅ 支持Web Share API');
    } else {
        console.log('❌ 不支持Web Share API');
    }
    
    // 如果没有剪贴板支持，显示提示
    if (!support.modern && !support.fallback) {
        console.warn('⚠️ 当前环境不支持任何剪贴板操作');
        showNotification('当前环境不支持剪贴板操作，复制功能将受限', 'warning');
    }
    
    return support;
}

// 系统设置功能已移除

// 隐藏网络下载模态框
function hideWebDownloadModal() {
    const webDownloadModal = document.getElementById('web-download-modal');
    const overlay = document.getElementById('overlay');
    
    if (webDownloadModal) webDownloadModal.style.display = 'none';
    if (overlay) overlay.style.display = 'none';
}

// 获取预览URL（处理共享文件）
function getPreviewUrl(path) {
    // 检查是否为共享文件（检查路径是否包含_shared）
    if (path.includes('_shared')) {
        // 解析共享文件路径
        const pathParts = path.split('/');
        const owner = pathParts[0].replace('_shared', '');
        const filename = pathParts[1];
        
        return `/api/download/shared/${owner}/${filename}`;
    } else {
        return `/api/download?path=${encodeURIComponent(path)}`;
    }
}

// 文件操作功能函数
function previewFile(path, fileName) {
    console.log('预览文件:', path, fileName);
    
    // 记录文件访问
    recordFileAccess(path, fileName);
    
    // 获取文件扩展名
    const fileExt = fileName.toLowerCase().split('.').pop();
    
    // 根据文件类型选择预览方式
    if (['txt', 'md', 'py', 'js', 'html', 'css', 'json', 'xml', 'sql', 'sh', 'bat', 'log'].includes(fileExt)) {
        // 文本文件预览
        previewTextFile(path, fileName);
    } else if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp'].includes(fileExt)) {
        // 图片文件预览
        previewImageFile(path, fileName);
    } else if (['pdf'].includes(fileExt)) {
        // PDF文件预览
        previewPdfFile(path, fileName);
    } else if (['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv'].includes(fileExt)) {
        // 视频文件预览
        previewVideoFile(path, fileName);
    } else if (['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a', 'wma'].includes(fileExt)) {
        // 音频文件预览
        previewAudioFile(path, fileName);
    } else {
        // 不支持的文件类型
        showNotification(`不支持预览此文件类型: ${fileName}`, 'warning');
    }
}

// 预览文本文件
function previewTextFile(path, fileName) {
    // 创建预览模态框
    const modal = document.createElement('div');
    modal.className = 'preview-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
    `;
    
    modal.innerHTML = `
        <div class="preview-content" style="
            background: white;
            border-radius: 12px;
            max-width: 90%;
            max-height: 90%;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        ">
            <div class="preview-header" style="
                padding: 20px 24px 16px;
                border-bottom: 1px solid #e5e7eb;
                display: flex;
                align-items: center;
                justify-content: space-between;
            ">
                <h3 style="margin: 0; font-size: 18px; color: #111827;">
                    <i class="fas fa-file-alt" style="margin-right: 8px; color: #6b7280;"></i>
                    ${fileName}
                </h3>
                <button class="close-preview-btn" style="
                    background: none;
                    border: none;
                    font-size: 20px;
                    cursor: pointer;
                    color: #6b7280;
                    padding: 4px;
                    border-radius: 4px;
                    transition: all 0.2s;
                ">&times;</button>
            </div>
            <div class="preview-body" style="
                padding: 24px;
                overflow-y: auto;
                flex: 1;
                font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                font-size: 14px;
                line-height: 1.6;
                color: #374151;
                background: #f9fafb;
                border-radius: 0 0 12px 12px;
            ">
                <div class="loading" style="text-align: center; color: #6b7280;">
                    <i class="fas fa-spinner fa-spin" style="font-size: 24px; margin-bottom: 16px;"></i>
                    <div>正在加载文件内容...</div>
                </div>
            </div>
        </div>
    `;
    
    // 添加到页面
    document.body.appendChild(modal);
    
    // 关闭按钮事件
    const closeBtn = modal.querySelector('.close-preview-btn');
    closeBtn.addEventListener('click', () => {
        document.body.removeChild(modal);
    });
    
    // 点击背景关闭
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    });
    
    // 加载文件内容
    loadFileContent(path, modal);
}

// 加载文件内容
function loadFileContent(path, modal) {
    const previewBody = modal.querySelector('.preview-body');
    
    // 使用fetch API获取文件内容
    fetch(`/api/editor/preview?path=${encodeURIComponent(path)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // 显示文件内容
                const truncatedMessage = data.truncated ? 
                    `<div style="margin-top: 16px; padding: 12px; background: #fef3c7; border-radius: 6px; color: #92400e; font-size: 13px;"><i class="fas fa-info-circle" style="margin-right: 6px;"></i>文件内容过长，仅显示前 ${data.line_count} 行</div>` : '';
                
                previewBody.innerHTML = `
                    <pre style="margin: 0; white-space: pre-wrap; word-wrap: break-word;">${escapeHtml(data.content)}</pre>
                    ${truncatedMessage}
                `;
            } else {
                previewBody.innerHTML = `
                    <div style="text-align: center; color: #dc2626; padding: 20px;">
                        <i class="fas fa-exclamation-triangle" style="font-size: 24px; margin-bottom: 16px;"></i>
                        <div>加载失败: ${data.message}</div>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('加载文件内容失败:', error);
            previewBody.innerHTML = `
                <div style="text-align: center; color: #dc2626; padding: 20px;">
                    <i class="fas fa-exclamation-triangle" style="font-size: 24px; margin-bottom: 16px;"></i>
                    <div>加载失败: ${error.message}</div>
                    <div style="margin-top: 8px; font-size: 13px; color: #6b7280;">
                        请检查文件是否存在或是否有访问权限
                    </div>
                </div>
            `;
        });
}

// 预览图片文件
function previewImageFile(path, fileName) {
    const modal = document.createElement('div');
    modal.className = 'preview-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.9);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
    `;
    
    modal.innerHTML = `
        <div class="preview-content" style="
            max-width: 95%;
            max-height: 95%;
            position: relative;
        ">
            <div class="preview-header" style="
                position: absolute;
                top: -50px;
                left: 0;
                right: 0;
                text-align: center;
                color: white;
                z-index: 10001;
            ">
                <h3 style="margin: 0; font-size: 16px; text-shadow: 0 2px 4px rgba(0,0,0,0.5);">
                    ${fileName}
                </h3>
            </div>
            <img src="${getPreviewUrl(path)}" 
                 alt="${fileName}" 
                 style="
                    max-width: 100%;
                    max-height: 100%;
                    object-fit: contain;
                    border-radius: 8px;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
                 "
                 onload="this.style.opacity='1'"
                 onerror="this.style.display='none'; this.nextElementSibling.style.display='block'"
            >
            <div class="error-message" style="
                display: none;
                text-align: center;
                color: white;
                padding: 40px;
                font-size: 16px;
            ">
                <i class="fas fa-exclamation-triangle" style="font-size: 32px; margin-bottom: 16px;"></i>
                <div>图片加载失败</div>
            </div>
            <button class="close-preview-btn" style="
                position: absolute;
                top: -50px;
                right: 0;
                background: none;
                border: none;
                font-size: 24px;
                cursor: pointer;
                color: white;
                padding: 8px;
                border-radius: 4px;
                transition: all 0.2s;
                text-shadow: 0 2px 4px rgba(0,0,0,0.5);
            ">&times;</button>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    const closeBtn = modal.querySelector('.close-preview-btn');
    closeBtn.addEventListener('click', () => {
        document.body.removeChild(modal);
    });
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    });
}

// 预览PDF文件
function previewPdfFile(path, fileName) {
    const modal = document.createElement('div');
    modal.className = 'preview-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
    `;
    
    modal.innerHTML = `
        <div class="preview-content" style="
            background: white;
            border-radius: 12px;
            max-width: 95%;
            max-height: 95%;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        ">
            <div class="preview-header" style="
                padding: 20px 24px 16px;
                border-bottom: 1px solid #e5e7eb;
                display: flex;
                align-items: center;
                justify-content: space-between;
            ">
                <h3 style="margin: 0; font-size: 18px; color: #111827;">
                    <i class="fas fa-file-pdf" style="margin-right: 8px; color: #dc2626;"></i>
                    ${fileName}
                </h3>
                <button class="close-preview-btn" style="
                    background: none;
                    border: none;
                    font-size: 20px;
                    cursor: pointer;
                    color: #6b7280;
                    padding: 4px;
                    border-radius: 4px;
                    transition: all 0.2s;
                ">&times;</button>
            </div>
            <div class="preview-body" style="
                flex: 1;
                overflow: hidden;
                position: relative;
            ">
                <iframe src="${getPreviewUrl(path)}" 
                        style="
                            width: 100%;
                            height: 100%;
                            border: none;
                            border-radius: 0 0 12px 12px;
                        "
                        title="${fileName}">
                </iframe>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    const closeBtn = modal.querySelector('.close-preview-btn');
    closeBtn.addEventListener('click', () => {
        document.body.removeChild(modal);
    });
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    });
}

// 预览视频文件
function previewVideoFile(path, fileName) {
    const modal = document.createElement('div');
    modal.className = 'preview-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.9);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
    `;
    
    modal.innerHTML = `
        <div class="preview-content" style="
            max-width: 95%;
            max-height: 95%;
            position: relative;
        ">
            <div class="preview-header" style="
                position: absolute;
                top: -50px;
                left: 0;
                right: 0;
                text-align: center;
                color: white;
                z-index: 10001;
            ">
                <h3 style="margin: 0; font-size: 16px; text-shadow: 0 2px 4px rgba(0,0,0,0.5);">
                    ${fileName}
                </h3>
            </div>
            <video controls style="
                max-width: 100%;
                max-height: 100%;
                border-radius: 8px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
            ">
                <source src="${getPreviewUrl(path)}" type="video/${fileName.split('.').pop()}">
                您的浏览器不支持视频播放
            </video>
            <button class="close-preview-btn" style="
                position: absolute;
                top: -50px;
                right: 0;
                background: none;
                border: none;
                font-size: 24px;
                cursor: pointer;
                color: white;
                padding: 8px;
                border-radius: 4px;
                transition: all 0.2s;
                text-shadow: 0 2px 4px rgba(0,0,0,0.5);
            ">&times;</button>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    const closeBtn = modal.querySelector('.close-preview-btn');
    closeBtn.addEventListener('click', () => {
        document.body.removeChild(modal);
    });
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    });
}

// 预览音频文件
function previewAudioFile(path, fileName) {
    const modal = document.createElement('div');
    modal.className = 'preview-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
    `;
    
    modal.innerHTML = `
        <div class="preview-content" style="
            background: white;
            border-radius: 12px;
            max-width: 500px;
            width: 90%;
            padding: 40px;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        ">
            <div class="preview-header" style="margin-bottom: 32px;">
                <h3 style="margin: 0; font-size: 20px; color: #111827;">
                    <i class="fas fa-music" style="margin-right: 12px; color: #7c3aed;"></i>
                    ${fileName}
                </h3>
            </div>
            <div class="preview-body" style="margin-bottom: 32px;">
                <audio controls style="width: 100%;">
                    <source src="${getPreviewUrl(path)}" type="audio/${fileName.split('.').pop()}">
                    您的浏览器不支持音频播放
                </audio>
            </div>
            <button class="close-preview-btn" style="
                background: #6b7280;
                border: none;
                color: white;
                padding: 12px 24px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.2s;
            ">关闭</button>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    const closeBtn = modal.querySelector('.close-preview-btn');
    closeBtn.addEventListener('click', () => {
        document.body.removeChild(modal);
    });
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    });
}

// HTML转义函数
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function copyFile(path, fileName) {
    console.log('复制文件:', path, fileName);
    
    // 显示文件树选择器
    showFileTreeSelector(path, fileName, 'copy');
}

// 降级复制到剪贴板函数
function fallbackCopyToClipboard(text, fileName) {
    try {
        // 创建临时文本区域
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        
        // 选择文本并复制
        textArea.focus();
        textArea.select();
        
        // 尝试使用execCommand复制
        const successful = document.execCommand('copy');
        if (successful) {
            showNotification(`文件路径已复制到剪贴板: ${fileName}`, 'success');
        } else {
            // 如果execCommand也失败，提示用户手动复制
            showNotification(`无法自动复制，请手动选择并复制路径: ${text}`, 'warning');
        }
        
        // 清理临时元素
        document.body.removeChild(textArea);
        
    } catch (error) {
        console.error('复制到剪贴板失败:', error);
        // 最后的降级方案：显示路径让用户手动复制
        showNotification(`复制失败，请手动复制路径: ${text}`, 'error');
    }
}

function cutFile(path, fileName) {
    console.log('剪切文件:', path, fileName);
    
    // 显示文件树选择器
    showFileTreeSelector(path, fileName, 'cut');
}

// 降级剪切到剪贴板函数
function fallbackCutToClipboard(text, fileName) {
    try {
        // 创建临时文本区域
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        
        // 选择文本并复制
        textArea.focus();
        textArea.select();
        
        // 尝试使用execCommand复制
        const successful = document.execCommand('copy');
        if (successful) {
            // 保存剪切状态到本地存储
            localStorage.setItem('cutFile', JSON.stringify({ 
                text, 
                fileName, 
                timestamp: Date.now() 
            }));
            showNotification(`文件已标记为剪切: ${fileName}`, 'success');
        } else {
            // 如果execCommand也失败，提示用户手动复制
            showNotification(`无法自动剪切，请手动选择并复制路径: ${text}`, 'warning');
        }
        
        // 清理临时元素
        document.body.removeChild(textArea);
        
    } catch (error) {
        console.error('剪切到剪贴板失败:', error);
        // 最后的降级方案：显示路径让用户手动复制
        showNotification(`剪切失败，请手动复制路径: ${text}`, 'error');
    }
}

function shareFile(path, fileName) {
    console.log('分享文件:', path, fileName);
    
    // 检查是否支持Web Share API
    if (navigator.share && navigator.canShare) {
        const shareData = {
            title: fileName,
            text: `分享文件: ${fileName}`,
            url: window.location.origin + '/api/download?path=' + encodeURIComponent(path)
        };
        
        // 检查是否可以分享这些数据
        if (navigator.canShare(shareData)) {
            navigator.share(shareData).then(() => {
                showNotification(`文件分享成功: ${fileName}`, 'success');
            }).catch(error => {
                console.log('分享失败:', error);
                if (error.name === 'AbortError') {
                    showNotification('分享已取消', 'info');
                } else {
                    showNotification(`分享失败: ${error.message}`, 'error');
                }
            });
        } else {
            showNotification('当前环境不支持分享此类型的内容', 'warning');
        }
    } else {
        // 降级方案：复制下载链接到剪贴板
        const downloadUrl = window.location.origin + '/api/download?path=' + encodeURIComponent(path);
        copyFile(downloadUrl, fileName);
        showNotification(`已复制下载链接到剪贴板: ${fileName}`, 'info');
    }
}

function showFileProperties(path, fileName) {
    console.log('显示文件属性:', path, fileName);
    
    // 创建属性对话框
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        border-radius: 12px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        z-index: 1001;
        min-width: 400px;
        max-width: 600px;
        max-height: 80vh;
        overflow-y: auto;
    `;
    
    modal.innerHTML = `
        <div class="modal-header" style="padding: 20px 24px 16px; border-bottom: 1px solid #eee;">
            <h3 style="margin: 0; color: #333; font-size: 18px;">
                <i class="fas fa-info-circle" style="color: #007bff; margin-right: 8px;"></i>
                文件属性: ${fileName}
            </h3>
            <button class="modal-close" onclick="this.closest('.modal').remove()" style="
                position: absolute;
                top: 20px;
                right: 24px;
                background: none;
                border: none;
                font-size: 20px;
                cursor: pointer;
                color: #999;
            ">&times;</button>
        </div>
        <div class="modal-body" style="padding: 24px;">
            <div style="margin-bottom: 16px;">
                <strong>文件名:</strong> ${fileName}
            </div>
            <div style="margin-bottom: 16px;">
                <strong>路径:</strong> ${path}
            </div>
            <div style="margin-bottom: 16px;">
                <strong>类型:</strong> ${path.includes('.') ? '文件' : '文件夹'}
            </div>
            <div style="margin-bottom: 16px;">
                <strong>位置:</strong> ${currentPath || '根目录'}
            </div>
            <div style="margin-bottom: 16px;">
                <strong>最后修改:</strong> ${new Date().toLocaleString('zh-CN')}
            </div>
        </div>
        <div class="modal-footer" style="padding: 16px 24px 24px; border-top: 1px solid #eee; text-align: right;">
            <button onclick="this.closest('.modal').remove()" style="
                padding: 8px 16px;
                background: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
            ">关闭</button>
        </div>
    `;
    
    // 添加遮罩层
    const overlay = document.createElement('div');
    overlay.className = 'overlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        z-index: 1000;
    `;
    
    // 点击遮罩层关闭
    overlay.addEventListener('click', () => {
        modal.remove();
        overlay.remove();
    });
    
    document.body.appendChild(overlay);
    document.body.appendChild(modal);
}

async function deleteFile(path, fileName) {
    console.log('删除文件:', path, fileName);
    
    const confirmed = confirm(`确定要删除 "${fileName}" 吗？\n\n此操作无法撤销！`);
    if (!confirmed) return;
    
    try {
        // 使用统一的删除API
        const apiEndpoint = '/api/delete';
        
        const response = await fetch(apiEndpoint, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path: path })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(`"${fileName}" 已删除`, 'success');
            // 强制刷新文件列表，添加时间戳防止缓存
            console.log('文件删除成功，强制刷新文件列表，当前路径:', currentPath);
            console.log('删除的文件路径:', path);
            
            // 立即刷新一次
            loadFileList();
            
            // 延迟再刷新一次，确保服务器端缓存已清理
            setTimeout(() => {
                console.log('延迟刷新文件列表，当前路径:', currentPath);
                loadFileList();
            }, 500);
            
            // 再次延迟刷新，确保彻底清理
            setTimeout(() => {
                console.log('最终刷新文件列表，当前路径:', currentPath);
                loadFileList();
            }, 1000);
        } else {
            throw new Error(result.message || '删除失败');
        }
    } catch (error) {
        console.error('删除文件失败:', error);
        showNotification('删除文件失败: ' + error.message, 'error');
    }
}

async function deleteSharedFile(filename, owner) {
    console.log('删除共享文件:', filename, '所有者:', owner);
    
    const confirmed = confirm(`确定要删除共享文件 "${filename}" 吗？\n\n此操作无法撤销！`);
    if (!confirmed) return;
    
    try {
        // 使用共享文件删除API
        const apiEndpoint = '/api/sharing/delete';
        
        const response = await fetch(apiEndpoint, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename: filename, owner: owner })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(`共享文件 "${filename}" 已删除`, 'success');
            // 重新加载共享文件列表
            loadSharedFiles();
        } else {
            throw new Error(result.message || '删除失败');
        }
    } catch (error) {
        console.error('删除共享文件失败:', error);
        showNotification('删除共享文件失败: ' + error.message, 'error');
    }
}

function renameFile(path, fileName) {
    console.log('重命名文件:', path, fileName);
    
    // 显示重命名对话框
    const newName = prompt(`请输入新的名称:`, fileName);
    if (!newName || newName.trim() === '' || newName === fileName) {
        return;
    }
    
    // 调用重命名API
    executeRename(path, newName.trim());
}

// 删除文件函数
async function deleteSelectedFiles(paths = null) {
    if (!paths || paths.length === 0) return;
    
    try {
        showLoading();
        
        // 使用统一的删除API
        const apiEndpoint = '/api/delete';
        const method = 'DELETE';
        
        // 逐个删除文件
        for (const filePath of paths) {
            const response = await fetch(apiEndpoint, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path: filePath })
            });
            
            const result = await response.json();
            
            if (!result.success) {
                throw new Error(result.message || '删除失败');
            }
        }
        
        showNotification(`成功删除 ${paths.length} 个文件`, 'success');
        
        // 强制刷新文件列表
        console.log('批量删除成功，强制刷新文件列表');
        setTimeout(() => {
            loadFileList();
        }, 100);
        
    } catch (error) {
        console.error('删除文件错误:', error);
        showNotification('删除文件时发生错误: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// 文件树选择器
function showFileTreeSelector(sourcePath, fileName, operation) {
    console.log('显示文件树选择器:', { sourcePath, fileName, operation });
    
    // 创建模态框
    const modal = document.createElement('div');
    modal.className = 'modal file-tree-modal';
    modal.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        border-radius: 12px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        z-index: 1001;
        width: 600px;
        max-width: 90vw;
        max-height: 80vh;
        overflow: hidden;
        display: flex;
        flex-direction: column;
    `;
    
    // 模态框头部
    const header = document.createElement('div');
    header.style.cssText = `
        padding: 20px 24px 16px;
        border-bottom: 1px solid #eee;
        background: #f8f9fa;
        border-radius: 12px 12px 0 0;
    `;
    
    const operationText = operation === 'copy' ? '复制' : '剪切';
    header.innerHTML = `
        <h3 style="margin: 0; color: #333; font-size: 18px; display: flex; align-items: center; gap: 12px;">
            <i class="fas fa-${operation === 'copy' ? 'copy' : 'cut'}" style="color: #007bff;"></i>
            ${operationText} "${fileName}" 到:
        </h3>
        <p style="margin: 8px 0 0; color: #666; font-size: 14px;">
            请选择目标文件夹
        </p>
    `;
    
    // 关闭按钮
    const closeBtn = document.createElement('button');
    closeBtn.innerHTML = '&times;';
    closeBtn.style.cssText = `
        position: absolute;
        top: 20px;
        right: 24px;
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        color: #999;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        transition: background-color 0.2s;
    `;
    closeBtn.addEventListener('mouseenter', () => closeBtn.style.backgroundColor = '#f0f0f0');
    closeBtn.addEventListener('mouseleave', () => closeBtn.style.backgroundColor = 'transparent');
    closeBtn.addEventListener('click', () => modal.remove());
    header.appendChild(closeBtn);
    
    // 模态框主体
    const body = document.createElement('div');
    body.style.cssText = `
        flex: 1;
        padding: 20px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 16px;
    `;
    
    // 当前路径显示
    const currentPathDiv = document.createElement('div');
    currentPathDiv.style.cssText = `
        background: #f8f9fa;
        padding: 12px 16px;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        font-family: monospace;
        font-size: 14px;
        color: #495057;
    `;
    currentPathDiv.innerHTML = `<strong>当前位置:</strong> 根目录`;
    
    // 添加搜索框
    const searchDiv = document.createElement('div');
    searchDiv.style.cssText = `
        margin-top: 12px;
    `;
    
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.placeholder = '搜索文件夹...';
    searchInput.style.cssText = `
        width: 100%;
        padding: 8px 12px;
        border: 1px solid #ddd;
        border-radius: 6px;
        font-size: 14px;
        box-sizing: border-box;
    `;
    
    // 搜索功能
    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const folderItems = container.querySelectorAll('div[style*="padding-left"]');
        
        folderItems.forEach(item => {
            const folderName = item.querySelector('span')?.textContent?.toLowerCase() || '';
            const folderPath = item.querySelector('small')?.textContent?.toLowerCase() || '';
            
            if (folderName.includes(searchTerm) || folderPath.includes(searchTerm)) {
                item.style.display = 'flex';
                // 高亮匹配的文本
                if (searchTerm) {
                    item.style.backgroundColor = '#fff3cd';
                } else {
                    item.style.backgroundColor = 'transparent';
                }
            } else {
                item.style.display = 'none';
            }
        });
    });
    
    searchDiv.appendChild(searchInput);
    currentPathDiv.appendChild(searchDiv);
    
    // 文件树容器
    const treeContainer = document.createElement('div');
    treeContainer.id = 'file-tree-container';
    treeContainer.style.cssText = `
        border: 1px solid #e9ecef;
        border-radius: 8px;
        max-height: 300px;
        overflow-y: auto;
        background: white;
    `;
    
    // 操作按钮
    const buttonContainer = document.createElement('div');
    buttonContainer.style.cssText = `
        display: flex;
        gap: 12px;
        justify-content: flex-end;
        padding-top: 16px;
        border-top: 1px solid #eee;
    `;
    
    const cancelBtn = document.createElement('button');
    cancelBtn.textContent = '取消';
    cancelBtn.style.cssText = `
        padding: 10px 20px;
        background: #6c757d;
        color: white;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        font-size: 14px;
        transition: background-color 0.2s;
    `;
    cancelBtn.addEventListener('mouseenter', () => cancelBtn.style.backgroundColor = '#5a6268');
    cancelBtn.addEventListener('mouseleave', () => cancelBtn.style.backgroundColor = '#6c757d');
    cancelBtn.addEventListener('click', () => modal.remove());
    
    const confirmBtn = document.createElement('button');
    confirmBtn.textContent = `确认${operationText}`;
    confirmBtn.style.cssText = `
        padding: 10px 20px;
        background: #007bff;
        color: white;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 600;
        transition: background-color 0.2s;
    `;
    confirmBtn.addEventListener('mouseenter', () => confirmBtn.style.backgroundColor = '#0056b3');
    confirmBtn.addEventListener('mouseleave', () => confirmBtn.style.backgroundColor = '#007bff');
    
    // 选择的目标路径
    let selectedTargetPath = '.';
    
    // 确认按钮点击事件
    confirmBtn.addEventListener('click', () => {
        if (operation === 'copy') {
            executeCopy(sourcePath, selectedTargetPath, fileName);
        } else if (operation === 'cut') {
            executeCut(sourcePath, selectedTargetPath, fileName);
        }
        modal.remove();
    });
    
    buttonContainer.appendChild(cancelBtn);
    buttonContainer.appendChild(confirmBtn);
    
    // 组装模态框
    body.appendChild(currentPathDiv);
    body.appendChild(treeContainer);
    body.appendChild(buttonContainer);
    
    modal.appendChild(header);
    modal.appendChild(body);
    
    // 添加遮罩层
    const overlay = document.createElement('div');
    overlay.className = 'overlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        z-index: 1000;
    `;
    
    // 点击遮罩层关闭
    overlay.addEventListener('click', () => {
        modal.remove();
        overlay.remove();
    });
    
    document.body.appendChild(overlay);
    document.body.appendChild(modal);
    
    // 加载文件树
    loadFileTree(treeContainer, selectedTargetPath, (path) => {
        selectedTargetPath = path;
        currentPathDiv.innerHTML = `<strong>当前位置:</strong> ${path || '根目录'}`;
        
        // 重新加载文件树以显示新路径下的内容
        loadFileTree(treeContainer, path, (newPath) => {
            selectedTargetPath = newPath;
            currentPathDiv.innerHTML = `<strong>当前位置:</strong> ${newPath || '根目录'}`;
        });
    });
    
    // 将selectedTargetPath暴露到全局，供搜索函数使用
    window.selectedTargetPath = selectedTargetPath;
}

// 加载文件树
async function loadFileTree(container, currentPath, onPathChange) {
    try {
        container.innerHTML = '<div style="padding: 20px; text-align: center; color: #666;">正在加载文件树...</div>';
        
        // 简化版本：只加载当前目录和父级目录
        const allFolders = await getSimpleFolderTree(currentPath || '.');
        
        if (allFolders && allFolders.length > 0) {
            renderSimpleFileTree(container, allFolders, currentPath, onPathChange);
        } else {
            container.innerHTML = '<div style="padding: 20px; text-align: center; color: #dc3545;">加载文件树失败</div>';
        }
    } catch (error) {
        console.error('加载文件树失败:', error);
        container.innerHTML = `<div style="padding: 20px; text-align: center; color: #dc3545;">加载文件树失败: ${error.message}</div>`;
    }
}

// 简化的文件夹树获取函数
async function getSimpleFolderTree(currentPath) {
    try {
        const folders = [];
        
        // 添加根目录
        folders.push({
            name: '根目录',
            path: '.',
            level: 0,
            parentPath: null
        });
        
        // 如果当前不在根目录，添加返回上一级按钮
        if (currentPath && currentPath !== '.' && currentPath !== '') {
            const parentPath = getParentPath(currentPath);
            folders.push({
                name: '← 返回上一级',
                path: parentPath,
                level: 0,
                parentPath: null,
                isBackButton: true
            });
        }
        
        // 获取当前目录下的文件夹
        try {
            const response = await fetch(`/api/list?path=${encodeURIComponent(currentPath || '.')}`);
            if (response.ok) {
                const result = await response.json();
                if (result && result.items && Array.isArray(result.items)) {
                    const currentFolders = result.items.filter(item => item.is_directory);
                    
                    currentFolders.forEach(folder => {
                        const fullPath = (currentPath && currentPath !== '.') ? `${currentPath}/${folder.name}` : folder.name;
                        folders.push({
                            name: folder.name,
                            path: fullPath,
                            level: 1,
                            parentPath: currentPath || '.'
                        });
                    });
                }
            }
        } catch (error) {
            console.warn('获取当前目录失败:', error);
        }
        
        return folders;
    } catch (error) {
        console.error('获取文件夹树失败:', error);
        return [];
    }
}

// 获取父级路径
function getParentPath(path) {
    if (!path || path === '.' || path === '') return '.';
    const parts = path.split('/');
    if (parts.length <= 1) return '.';
    parts.pop();
    return parts.join('/');
}

// 简化的文件树渲染函数
function renderSimpleFileTree(container, folders, currentPath, onPathChange) {
    container.innerHTML = '';
    
    // 添加搜索框
    const searchContainer = document.createElement('div');
    searchContainer.style.cssText = 'margin-bottom: 15px;';
    searchContainer.innerHTML = `
        <input type="text" 
               placeholder="搜索文件夹..." 
               style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px;"
               onkeyup="filterFileTree(this.value, '${currentPath || '.'}')">
    `;
    container.appendChild(searchContainer);
    
    // 渲染文件夹列表
    folders.forEach(folder => {
        const folderItem = document.createElement('div');
        folderItem.style.cssText = `
            padding: 8px 12px;
            margin: 2px 0;
            cursor: pointer;
            border-radius: 4px;
            transition: background-color 0.2s;
            display: flex;
            align-items: center;
            ${folder.isBackButton ? 'background-color: #f8f9fa; border: 1px solid #e9ecef;' : ''}
        `;
        
        if (folder.isBackButton) {
            folderItem.style.cssText += 'color: #6c757d; font-weight: 500;';
        }
        
        folderItem.innerHTML = `
            <i class="fas ${folder.isBackButton ? 'fa-arrow-left' : 'fa-folder'}" 
               style="margin-right: 8px; color: ${folder.isBackButton ? '#6c757d' : '#ffc107'};"></i>
            <span>${folder.name}</span>
        `;
        
        folderItem.onclick = () => {
            if (onPathChange) {
                onPathChange(folder.path);
            }
            
            // 无论是返回上一级按钮还是普通文件夹，都需要重新加载文件树
            setTimeout(() => {
                loadFileTree(container, folder.path, onPathChange);
            }, 100);
        };
        
        folderItem.onmouseover = () => {
            if (!folder.isBackButton) {
                folderItem.style.backgroundColor = '#f8f9fa';
            }
        };
        
        folderItem.onmouseout = () => {
            if (!folder.isBackButton) {
                folderItem.style.backgroundColor = 'transparent';
            }
        };
        
        container.appendChild(folderItem);
    });
}

// 搜索过滤函数
function filterFileTree(searchTerm, currentPath) {
    const container = document.querySelector('.file-tree-container');
    if (!container) return;
    
    if (!searchTerm.trim()) {
        // 如果搜索框为空，重新加载文件树
        loadFileTree(container, currentPath, (newPath) => {
            // 更新选中的目标路径
            if (window.selectedTargetPath !== undefined) {
                window.selectedTargetPath = newPath;
            }
            console.log('选择新路径:', newPath);
        });
        return;
    }
    
    // 简单的搜索过滤逻辑
    const items = container.querySelectorAll('div[style*="cursor: pointer"]');
    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        if (text.includes(searchTerm.toLowerCase())) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}

// 执行复制操作
async function executeCopy(sourcePath, targetPath, fileName) {
    try {
        showLoading();
        showNotification(`正在复制 "${fileName}" 到 ${targetPath || '根目录'}...`, 'info');
        
        // 构建正确的源路径和目标路径
        const finalSourcePath = sourcePath;
        const finalTargetPath = targetPath ? `${targetPath}/${fileName}` : fileName;
        
        console.log('复制操作路径:', { sourcePath: finalSourcePath, targetPath: finalTargetPath });
        
        // 调用复制API
        const response = await fetch('/api/copy', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                source_path: finalSourcePath,
                target_path: finalTargetPath
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(`成功复制 "${fileName}" 到 ${targetPath || '根目录'}`, 'success');
            // 刷新文件列表
            loadFileList();
        } else {
            throw new Error(result.message || '复制失败');
        }
        
    } catch (error) {
        console.error('复制文件错误:', error);
        showNotification(`复制文件时发生错误: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

// 执行重命名操作
async function executeRename(oldPath, newName) {
    try {
        showLoading();
        showNotification(`正在重命名文件...`, 'info');
        
        // 构建新路径
        const pathParts = oldPath.split('/');
        const oldFileName = pathParts.pop();
        const newPath = pathParts.length > 0 ? pathParts.join('/') + '/' + newName : newName;
        
        console.log('重命名操作路径:', { oldPath, newName, newPath });
        
        // 调用重命名API
        const response = await fetch('/api/rename', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                old_path: oldPath,
                new_name: newName
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(`成功重命名文件为: ${newName}`, 'success');
            // 刷新文件列表
            loadFileList();
        } else {
            throw new Error(result.message || '重命名失败');
        }
        
    } catch (error) {
        console.error('重命名文件错误:', error);
        showNotification(`重命名文件时发生错误: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

// 执行剪切操作
async function executeCut(sourcePath, targetPath, fileName) {
    try {
        showLoading();
        showNotification(`正在移动 "${fileName}" 到 ${targetPath || '根目录'}...`, 'info');
        
        // 构建正确的源路径和目标路径
        const finalSourcePath = sourcePath;
        const finalTargetPath = targetPath ? `${targetPath}/${fileName}` : fileName;
        
        console.log('移动操作路径:', { sourcePath: finalSourcePath, targetPath: finalTargetPath });
        
        // 调用移动API
        const response = await fetch('/api/move', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                source_path: finalSourcePath,
                target_path: finalTargetPath
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(`成功移动 "${fileName}" 到 ${targetPath || '根目录'}`, 'success');
            // 刷新文件列表
            loadFileList();
        } else {
            throw new Error(result.message || '移动失败');
        }
        
    } catch (error) {
        console.error('移动文件错误:', error);
        showNotification(`移动文件时发生错误: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

// 应用视图特定的样式
function applyViewStyles(view) {
    // 视图样式功能已移除
    console.log('视图样式功能已禁用');
}

// 排序文件
function sortFiles(sortBy) {
    // 排序功能已移除
    console.log('排序功能已禁用');
}

// 获取文件行数据
function getFileRowData(row) {
    // 文件行数据获取功能已移除
    console.log('文件行数据获取功能已禁用');
    return null;
}

// 解析文件大小
function parseFileSize(sizeStr) {
    // 文件大小解析功能已移除
    console.log('文件大小解析功能已禁用');
    return 0;
}

// 分享文件到共享目录
async function shareToShared(sourcePath, fileName, isDirectory) {
    try {
        console.log('shareToShared 调用参数:', { sourcePath, fileName, isDirectory });
        
        // 显示分享对话框
        const operation = await showShareDialog(fileName, isDirectory);
        if (!operation) return; // 用户取消
        
        const { targetName } = operation;
        console.log('分享对话框返回:', operation);
        
        showLoading();
        showNotification(`正在共享 "${fileName}" 到共享目录...`, 'info');
        
        // 调用共享API
        const apiEndpoint = '/api/sharing/share';
        const requestBody = {
            source_path: sourcePath,
            target_name: targetName
        };
        console.log('发送到API的请求体:', requestBody);
        
        const response = await fetch(apiEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(`成功共享 "${fileName}" 到共享目录`, 'success');
            // 刷新文件列表
            loadFileList();
        } else {
            throw new Error(result.message || '分享失败');
        }
        
    } catch (error) {
        console.error('分享文件错误:', error);
        showNotification(`分享文件时发生错误: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

// 显示分享到共享目录的通用对话框
function showShareToSharedDialog() {
    // 检查是否有选中的文件
    const selectedFiles = getSelectedFiles();
    if (selectedFiles.length === 0) {
        showNotification('请先选择要分享的文件或文件夹', 'warning');
        return;
    }
    
    // 如果只选中一个文件，直接调用分享
    if (selectedFiles.length === 1) {
        const file = selectedFiles[0];
        shareToShared(file.path, file.name, file.isDirectory);
        return;
    }
    
    // 如果选中多个文件，显示批量分享对话框
    showBatchShareDialog(selectedFiles);
}

// 获取选中的文件
function getSelectedFiles() {
    const selectedRows = document.querySelectorAll('.file-row.selected');
    const files = [];
    
    selectedRows.forEach(row => {
        const nameElement = row.querySelector('.file-name');
        const path = row.getAttribute('data-path');
        const isDirectory = row.classList.contains('folder');
        
        if (nameElement && path) {
            files.push({
                name: nameElement.textContent,
                path: path,
                isDirectory: isDirectory
            });
        }
    });
    
    return files;
}

// 显示批量分享对话框
function showBatchShareDialog(files) {
    const dialog = document.createElement('div');
    dialog.className = 'share-dialog';
    dialog.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 2000;
    `;
    
    const content = document.createElement('div');
    content.style.cssText = `
        background: white;
        border-radius: 12px;
        padding: 24px;
        width: 500px;
        max-width: 90vw;
        max-height: 80vh;
        overflow-y: auto;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
    `;
    
    const title = document.createElement('h3');
    title.textContent = `批量分享 ${files.length} 个文件/文件夹到共享目录`;
    title.style.cssText = `
        margin: 0 0 20px 0;
        color: #333;
        font-size: 18px;
    `;
    
    // 文件列表
    const fileList = document.createElement('div');
    fileList.style.cssText = `
        margin-bottom: 20px;
        max-height: 200px;
        overflow-y: auto;
        border: 1px solid #eee;
        border-radius: 6px;
        padding: 12px;
    `;
    
    files.forEach(file => {
        const fileItem = document.createElement('div');
        fileItem.style.cssText = `
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px;
            border-bottom: 1px solid #f0f0f0;
        `;
        
        const icon = document.createElement('i');
        icon.className = `fas ${file.isDirectory ? 'fa-folder' : 'fa-file'}`;
        icon.style.color = file.isDirectory ? '#f59e0b' : '#6b7280';
        
        const name = document.createElement('span');
        name.textContent = file.name;
        
        fileItem.appendChild(icon);
        fileItem.appendChild(name);
        fileList.appendChild(fileItem);
    });
    
    // 硬链接共享说明
    const infoGroup = document.createElement('div');
    infoGroup.style.cssText = `
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 20px;
        padding: 12px;
        background: #f0f9ff;
        border: 1px solid #bae6fd;
        border-radius: 6px;
        color: #0369a1;
    `;
    
    const infoIcon = document.createElement('i');
    infoIcon.className = 'fas fa-info-circle';
    
    const infoText = document.createElement('span');
    infoText.textContent = '使用硬链接共享，节省存储空间';
    
    infoGroup.appendChild(infoIcon);
    infoGroup.appendChild(infoText);
    
    // 按钮组
    const buttonGroup = document.createElement('div');
    buttonGroup.style.cssText = `
        display: flex;
        gap: 12px;
        justify-content: flex-end;
    `;
    
    const cancelBtn = document.createElement('button');
    cancelBtn.textContent = '取消';
    cancelBtn.style.cssText = `
        padding: 10px 20px;
        border: 1px solid #ddd;
        background: white;
        border-radius: 6px;
        cursor: pointer;
        font-size: 14px;
    `;
    cancelBtn.addEventListener('click', () => {
        document.body.removeChild(dialog);
    });
    
    const shareBtn = document.createElement('button');
    shareBtn.textContent = '批量分享';
    shareBtn.style.cssText = `
        padding: 10px 20px;
        background: #007bff;
        color: white;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        font-size: 14px;
    `;
    shareBtn.addEventListener('click', async () => {
        await batchShareFiles(files);
        document.body.removeChild(dialog);
    });
    
    buttonGroup.appendChild(cancelBtn);
    buttonGroup.appendChild(shareBtn);
    
    // 组装内容
    content.appendChild(title);
    content.appendChild(fileList);
    content.appendChild(infoGroup);
    content.appendChild(buttonGroup);
    dialog.appendChild(content);
    
    // 添加到页面
    document.body.appendChild(dialog);
}

// 批量分享文件
async function batchShareFiles(files) {
    try {
        showLoading();
        showNotification(`正在批量共享 ${files.length} 个文件/文件夹到共享目录...`, 'info');
        
        let successCount = 0;
        let errorCount = 0;
        
        for (const file of files) {
            try {
                const apiEndpoint = '/api/sharing/share';
                const response = await fetch(apiEndpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        source_path: file.path,
                        target_name: file.name
                    })
                });
                
                if (response.ok) {
                    const result = await response.json();
                    if (result.success) {
                        successCount++;
                    } else {
                        errorCount++;
                        console.error(`分享失败: ${file.name} - ${result.message}`);
                    }
                } else {
                    errorCount++;
                    console.error(`分享失败: ${file.name} - HTTP ${response.status}`);
                }
            } catch (error) {
                errorCount++;
                console.error(`分享失败: ${file.name} - ${error.message}`);
            }
        }
        
        // 显示结果
        if (errorCount === 0) {
            showNotification(`成功共享所有 ${successCount} 个文件/文件夹到共享目录`, 'success');
        } else {
            showNotification(`批量分享完成: 成功 ${successCount} 个，失败 ${errorCount} 个`, errorCount > successCount ? 'warning' : 'success');
        }
        
        // 刷新文件列表
        loadFileList();
        
    } catch (error) {
        console.error('批量分享错误:', error);
        showNotification(`批量分享时发生错误: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

// 显示分享对话框
function showShareDialog(fileName, isDirectory) {
    return new Promise((resolve) => {
        // 创建对话框
        const dialog = document.createElement('div');
        dialog.className = 'share-dialog';
        dialog.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 2000;
        `;
        
        const content = document.createElement('div');
        content.style.cssText = `
            background: white;
            border-radius: 12px;
            padding: 24px;
            width: 400px;
            max-width: 90vw;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        `;
        
        const title = document.createElement('h3');
        title.textContent = `分享${isDirectory ? '文件夹' : '文件'}到共享目录`;
        title.style.cssText = `
            margin: 0 0 20px 0;
            color: #333;
            font-size: 18px;
        `;
        
        const form = document.createElement('div');
        form.style.cssText = `
            display: flex;
            flex-direction: column;
            gap: 16px;
        `;
        
        // 文件名输入
        const nameGroup = document.createElement('div');
        nameGroup.style.cssText = `
            display: flex;
            flex-direction: column;
            gap: 8px;
        `;
        
        const nameLabel = document.createElement('label');
        nameLabel.textContent = '目标名称:';
        nameLabel.style.cssText = `
            font-weight: 500;
            color: #555;
        `;
        
        const nameInput = document.createElement('input');
        nameInput.type = 'text';
        nameInput.value = fileName;
        nameInput.style.cssText = `
            padding: 10px 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
            outline: none;
        `;
        nameInput.addEventListener('input', (e) => {
            nameInput.value = e.target.value;
        });
        
        nameGroup.appendChild(nameLabel);
        nameGroup.appendChild(nameInput);
        
        // 硬链接共享说明
        const infoGroup = document.createElement('div');
        infoGroup.style.cssText = `
            display: flex;
            flex-direction: column;
            gap: 8px;
            padding: 12px;
            background: #f8f9fa;
            border-radius: 6px;
            border-left: 4px solid #007bff;
        `;
        
        const infoText = document.createElement('p');
        infoText.textContent = '使用硬链接共享文件，节省存储空间，保持文件同步';
        infoText.style.cssText = `
            margin: 0;
            color: #666;
            font-size: 13px;
            line-height: 1.4;
        `;
        
        infoGroup.appendChild(infoText);
        
        form.appendChild(nameGroup);
        form.appendChild(infoGroup);
        
        // 按钮组
        const buttonGroup = document.createElement('div');
        buttonGroup.style.cssText = `
            display: flex;
            gap: 12px;
            justify-content: flex-end;
            margin-top: 20px;
        `;
        
        const cancelBtn = document.createElement('button');
        cancelBtn.textContent = '取消';
        cancelBtn.style.cssText = `
            padding: 10px 20px;
            border: 1px solid #ddd;
            background: white;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
        `;
        cancelBtn.addEventListener('click', () => {
            document.body.removeChild(dialog);
            resolve(null);
        });
        
        const shareBtn = document.createElement('button');
        shareBtn.textContent = '分享';
        shareBtn.style.cssText = `
            padding: 10px 20px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
        `;
        shareBtn.addEventListener('click', () => {
            const targetName = nameInput.value.trim();
            
            if (!targetName) {
                alert('请输入目标名称');
                return;
            }
            
            document.body.removeChild(dialog);
            resolve({
                targetName,
                operationType: 'hardlink' // 固定使用硬链接共享
            });
        });
        
        buttonGroup.appendChild(cancelBtn);
        buttonGroup.appendChild(shareBtn);
        
        // 组装表单
        form.appendChild(nameGroup);
        form.appendChild(buttonGroup);
        
        content.appendChild(title);
        content.appendChild(form);
        dialog.appendChild(content);
        
        // 添加到页面
        document.body.appendChild(dialog);
        
        // 聚焦到输入框
        nameInput.focus();
    });
}

// 导出函数供全局使用
window.showNotification = showNotification;
window.openFolder = openFolder;
window.downloadFile = downloadFile;
window.editFile = editFile;
window.showFileMenu = showFileMenu;
window.hideNewFolderModal = hideNewFolderModal;
window.previewFile = previewFile;
window.copyFile = copyFile;
window.cutFile = cutFile;
window.renameFile = renameFile;
window.shareFile = shareFile;
window.shareToShared = shareToShared;
window.showShareToSharedDialog = showShareToSharedDialog;
window.showFileProperties = showFileProperties;
window.deleteFile = deleteFile;
window.handleLogout = handleLogout;
window.toggleFavorite = toggleFavorite;
window.isFileFavorite = isFileFavorite;
window.getFavoriteFiles = getFavoriteFiles;
window.clearAllFavorites = clearAllFavorites;
window.recordFileAccess = recordFileAccess;
window.getRecentFiles = getRecentFiles;
window.clearRecentHistory = clearRecentHistory;
window.removeClearHistoryButton = removeClearHistoryButton;


// 退出登录处理函数
async function handleLogout() {
    console.log('用户请求退出登录');
    
    // 显示确认对话框
    if (confirm('确定要退出登录吗？')) {
        try {
            showNotification('正在退出登录...', 'info');
            
            // 调用服务器端logout API
            const response = await fetch('/api/auth/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                // 清除本地存储的用户信息
                localStorage.removeItem('user_token');
                localStorage.removeItem('user_info');
                localStorage.removeItem('user_permissions');
                localStorage.removeItem('current_path');
                localStorage.removeItem('view_mode');
                localStorage.removeItem('sort_order');
                
                // 清除session storage
                sessionStorage.clear();
                
                // 显示退出成功通知
                showNotification('退出登录成功', 'success');
                
                // 延迟跳转到登录页面
                setTimeout(() => {
                    window.location.href = '/login';
                }, 1000);
                
            } else {
                // 如果API调用失败，尝试直接跳转到logout页面
                console.warn('Logout API调用失败，尝试直接跳转');
                showNotification('正在跳转到登录页面...', 'info');
                
                setTimeout(() => {
                    window.location.href = '/logout';
                }, 1000);
            }
            
        } catch (error) {
            console.error('退出登录时发生错误:', error);
            showNotification('退出登录时发生错误，正在跳转...', 'warning');
            
            // 即使出错也强制跳转到logout页面
            setTimeout(() => {
                window.location.href = '/logout';
            }, 2000);
        }
    }
}
