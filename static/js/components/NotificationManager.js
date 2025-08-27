/**
 * 通知管理器组件
 * 管理应用中的所有通知消息
 */

class NotificationManager {
    constructor(options = {}) {
        this.options = {
            position: 'top-right',
            autoHide: true,
            autoHideDelay: 5000,
            maxNotifications: 5,
            animation: 'slide',
            sound: false,
            desktop: false,
            ...options
        };
        
        this.notifications = [];
        this.container = null;
        this.init();
    }
    
    /**
     * 初始化通知管理器
     */
    init() {
        this.createContainer();
        this.bindEvents();
        this.loadFromLocalStorage();
    }
    
    /**
     * 创建通知容器
     */
    createContainer() {
        // 检查是否已存在容器
        this.container = document.getElementById('notification-container');
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'notification-container';
            this.container.className = `notification-container notification-${this.options.position}`;
            document.body.appendChild(this.container);
        }
        
        // 应用样式
        this.applyStyles();
    }
    
    /**
     * 应用容器样式
     */
    applyStyles() {
        const styles = `
            .notification-container {
                position: fixed;
                z-index: var(--z-toast);
                pointer-events: none;
                max-width: 400px;
                width: 100%;
            }
            
            .notification-container.notification-top-right {
                top: 20px;
                right: 20px;
            }
            
            .notification-container.notification-top-left {
                top: 20px;
                left: 20px;
            }
            
            .notification-container.notification-bottom-right {
                bottom: 20px;
                right: 20px;
            }
            
            .notification-container.notification-bottom-left {
                bottom: 20px;
                left: 20px;
            }
            
            .notification {
                background: var(--background-color);
                border: 1px solid var(--border-color);
                border-radius: var(--border-radius-md);
                box-shadow: var(--shadow-md);
                margin-bottom: 10px;
                padding: 16px;
                pointer-events: auto;
                position: relative;
                transition: all var(--transition-normal);
                max-width: 100%;
                word-wrap: break-word;
            }
            
            .notification.success {
                border-left: 4px solid var(--success-color);
                background: var(--success-light);
            }
            
            .notification.warning {
                border-left: 4px solid var(--warning-color);
                background: var(--warning-light);
            }
            
            .notification.error {
                border-left: 4px solid var(--error-color);
                background: var(--error-light);
            }
            
            .notification.info {
                border-left: 4px solid var(--info-color);
                background: var(--info-light);
            }
            
            .notification-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 8px;
            }
            
            .notification-title {
                font-weight: var(--font-weight-semibold);
                color: var(--text-color);
                margin: 0;
                font-size: var(--font-size-sm);
            }
            
            .notification-message {
                color: var(--text-secondary);
                margin: 0;
                font-size: var(--font-size-sm);
                line-height: var(--line-height-normal);
            }
            
            .notification-close {
                background: none;
                border: none;
                color: var(--text-muted);
                cursor: pointer;
                font-size: 18px;
                padding: 0;
                width: 20px;
            }
            
            .notification-close:hover {
                color: var(--text-color);
            }
            
            .notification-progress {
                position: absolute;
                bottom: 0;
                left: 0;
                height: 3px;
                background: var(--primary-color);
                transition: width linear;
            }
            
            .notification-enter {
                opacity: 0;
                transform: translateX(100%);
            }
            
            .notification-enter-active {
                opacity: 1;
                transform: translateX(0);
            }
            
            .notification-exit {
                opacity: 1;
                transform: translateX(0);
            }
            
            .notification-exit-active {
                opacity: 0;
                transform: translateX(100%);
            }
        `;
        
        // 检查样式是否已存在
        if (!document.getElementById('notification-styles')) {
            const styleSheet = document.createElement('style');
            styleSheet.id = 'notification-styles';
            styleSheet.textContent = styles;
            document.head.appendChild(styleSheet);
        }
    }
    
    /**
     * 绑定事件
     */
    bindEvents() {
        // 点击通知关闭按钮
        this.container.addEventListener('click', (e) => {
            if (e.target.classList.contains('notification-close')) {
                const notification = e.target.closest('.notification');
                if (notification) {
                    this.remove(notification.dataset.id);
                }
            }
        });
        
        // 点击通知内容
        this.container.addEventListener('click', (e) => {
            if (e.target.classList.contains('notification') || e.target.classList.contains('notification-message')) {
                const notification = e.target.closest('.notification');
                if (notification && notification.dataset.action) {
                    this.handleAction(notification.dataset.action, notification.dataset.actionData);
                }
            }
        });
    }
    
    /**
     * 显示通知
     * @param {string} message - 通知消息
     * @param {string} type - 通知类型 (success, warning, error, info)
     * @param {object} options - 通知选项
     */
    show(message, type = 'info', options = {}) {
        const notificationOptions = {
            title: options.title || this.getDefaultTitle(type),
            message: message,
            type: type,
            duration: options.duration || this.options.autoHideDelay,
            action: options.action,
            actionData: options.actionData,
            sound: options.sound !== undefined ? options.sound : this.options.sound,
            desktop: options.desktop !== undefined ? options.desktop : this.options.desktop,
            ...options
        };
        
        // 创建通知元素
        const notification = this.createNotification(notificationOptions);
        
        // 添加到容器
        this.addNotification(notification);
        
        // 播放声音
        if (notificationOptions.sound) {
            this.playSound(type);
        }
        
        // 显示桌面通知
        if (notificationOptions.desktop) {
            this.showDesktopNotification(notificationOptions);
        }
        
        // 自动隐藏
        if (this.options.autoHide && notificationOptions.duration > 0) {
            this.autoHide(notification, notificationOptions.duration);
        }
        
        return notification.dataset.id;
    }
    
    /**
     * 创建通知元素
     * @param {object} options - 通知选项
     * @returns {HTMLElement} 通知元素
     */
    createNotification(options) {
        const notification = document.createElement('div');
        const id = this.generateId();
        
        notification.className = `notification ${options.type}`;
        notification.dataset.id = id;
        notification.dataset.type = options.type;
        
        if (options.action) {
            notification.dataset.action = options.action;
            notification.dataset.actionData = options.actionData;
            notification.style.cursor = 'pointer';
        }
        
        notification.innerHTML = `
            <div class="notification-header">
                <h4 class="notification-title">${options.title}</h4>
                <button class="notification-close" aria-label="关闭通知">&times;</button>
            </div>
            <div class="notification-message">${options.message}</div>
            ${options.duration > 0 ? '<div class="notification-progress"></div>' : ''}
        `;
        
        return notification;
    }
    
    /**
     * 添加通知到容器
     * @param {HTMLElement} notification - 通知元素
     */
    addNotification(notification) {
        // 检查最大通知数量
        if (this.notifications.length >= this.options.maxNotifications) {
            this.removeOldest();
        }
        
        // 添加到数组
        this.notifications.push({
            id: notification.dataset.id,
            element: notification,
            timestamp: Date.now()
        });
        
        // 添加到DOM
        this.container.appendChild(notification);
        
        // 触发进入动画
        requestAnimationFrame(() => {
            notification.classList.add('notification-enter-active');
        });
        
        // 启动进度条
        if (notification.querySelector('.notification-progress')) {
            this.startProgress(notification);
        }
    }
    
    /**
     * 启动进度条
     * @param {HTMLElement} notification - 通知元素
     */
    startProgress(notification) {
        const progress = notification.querySelector('.notification-progress');
        if (!progress) return;
        
        const duration = this.options.autoHideDelay;
        const startTime = Date.now();
        
        const updateProgress = () => {
            const elapsed = Date.now() - startTime;
            const progressPercent = Math.min((elapsed / duration) * 100, 100);
            
            progress.style.width = `${progressPercent}%`;
            
            if (progressPercent < 100) {
                requestAnimationFrame(updateProgress);
            }
        };
        
        requestAnimationFrame(updateProgress);
    }
    
    /**
     * 自动隐藏通知
     * @param {HTMLElement} notification - 通知元素
     * @param {number} duration - 持续时间
     */
    autoHide(notification, duration) {
        setTimeout(() => {
            this.remove(notification.dataset.id);
        }, duration);
    }
    
    /**
     * 移除通知
     * @param {string} id - 通知ID
     */
    remove(id) {
        const notificationData = this.notifications.find(n => n.id === id);
        if (!notificationData) return;
        
        const { element } = notificationData;
        
        // 触发退出动画
        element.classList.add('notification-exit-active');
        
        // 动画结束后移除
        setTimeout(() => {
            if (element.parentNode) {
                element.parentNode.removeChild(element);
            }
            
            // 从数组中移除
            this.notifications = this.notifications.filter(n => n.id !== id);
        }, 300);
    }
    
    /**
     * 移除最旧的通知
     */
    removeOldest() {
        if (this.notifications.length === 0) return;
        
        const oldest = this.notifications[0];
        this.remove(oldest.id);
    }
    
    /**
     * 清空所有通知
     */
    clear() {
        this.notifications.forEach(notification => {
            this.remove(notification.id);
        });
    }
    
    /**
     * 获取默认标题
     * @param {string} type - 通知类型
     * @returns {string} 默认标题
     */
    getDefaultTitle(type) {
        const titles = {
            success: '成功',
            warning: '警告',
            error: '错误',
            info: '信息'
        };
        
        return titles[type] || '通知';
    }
    
    /**
     * 生成唯一ID
     * @returns {string} 唯一ID
     */
    generateId() {
        return 'notification_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    /**
     * 播放声音
     * @param {string} type - 通知类型
     */
    playSound(type) {
        // 这里可以添加声音播放逻辑
        console.log(`播放${type}通知声音`);
    }
    
    /**
     * 显示桌面通知
     * @param {object} options - 通知选项
     */
    showDesktopNotification(options) {
        if (!('Notification' in window)) return;
        
        if (Notification.permission === 'granted') {
            new Notification(options.title, {
                body: options.message,
                icon: '/static/favicon.svg',
                tag: 'file-manager-notification'
            });
        } else if (Notification.permission !== 'denied') {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    this.showDesktopNotification(options);
                }
            });
        }
    }
    
    /**
     * 处理通知动作
     * @param {string} action - 动作名称
     * @param {string} actionData - 动作数据
     */
    handleAction(action, actionData) {
        // 这里可以添加动作处理逻辑
        console.log(`执行动作: ${action}`, actionData);
        
        // 触发自定义事件
        const event = new CustomEvent('notificationAction', {
            detail: { action, actionData }
        });
        document.dispatchEvent(event);
    }
    
    /**
     * 从本地存储加载配置
     */
    loadFromLocalStorage() {
        try {
            const saved = localStorage.getItem('notificationSettings');
            if (saved) {
                const settings = JSON.parse(saved);
                this.options = { ...this.options, ...settings };
            }
        } catch (error) {
            console.warn('加载通知设置失败:', error);
        }
    }
    
    /**
     * 保存配置到本地存储
     */
    saveToLocalStorage() {
        try {
            localStorage.setItem('notificationSettings', JSON.stringify(this.options));
        } catch (error) {
            console.warn('保存通知设置失败:', error);
        }
    }
    
    /**
     * 更新配置
     * @param {object} newOptions - 新配置
     */
    updateOptions(newOptions) {
        this.options = { ...this.options, ...newOptions };
        this.saveToLocalStorage();
        
        // 重新应用样式
        this.applyStyles();
    }
    
    /**
     * 获取通知统计
     * @returns {object} 统计信息
     */
    getStats() {
        const now = Date.now();
        const stats = {
            total: this.notifications.length,
            byType: {},
            oldest: null,
            newest: null
        };
        
        this.notifications.forEach(notification => {
            const type = notification.element.dataset.type;
            stats.byType[type] = (stats.byType[type] || 0) + 1;
            
            if (!stats.oldest || notification.timestamp < stats.oldest) {
                stats.oldest = notification.timestamp;
            }
            
            if (!stats.newest || notification.timestamp > stats.newest) {
                stats.newest = notification.timestamp;
            }
        });
        
        return stats;
    }
}

// 创建全局通知管理器实例
const notificationManager = new NotificationManager();

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { NotificationManager, notificationManager };
} else {
    window.NotificationManager = NotificationManager;
    window.notificationManager = notificationManager;
}
