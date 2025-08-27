/**
 * 前端配置文件
 * 管理前端相关的配置选项，与后端配置保持一致
 */

// 前端配置对象
const FrontendConfig = {
    // 应用基础配置
    app: {
        name: "文件管理系统",
        version: "2.0.0",
        description: "现代化的文件管理系统",
        author: "File Manager Team",
        contact: "support@filemanager.local"
    },
    
    // 主题配置
    theme: {
        primaryColor: "#4a6fa5",
        secondaryColor: "#6c8ebf",
        backgroundColor: "#ffffff",
        textColor: "#333333",
        accentColor: "#e74c3c",
        successColor: "#28a745",
        warningColor: "#ffc107",
        errorColor: "#dc3545",
        infoColor: "#17a2b8",
        borderColor: "#dee2e6",
        shadowColor: "rgba(0, 0, 0, 0.1)",
        hoverColor: "#f8f9fa",
        focusColor: "#4a6fa5"
    },
    
    // 功能配置
    features: {
        defaultView: "list",           // 默认视图模式: list, grid, details
        pageSize: 50,                  // 每页显示项目数
        showHidden: false,             // 是否显示隐藏文件
        enableDragDrop: true,          // 是否启用拖拽上传
        enablePreview: true,           // 是否启用文件预览
        enableSearch: true,            // 是否启用搜索功能
        enableSorting: true,           // 是否启用排序功能
        enableBulkOperations: true,    // 是否启用批量操作
        enableKeyboardShortcuts: true, // 是否启用键盘快捷键
        enableContextMenu: true,       // 是否启用右键菜单
        enableBreadcrumb: true,        // 是否启用面包屑导航
        enableFileTree: true,          // 是否启用文件树
        enableThumbnails: true,        // 是否启用缩略图
        enableProgressBar: true,       // 是否启用进度条
        enableDebugMode: false,        // 是否启用调试模式
        showDevelopmentTools: false,   // 是否显示开发工具
        enableVirtualScrolling: true,  // 是否启用虚拟滚动
        enableLazyLoading: true        // 是否启用懒加载
    },
    
    // 编辑器配置
    editor: {
        enabled: true,
        defaultTheme: "default",
        availableThemes: ["default", "monokai", "eclipse", "dracula", "solarized", "github", "vs-dark"],
        syntaxHighlighting: true,
        lineNumbers: true,
        wordWrap: true,
        autoComplete: true,
        bracketMatching: true,
        lineFolding: true,
        searchReplace: true,
        minimap: true,
        fontSize: 14,
        fontFamily: "Consolas, Monaco, 'Courier New', 'Fira Code', monospace",
        tabSize: 4,
        insertSpaces: true,
        autoSave: true,
        autoSaveInterval: 30000, // 30秒
        maxFileSize: 10485760,   // 10MB
        enableLineHighlighting: true,
        enableBracketPairColorization: true,
        enableIndentGuides: true,
        enableWhitespace: false,
        enableLineEndings: true
    },
    
    // 通知配置
    notifications: {
        autoHide: true,
        autoHideDelay: 5000,        // 5秒
        maxNotifications: 5,
        position: "top-right",      // top-right, top-left, bottom-right, bottom-left
        animation: "slide",         // slide, fade, bounce, zoom
        sound: false,
        desktop: false,
        enableToast: true,
        enableSnackbar: true,
        enableModal: true
    },
    
    // 上传配置
    upload: {
        maxFileSize: 1073741824,    // 1GB
        maxFiles: 100,
        allowedExtensions: [],      // 空数组表示允许所有
        forbiddenExtensions: [".bat", ".cmd", ".com", ".pif", ".scr", ".vbs", ".js"],
        chunkSize: 1048576,         // 1MB分块
        retryAttempts: 3,
        retryDelay: 1000,
        showProgress: true,
        autoStart: true,
        concurrent: 3,
        enableDragDrop: true,
        enablePaste: true,
        enableCamera: false,
        enableMicrophone: false,
        enableScreenCapture: false,
        showFileList: true,
        enableResume: true,
        enableCancel: true
    },
    
    // 下载配置
    download: {
        enableResume: true,
        chunkSize: 1048576,         // 1MB分块
        concurrent: 3,
        showProgress: true,
        autoStart: true,
        enableQueue: true,
        maxConcurrent: 5,
        enableSpeedLimit: false,
        speedLimit: 1048576,        // 1MB/s
        enableNotification: true,
        enableAutoOpen: false
    },
    
    // 文件预览配置
    preview: {
        enabled: true,
        maxSize: 10485760,          // 10MB
        supportedTypes: [
            ".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".xml",
            ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp",
            ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"
        ],
        imageFormats: [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff"],
        textFormats: [".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".xml", ".sql", ".sh", ".bat", ".log"],
        officeFormats: [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".odt", ".ods", ".odp"],
        videoFormats: [".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm", ".mkv", ".m4v", ".3gp"],
        audioFormats: [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"],
        codeFormats: [".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".scss", ".less", ".vue", ".php", ".java", ".cpp", ".c", ".h", ".go", ".rs", ".swift", ".kt"],
        enableThumbnails: true,
        thumbnailSize: 150,
        enableFullscreen: true,
        enableZoom: true,
        enableRotate: true
    },
    
    // 性能配置
    performance: {
        lazyLoading: true,          // 懒加载
        virtualScrolling: true,     // 虚拟滚动
        debounceDelay: 300,         // 防抖延迟
        throttleDelay: 100,         // 节流延迟
        cacheEnabled: true,         // 启用缓存
        cacheSize: 100,             // 缓存大小
        preloadEnabled: true,       // 预加载
        preloadCount: 10,           // 预加载数量
        enableWebWorkers: true,     // 启用Web Workers
        enableServiceWorker: false, // 启用Service Worker
        enableIndexedDB: true,      // 启用IndexedDB
        enableLocalStorage: true,   // 启用LocalStorage
        enableSessionStorage: true, // 启用SessionStorage
        maxMemoryUsage: 52428800,   // 最大内存使用量 (50MB)
        enableGarbageCollection: true
    },
    
    // 安全配置
    security: {
        enableFileValidation: true,
        enablePathValidation: true,
        maxPathLength: 4096,
        forbiddenCharacters: ["<", ">", ":", "\"", "|", "?", "*"],
        enableXSSProtection: true,
        enableCSRFProtection: true,
        enableContentSecurityPolicy: true,
        enableStrictTransportSecurity: true,
        enableXFrameOptions: true,
        enableXContentTypeOptions: true,
        enableReferrerPolicy: true,
        allowedDomains: [],
        blockedDomains: [],
        enableSandbox: false
    },
    
    // 国际化配置
    i18n: {
        defaultLanguage: "zh-CN",
        supportedLanguages: ["zh-CN", "en-US", "ja-JP", "ko-KR"],
        dateFormat: "YYYY-MM-DD",
        timeFormat: "HH:mm:ss",
        numberFormat: {
            decimal: ".",
            thousands: ",",
            precision: 2
        },
        currency: "CNY",
        timezone: "Asia/Shanghai",
        enableAutoDetect: true,
        fallbackLanguage: "en-US"
    },
    
    // 快捷键配置
    shortcuts: {
        "Ctrl+S": "保存文件",
        "Ctrl+F": "搜索",
        "Ctrl+Z": "撤销",
        "Ctrl+Y": "重做",
        "Ctrl+A": "全选",
        "Ctrl+C": "复制",
        "Ctrl+V": "粘贴",
        "Ctrl+X": "剪切",
        "Ctrl+D": "删除",
        "Ctrl+N": "新建文件夹",
        "Ctrl+U": "上传文件",
        "Ctrl+Shift+N": "新建文件",
        "Ctrl+Shift+O": "打开文件",
        "Ctrl+Shift+S": "另存为",
        "Ctrl+Shift+F": "全局搜索",
        "Ctrl+Shift+R": "刷新",
        "Ctrl+Shift+T": "新建标签页",
        "Ctrl+W": "关闭标签页",
        "Ctrl+Tab": "下一个标签页",
        "Ctrl+Shift+Tab": "上一个标签页",
        "F1": "帮助",
        "F2": "重命名",
        "F3": "查找下一个",
        "F4": "查找上一个",
        "F5": "刷新",
        "F6": "地址栏",
        "F7": "拼写检查",
        "F8": "调试",
        "F9": "编译",
        "F10": "菜单",
        "F11": "全屏",
        "F12": "开发者工具",
        "Delete": "删除",
        "Enter": "打开/进入",
        "Backspace": "返回上级",
        "Space": "预览",
        "Tab": "下一个项目",
        "Shift+Tab": "上一个项目",
        "Home": "第一个项目",
        "End": "最后一个项目",
        "PageUp": "上一页",
        "PageDown": "下一页"
    },
    
    // 错误处理配置
    errorHandling: {
        retryAttempts: 3,
        retryDelay: 1000,
        showDetails: false,
        logErrors: true,
        userFriendlyMessages: true,
        enableErrorReporting: false,
        enableCrashReporting: false,
        enablePerformanceMonitoring: true,
        enableUserAnalytics: false,
        enableTelemetry: false
    },
    
    // 网络配置
    network: {
        timeout: 30000,             // 30秒
        retryAttempts: 3,
        retryDelay: 1000,
        enableOfflineMode: true,
        enableBackgroundSync: false,
        enablePushNotifications: false,
        enableWebSocket: true,
        enableServerSentEvents: false,
        enablePolling: true,
        pollingInterval: 5000,      // 5秒
        enableCompression: true,
        enableCaching: true,
        maxConcurrentRequests: 10
    },
    
    // 存储配置
    storage: {
        enableLocalStorage: true,
        enableSessionStorage: true,
        enableIndexedDB: true,
        enableWebSQL: false,
        enableFileSystem: false,
        maxStorageSize: 104857600,   // 100MB
        enableCompression: true,
        enableEncryption: false,
        enableBackup: true,
        backupInterval: 86400000,    // 24小时
        enableSync: false
    },
    
    // 主题配置
    themes: {
        light: {
            name: "浅色主题",
            primary: "#4a6fa5",
            secondary: "#6c8ebf",
            background: "#ffffff",
            surface: "#f8f9fa",
            text: "#333333",
            textSecondary: "#6c757d",
            border: "#dee2e6",
            shadow: "rgba(0, 0, 0, 0.1)",
            hover: "#e9ecef",
            focus: "#4a6fa5"
        },
        dark: {
            name: "深色主题",
            primary: "#4a6fa5",
            secondary: "#6c8ebf",
            background: "#1a1a1a",
            surface: "#2d2d2d",
            text: "#ffffff",
            textSecondary: "#b0b0b0",
            border: "#404040",
            shadow: "rgba(0, 0, 0, 0.3)",
            hover: "#404040",
            focus: "#4a6fa5"
        },
        blue: {
            name: "蓝色主题",
            primary: "#007bff",
            secondary: "#0056b3",
            background: "#f8f9fa",
            surface: "#ffffff",
            text: "#212529",
            textSecondary: "#6c757d",
            border: "#dee2e6",
            shadow: "rgba(0, 123, 255, 0.1)",
            hover: "#e3f2fd",
            focus: "#007bff"
        }
    }
};

// 配置管理器
class ConfigManager {
    constructor() {
        this.config = FrontendConfig;
        this.overrides = {};
        this.theme = 'light';
        this.language = 'zh-CN';
        this.loadFromLocalStorage();
        this.applyTheme();
        this.applyLanguage();
    }
    
    /**
     * 获取配置值
     * @param {string} key - 配置键，支持点号分隔的嵌套键
     * @param {*} defaultValue - 默认值
     * @returns {*} 配置值
     */
    get(key, defaultValue = null) {
        const keys = key.split('.');
        let value = this.config;
        
        // 检查是否有本地覆盖
        if (this.overrides[key] !== undefined) {
            return this.overrides[key];
        }
        
        try {
            for (const k of keys) {
                value = value[k];
            }
            return value !== undefined ? value : defaultValue;
        } catch (error) {
            return defaultValue;
        }
    }
    
    /**
     * 设置配置值
     * @param {string} key - 配置键
     * @param {*} value - 配置值
     */
    set(key, value) {
        this.overrides[key] = value;
        this.saveToLocalStorage();
        
        // 特殊处理某些配置
        if (key === 'theme') {
            this.theme = value;
            this.applyTheme();
        } else if (key === 'language') {
            this.language = value;
            this.applyLanguage();
        }
    }
    
    /**
     * 重置配置到默认值
     * @param {string} key - 配置键，如果不指定则重置所有
     */
    reset(key = null) {
        if (key) {
            delete this.overrides[key];
        } else {
            this.overrides = {};
        }
        this.saveToLocalStorage();
        this.applyTheme();
        this.applyLanguage();
    }
    
    /**
     * 从本地存储加载配置
     */
    loadFromLocalStorage() {
        try {
            const saved = localStorage.getItem('fileManagerConfig');
            if (saved) {
                this.overrides = JSON.parse(saved);
            }
            
            // 加载主题和语言设置
            this.theme = this.overrides.theme || 'light';
            this.language = this.overrides.language || 'zh-CN';
        } catch (error) {
            console.warn('加载本地配置失败:', error);
        }
    }
    
    /**
     * 保存配置到本地存储
     */
    saveToLocalStorage() {
        try {
            localStorage.setItem('fileManagerConfig', JSON.stringify(this.overrides));
        } catch (error) {
            console.warn('保存本地配置失败:', error);
        }
    }
    
    /**
     * 获取所有配置
     * @returns {object} 配置对象
     */
    getAll() {
        return {
            ...this.config,
            ...this.overrides
        };
    }
    
    /**
     * 应用主题配置
     */
    applyTheme() {
        const themeConfig = this.get(`themes.${this.theme}`);
        if (!themeConfig) return;
        
        const root = document.documentElement;
        
        // 设置CSS变量
        Object.entries(themeConfig).forEach(([key, value]) => {
            root.style.setProperty(`--${key.replace(/([A-Z])/g, '-$1').toLowerCase()}`, value);
        });
        
        // 设置主题类名
        root.className = root.className.replace(/theme-\w+/g, '');
        root.classList.add(`theme-${this.theme}`);
    }
    
    /**
     * 应用语言配置
     */
    applyLanguage() {
        // 这里可以添加语言切换逻辑
        document.documentElement.lang = this.language;
    }
    
    /**
     * 获取当前主题
     * @returns {string} 当前主题名称
     */
    getCurrentTheme() {
        return this.theme;
    }
    
    /**
     * 获取当前语言
     * @returns {string} 当前语言代码
     */
    getCurrentLanguage() {
        return this.language;
    }
    
    /**
     * 切换主题
     * @param {string} themeName - 主题名称
     */
    switchTheme(themeName) {
        if (this.config.themes[themeName]) {
            this.set('theme', themeName);
        }
    }
    
    /**
     * 切换语言
     * @param {string} languageCode - 语言代码
     */
    switchLanguage(languageCode) {
        if (this.config.i18n.supportedLanguages.includes(languageCode)) {
            this.set('language', languageCode);
        }
    }
    
    /**
     * 验证配置
     * @returns {object} 验证结果
     */
    validate() {
        const errors = [];
        const warnings = [];
        
        // 验证文件大小限制
        const maxFileSize = this.get('upload.maxFileSize');
        if (maxFileSize > 2147483648) { // 2GB
            warnings.push('文件大小限制超过2GB，可能影响性能');
        }
        
        // 验证分块大小
        const chunkSize = this.get('upload.chunkSize');
        if (chunkSize < 524288) { // 512KB
            errors.push('分块大小不能小于512KB');
        }
        
        // 验证页面大小
        const pageSize = this.get('features.pageSize');
        if (pageSize > 200) {
            warnings.push('页面大小超过200，可能影响性能');
        }
        
        // 验证缓存大小
        const cacheSize = this.get('performance.cacheSize');
        if (cacheSize > 1000) {
            warnings.push('缓存大小超过1000，可能影响内存使用');
        }
        
        return { errors, warnings, isValid: errors.length === 0 };
    }
    
    /**
     * 导出配置
     * @param {string} format - 导出格式 (json, yaml)
     * @returns {string} 配置字符串
     */
    export(format = 'json') {
        const config = this.getAll();
        
        if (format === 'json') {
            return JSON.stringify(config, null, 2);
        } else if (format === 'yaml') {
            // 简单的YAML转换
            return this._toYaml(config);
        } else {
            throw new Error(`不支持的导出格式: ${format}`);
        }
    }
    
    /**
     * 转换为YAML格式
     * @param {object} obj - 对象
     * @param {number} indent - 缩进
     * @returns {string} YAML字符串
     */
    _toYaml(obj, indent = 0) {
        const spaces = '  '.repeat(indent);
        let yaml = '';
        
        for (const [key, value] of Object.entries(obj)) {
            if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
                yaml += `${spaces}${key}:\n${this._toYaml(value, indent + 1)}`;
            } else if (Array.isArray(value)) {
                yaml += `${spaces}${key}:\n`;
                value.forEach(item => {
                    yaml += `${spaces}  - ${JSON.stringify(item)}\n`;
                });
            } else {
                yaml += `${spaces}${key}: ${JSON.stringify(value)}\n`;
            }
        }
        
        return yaml;
    }
    
    /**
     * 重置为默认配置
     */
    resetToDefaults() {
        this.overrides = {};
        this.theme = 'light';
        this.language = 'zh-CN';
        this.saveToLocalStorage();
        this.applyTheme();
        this.applyLanguage();
    }
}

// 创建全局配置管理器实例
const configManager = new ConfigManager();

// 导出配置
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { FrontendConfig, ConfigManager, configManager };
} else {
    // 浏览器环境
    window.FrontendConfig = FrontendConfig;
    window.ConfigManager = ConfigManager;
    window.configManager = configManager;
}
