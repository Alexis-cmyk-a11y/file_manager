/**
 * 分块上传UI组件
 * 提供分块上传的用户界面和交互
 */

class ChunkedUploadUI {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            maxFileSize: 100 * 1024 * 1024, // 100MB 默认最大文件大小
            allowedTypes: [], // 空数组表示允许所有类型
            showProgress: true,
            showDetails: true,
            autoStart: true,
            ...options
        };
        
        this.uploader = null;
        this.currentUpload = null;
        
        this.init();
    }
    
    init() {
        this.createUI();
        this.bindEvents();
    }
    
    createUI() {
        this.container.innerHTML = `
            <div class="chunked-upload-container">
                <div class="upload-header">
                    <h3><i class="fas fa-cloud-upload-alt"></i> 大文件上传</h3>
                    <p>支持断点续传，适合上传大文件</p>
                </div>
                
                <div class="upload-area" id="upload-area">
                    <div class="upload-dropzone" id="upload-dropzone">
                        <div class="dropzone-content">
                            <i class="fas fa-cloud-upload-alt"></i>
                            <h4>拖拽文件到此处或点击选择</h4>
                            <p>支持大文件上传，自动分块处理</p>
                            <button type="button" class="btn-select-file" id="select-file-btn">
                                <i class="fas fa-folder-open"></i> 选择文件
                            </button>
                        </div>
                    </div>
                    
                    <input type="file" id="file-input" style="display: none;" />
                </div>
                
                <div class="upload-progress" id="upload-progress" style="display: none;">
                    <div class="progress-header">
                        <div class="file-info">
                            <span class="filename" id="upload-filename"></span>
                            <span class="file-size" id="upload-filesize"></span>
                        </div>
                        <div class="progress-controls">
                            <button type="button" class="btn-pause" id="pause-btn" style="display: none;">
                                <i class="fas fa-pause"></i> 暂停
                            </button>
                            <button type="button" class="btn-resume" id="resume-btn" style="display: none;">
                                <i class="fas fa-play"></i> 继续
                            </button>
                            <button type="button" class="btn-cancel" id="cancel-btn">
                                <i class="fas fa-times"></i> 取消
                            </button>
                        </div>
                    </div>
                    
                    <div class="progress-bar-container">
                        <div class="progress-bar">
                            <div class="progress-fill" id="progress-fill"></div>
                        </div>
                    </div>
                    
                    <div class="upload-details" id="upload-details">
                        <div class="detail-item">
                            <span class="label">上传速度:</span>
                            <span class="value" id="upload-speed">计算中...</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">已上传:</span>
                            <span class="value" id="uploaded-size">0 B</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">剩余时间:</span>
                            <span class="value" id="remaining-time">计算中...</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">块进度:</span>
                            <span class="value" id="chunk-progress">0 / 0</span>
                        </div>
                    </div>
                </div>
                
                <div class="upload-result" id="upload-result" style="display: none;">
                    <div class="result-content">
                        <i class="fas fa-check-circle success-icon"></i>
                        <h4>上传完成</h4>
                        <p id="result-message"></p>
                        <button type="button" class="btn-close-result" id="close-result-btn">
                            <i class="fas fa-times"></i> 关闭
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        this.addStyles();
    }
    
    addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .chunked-upload-container {
                background: white;
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                overflow: hidden;
            }
            
            .upload-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                text-align: center;
            }
            
            .upload-header h3 {
                margin: 0 0 8px 0;
                font-size: 1.5rem;
                font-weight: 600;
            }
            
            .upload-header p {
                margin: 0;
                opacity: 0.9;
                font-size: 0.95rem;
            }
            
            .upload-area {
                padding: 30px;
            }
            
            .upload-dropzone {
                border: 2px dashed #d1d5db;
                border-radius: 8px;
                padding: 40px 20px;
                text-align: center;
                transition: all 0.3s ease;
                cursor: pointer;
            }
            
            .upload-dropzone:hover {
                border-color: #667eea;
                background-color: #f8fafc;
            }
            
            .upload-dropzone.dragover {
                border-color: #667eea;
                background-color: #eef2ff;
                transform: scale(1.02);
            }
            
            .dropzone-content i {
                font-size: 3rem;
                color: #9ca3af;
                margin-bottom: 16px;
            }
            
            .dropzone-content h4 {
                margin: 0 0 8px 0;
                color: #374151;
                font-size: 1.25rem;
                font-weight: 600;
            }
            
            .dropzone-content p {
                margin: 0 0 20px 0;
                color: #6b7280;
                font-size: 0.95rem;
            }
            
            .btn-select-file {
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .btn-select-file:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
            }
            
            .upload-progress {
                padding: 20px;
                border-top: 1px solid #e5e7eb;
            }
            
            .progress-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 16px;
            }
            
            .file-info .filename {
                font-weight: 600;
                color: #374151;
                display: block;
            }
            
            .file-info .file-size {
                color: #6b7280;
                font-size: 0.9rem;
            }
            
            .progress-controls {
                display: flex;
                gap: 8px;
            }
            
            .progress-controls button {
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            
            .btn-pause {
                background: #f59e0b;
                color: white;
            }
            
            .btn-resume {
                background: #10b981;
                color: white;
            }
            
            .btn-cancel {
                background: #ef4444;
                color: white;
            }
            
            .progress-controls button:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }
            
            .progress-bar-container {
                margin-bottom: 16px;
            }
            
            .progress-bar {
                width: 100%;
                height: 8px;
                background: #e5e7eb;
                border-radius: 4px;
                overflow: hidden;
                margin-bottom: 8px;
            }
            
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #667eea, #764ba2);
                width: 0%;
                transition: width 0.3s ease;
            }
            
            .progress-text {
                text-align: center;
                font-weight: 600;
                color: #374151;
            }
            
            .upload-details {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 12px;
                padding: 16px;
                background: #f9fafb;
                border-radius: 8px;
            }
            
            .detail-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .detail-item .label {
                color: #6b7280;
                font-size: 0.9rem;
            }
            
            .detail-item .value {
                color: #374151;
                font-weight: 600;
                font-size: 0.9rem;
            }
            
            .upload-result {
                padding: 20px;
                border-top: 1px solid #e5e7eb;
                text-align: center;
            }
            
            .result-content .success-icon {
                font-size: 3rem;
                color: #10b981;
                margin-bottom: 16px;
            }
            
            .result-content h4 {
                margin: 0 0 8px 0;
                color: #374151;
                font-size: 1.25rem;
                font-weight: 600;
            }
            
            .result-content p {
                margin: 0 0 20px 0;
                color: #6b7280;
            }
            
            .btn-close-result {
                background: #6b7280;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            
            .btn-close-result:hover {
                background: #4b5563;
            }
        `;
        document.head.appendChild(style);
    }
    
    bindEvents() {
        const dropzone = document.getElementById('upload-dropzone');
        const fileInput = document.getElementById('file-input');
        const selectBtn = document.getElementById('select-file-btn');
        const pauseBtn = document.getElementById('pause-btn');
        const resumeBtn = document.getElementById('resume-btn');
        const cancelBtn = document.getElementById('cancel-btn');
        const closeResultBtn = document.getElementById('close-result-btn');
        
        // 文件选择
        selectBtn.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', (e) => this.handleFileSelect(e.target.files[0]));
        
        // 拖拽上传
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        });
        
        dropzone.addEventListener('dragleave', () => {
            dropzone.classList.remove('dragover');
        });
        
        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
            const file = e.dataTransfer.files[0];
            if (file) this.handleFileSelect(file);
        });
        
        // 控制按钮
        pauseBtn.addEventListener('click', () => this.pauseUpload());
        resumeBtn.addEventListener('click', () => this.resumeUpload());
        cancelBtn.addEventListener('click', () => this.cancelUpload());
        closeResultBtn.addEventListener('click', () => this.closeResult());
    }
    
    handleFileSelect(file) {
        if (!file) return;
        
        // 验证文件
        if (!this.validateFile(file)) return;
        
        this.currentUpload = file;
        this.showProgress();
        this.startUpload(file);
    }
    
    validateFile(file) {
        // 检查文件大小
        if (file.size > this.options.maxFileSize) {
            showNotification(`文件大小超过限制 (${this.formatFileSize(this.options.maxFileSize)})`, 'error');
            return false;
        }
        
        // 检查文件类型
        if (this.options.allowedTypes.length > 0) {
            const fileType = file.type;
            const fileName = file.name.toLowerCase();
            const isAllowed = this.options.allowedTypes.some(type => 
                fileType.includes(type) || fileName.endsWith(type)
            );
            
            if (!isAllowed) {
                showNotification(`不支持的文件类型: ${fileType}`, 'error');
                return false;
            }
        }
        
        return true;
    }
    
    showProgress() {
        document.getElementById('upload-progress').style.display = 'block';
        document.getElementById('upload-filename').textContent = this.currentUpload.name;
        document.getElementById('upload-filesize').textContent = this.formatFileSize(this.currentUpload.size);
    }
    
    startUpload(file) {
        // 记录开始时间
        this.uploadStartTime = Date.now();
        
        this.uploader = new ChunkedUploader({
            chunkSize: 5 * 1024 * 1024, // 5MB 块大小
            maxConcurrentChunks: 3, // 并发上传3个块，提高速度
            chunkDelay: 200, // 块之间延迟200ms，大幅减少等待时间
            onProgress: (data) => {
                // 添加开始时间到进度数据
                data.startTime = this.uploadStartTime;
                this.updateProgress(data);
            },
            onComplete: (data) => this.onUploadComplete(data),
            onError: (error) => this.onUploadError(error),
            onStatusChange: (status) => this.onStatusChange(status)
        });
        
        // 获取当前目录，如果currentPath未定义则使用根目录
        const targetDirectory = (typeof currentPath !== 'undefined' && currentPath && currentPath !== '') ? currentPath : '.';
        
        this.uploader.upload(file, targetDirectory).catch(error => {
            this.onUploadError(error);
        });
    }
    
    updateProgress(data) {
        const progressFill = document.getElementById('progress-fill');
        const chunkProgress = document.getElementById('chunk-progress');
        
        if (progressFill) {
            progressFill.style.width = `${data.progress}%`;
        }
        if (chunkProgress) {
            chunkProgress.textContent = `${data.uploadedChunks} / ${data.totalChunks}`;
        }
        
        // 更新上传详情
        this.updateUploadDetails(data);
    }
    
    updateUploadDetails(data) {
        // 更新上传详情
        const uploadedSize = document.getElementById('uploaded-size');
        const uploadSpeed = document.getElementById('upload-speed');
        const remainingTime = document.getElementById('remaining-time');
        
        if (uploadedSize) {
            uploadedSize.textContent = this.formatFileSize(data.uploadedBytes || 0);
        }
        
        if (uploadSpeed && data.uploadedBytes && data.startTime) {
            const elapsed = (Date.now() - data.startTime) / 1000; // 秒
            const speed = data.uploadedBytes / elapsed; // 字节/秒
            uploadSpeed.textContent = this.formatFileSize(speed) + '/s';
            
            if (data.totalBytes && speed > 0) {
                const remaining = (data.totalBytes - data.uploadedBytes) / speed;
                remainingTime.textContent = this.formatTime(remaining);
            }
        }
    }
    
    onUploadComplete(data) {
        document.getElementById('upload-result').style.display = 'block';
        document.getElementById('result-message').textContent = 
            `文件 "${data.filename}" 上传成功！`;
        
        showNotification('文件上传完成！', 'success');
        
        // 刷新文件列表
        if (typeof loadFileList === 'function') {
            console.log('分块上传完成，准备刷新文件列表，当前路径:', typeof currentPath !== 'undefined' ? currentPath : '未定义');
            
            // 延迟一点时间确保服务器端文件已写入
            setTimeout(() => {
                console.log('延迟刷新文件列表，当前路径:', typeof currentPath !== 'undefined' ? currentPath : '未定义');
                loadFileList();
            }, 500);
        }
        
        // 延迟3秒后自动关闭模态框并刷新页面
        setTimeout(() => {
            // 关闭模态框
            const modal = document.getElementById('chunked-upload-modal');
            if (modal) {
                modal.style.display = 'none';
            }
            
            // 刷新页面以显示新上传的文件
            window.location.reload();
        }, 3000);
    }
    
    onUploadError(error) {
        console.error('上传错误:', error);
        
        // 检查是否是会话过期错误
        if (error.message && error.message.includes('上传信息不存在或已过期')) {
            console.log('检测到会话过期，将重新初始化上传');
            showNotification('上传会话已过期，请重新选择文件上传', 'warning');
            this.resetUI();
            return;
        }
        
        showNotification(`上传失败: ${error.message}`, 'error');
        this.resetUI();
    }
    
    onStatusChange(status) {
        const pauseBtn = document.getElementById('pause-btn');
        const resumeBtn = document.getElementById('resume-btn');
        
        if (status === 'paused') {
            pauseBtn.style.display = 'none';
            resumeBtn.style.display = 'inline-block';
        } else if (status === 'uploading') {
            pauseBtn.style.display = 'inline-block';
            resumeBtn.style.display = 'none';
        }
    }
    
    pauseUpload() {
        if (this.uploader) {
            this.uploader.pause();
        }
    }
    
    resumeUpload() {
        if (this.uploader) {
            this.uploader.resume();
        }
    }
    
    cancelUpload() {
        if (this.uploader) {
            this.uploader.cancel();
        }
        this.resetUI();
    }
    
    closeResult() {
        document.getElementById('upload-result').style.display = 'none';
        this.resetUI();
    }
    
    resetUI() {
        document.getElementById('upload-progress').style.display = 'none';
        document.getElementById('upload-result').style.display = 'none';
        document.getElementById('file-input').value = '';
        this.currentUpload = null;
        this.uploader = null;
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    formatTime(seconds) {
        if (seconds < 60) {
            return Math.round(seconds) + '秒';
        } else if (seconds < 3600) {
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = Math.round(seconds % 60);
            return minutes + '分' + remainingSeconds + '秒';
        } else {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            return hours + '小时' + minutes + '分';
        }
    }
    
    // 设置文件到上传器
    setFiles(files) {
        if (!files || files.length === 0) {
            console.warn('没有文件需要上传');
            return;
        }
        
        console.log('设置文件到分块上传器:', files.map(f => ({ name: f.name, size: f.size })));
        
        // 模拟文件选择事件
        const fileInput = document.getElementById('file-input');
        if (fileInput) {
            // 创建DataTransfer对象来设置文件
            const dataTransfer = new DataTransfer();
            files.forEach(file => dataTransfer.items.add(file));
            fileInput.files = dataTransfer.files;
            
            // 触发change事件
            const event = new Event('change', { bubbles: true });
            fileInput.dispatchEvent(event);
        }
    }
}

// 导出类
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChunkedUploadUI;
} else {
    window.ChunkedUploadUI = ChunkedUploadUI;
}
