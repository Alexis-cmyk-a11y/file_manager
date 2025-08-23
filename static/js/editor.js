/**
 * 在线编辑器核心功能
 * 基于CodeMirror实现
 */

class FileEditor {
    constructor() {
        this.editor = null;
        this.currentFile = null;
        this.isModified = false;
        this.originalContent = '';
        this.searchQuery = null;
        this.searchResults = [];
        this.currentSearchIndex = -1;
        this.searchTimeout = null; // 搜索防抖超时
        this._clearSearchTimeout = null; // 清除搜索高亮的超时
        
        // 撤销/重做系统
        this.undoStack = [];
        this.redoStack = [];
        this.maxHistorySize = 100; // 最大历史记录数量
        this.isUndoRedoAction = false; // 防止撤销/重做操作触发新的历史记录
        this.lastUndoRedoTime = 0; // 记录最后一次撤销/重做操作时间
        this.undoRedoNotificationThreshold = 2000; // 撤销/重做通知间隔阈值(毫秒)
        this.showUndoRedoNotifications = true; // 是否显示撤销/重做通知
        
        this.init();
    }
    
    init() {
        this.loadUserPreferences(); // 加载用户偏好设置
        this.setupEventListeners();
        this.initializeEditor();
        this.loadFileFromURL();
        this.hideLoadingIndicator();
    }
    
    setupEventListeners() {
        // 返回按钮
        document.getElementById('back-btn').addEventListener('click', () => {
            this.handleBack();
        });
        
        // 保存按钮
        document.getElementById('save-btn').addEventListener('click', () => {
            this.saveFile();
        });
        
        // 撤销/重做按钮
        document.getElementById('undo-btn').addEventListener('click', () => {
            this.undo();
        });
        
        document.getElementById('redo-btn').addEventListener('click', () => {
            this.redo();
        });
        
        // 全屏按钮和主题选择器已移除
        
        // 搜索相关按钮
        document.getElementById('search-btn').addEventListener('click', () => {
            this.toggleSearchPanel();
        });
        
        document.getElementById('replace-btn').addEventListener('click', () => {
            this.toggleReplacePanel();
        });
        
        document.getElementById('goto-line-btn').addEventListener('click', () => {
            this.showGotoLineModal();
        });
        
        // 搜索面板事件
        document.getElementById('search-input').addEventListener('input', (e) => {
            this.handleSearchInput(e.target.value);
        });
        
        // 搜索输入框回车键处理
        document.getElementById('search-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                e.stopPropagation(); // 阻止事件冒泡到编辑器
                
                // 确保搜索输入框保持焦点
                document.getElementById('search-input').focus();
                
                // 如果已经有搜索结果且搜索内容没有变化，则切换到下一个匹配项
                if (this.searchResults.length > 0 && this.searchQuery === document.getElementById('search-input').value.trim()) {
                    this.searchNext();
                } else {
                    // 否则执行新的搜索
                    this.performSafeSearch();
                }
            }
        });
        
        document.getElementById('search-next').addEventListener('click', () => {
            this.searchNext();
        });
        
        document.getElementById('search-prev').addEventListener('click', () => {
            this.searchPrevious();
        });
        
        document.getElementById('close-search').addEventListener('click', () => {
            this.hideSearchPanel();
        });
        
        // 替换相关事件
        document.getElementById('replace-btn-single').addEventListener('click', () => {
            this.replaceCurrent();
        });
        
        document.getElementById('replace-btn-all').addEventListener('click', () => {
            this.replaceAll();
        });
        
        // 跳转行模态框事件
        document.getElementById('confirm-goto-btn').addEventListener('click', () => {
            this.gotoLine();
        });
        
        document.getElementById('cancel-goto-btn').addEventListener('click', () => {
            this.hideModal('goto-line-modal');
        });
        
        // 确认保存模态框事件
        document.getElementById('confirm-save-btn').addEventListener('click', () => {
            this.saveFile();
            this.hideModal('save-confirm-modal');
        });
        
        document.getElementById('discard-save-btn').addEventListener('click', () => {
            this.discardChanges();
            this.hideModal('save-confirm-modal');
        });
        
        document.getElementById('cancel-save-btn').addEventListener('click', () => {
            this.hideModal('save-confirm-modal');
        });
        
        // 键盘快捷键
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });
        
        // 页面卸载前确认
        window.addEventListener('beforeunload', (e) => {
            if (this.isModified) {
                e.preventDefault();
                e.returnValue = '文件已修改，确定要离开吗？';
                return e.returnValue;
            }
        });
        
        // 当用户点击编辑器时，清除搜索高亮
        document.addEventListener('click', (e) => {
            const editorElement = document.getElementById('code-editor');
            const searchPanel = document.getElementById('search-panel');
            
            // 如果点击的是编辑器区域而不是搜索面板，清除搜索高亮
            if (editorElement && editorElement.contains(e.target) && 
                (!searchPanel || !searchPanel.contains(e.target))) {
                if (this.searchResults.length > 0) {
                    this.clearSearchHighlight();
                    this.searchResults = [];
                    this.currentSearchIndex = -1;
                    this.updateSearchStatus();
                }
            }
        });
        
        // 当搜索面板失去焦点时，延迟隐藏
        document.addEventListener('focusout', (e) => {
            const searchPanel = document.getElementById('search-panel');
            if (searchPanel && !searchPanel.contains(e.target) && 
                !searchPanel.contains(e.relatedTarget)) {
                // 延迟隐藏，给用户时间切换到其他搜索相关元素
                setTimeout(() => {
                    if (!searchPanel.contains(document.activeElement)) {
                        this.hideSearchPanel();
                    }
                }, 200);
            }
        });
    }
    
    initializeEditor() {
        const editorElement = document.getElementById('code-editor');
        
        // 尝试使用最简单的CodeMirror 6初始化方式
        try {
            // 直接创建编辑器，不指定复杂配置
            this.editor = new CodeMirror(editorElement, {
                value: "",
                mode: "text/plain",
                lineNumbers: true,
                theme: "default"
            });
            
            console.log('编辑器初始化成功');
        } catch (error) {
            console.error('编辑器初始化失败:', error);
            
            // 如果CodeMirror 6失败，尝试使用原生textarea
            try {
                editorElement.innerHTML = '<textarea id="fallback-editor" style="width:100%;height:500px;font-family:Consolas,Monaco,\'Courier New\',monospace;font-size:14px;border:none;outline:none;resize:none;padding:10px;"></textarea>';
                this.editor = null;
                console.log('已回退到原生textarea编辑器');
                
                // 为原生textarea添加内容变化监听器
                const fallbackEditor = document.getElementById('fallback-editor');
                if (fallbackEditor) {
                    // 创建监听器函数并绑定到实例
                    this._handleInputChange = () => {
                        console.log('textarea input事件触发 (initializeEditor)');
                        this.handleContentChange();
                    };
                    
                    this._handleKeyUp = () => {
                        this.updateCursorPosition();
                    };
                    
                    // 添加事件监听器
                    fallbackEditor.addEventListener('input', this._handleInputChange);
                    fallbackEditor.addEventListener('keyup', this._handleKeyUp);
                    
                    console.log('已在initializeEditor中为原生textarea添加事件监听器');
                }
            } catch (fallbackError) {
                console.error('回退编辑器创建失败:', fallbackError);
            }
            return;
        }
        
        // 主题设置已移除
        
        // 为CodeMirror 5添加内容变化监听器
        if (this.editor && this.editor.on) {
            this.editor.on('change', () => {
                this.handleContentChange();
            });
        }
        
        // 初始化撤销/重做按钮状态
        this.updateUndoRedoButtons();
    }
    
    loadFileFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        const filePath = urlParams.get('file');
        
        if (filePath) {
            this.openFile(filePath);
        } else {
            this.showNotification('未指定文件路径', 'error');
        }
    }
    
    async openFile(filePath) {
        try {
            this.showLoadingIndicator();
            
            const response = await fetch('/api/editor/open', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ path: filePath })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.currentFile = {
                    path: filePath,
                    name: result.name,
                    content: result.content,
                    syntax_mode: result.syntax_mode,
                    encoding: result.encoding,
                    size: result.size,
                    line_count: result.line_count
                };
                
                this.originalContent = result.content;
                this.isModified = false;
                
                this.setEditorContent(result.content, result.syntax_mode);
                this.updateFileInfo();
                this.updateStatusBar();
                
                // 初始化撤销/重做历史记录
                this.clearHistory();
                this.addToHistory(result.content);
                
                this.showNotification(`文件 ${result.name} 加载成功`, 'success');
            } else {
                this.showNotification(result.message || '文件加载失败', 'error');
            }
        } catch (error) {
            console.error('打开文件失败:', error);
            this.showNotification('文件加载失败: ' + error.message, 'error');
        } finally {
            this.hideLoadingIndicator();
        }
    }
    
    setEditorContent(content, mode) {
        if (!this.editor) {
            // 如果编辑器初始化失败，使用fallback textarea
            const fallbackEditor = document.getElementById('fallback-editor');
            if (fallbackEditor) {
                fallbackEditor.value = content;
                
                // 确保为原生textarea添加事件监听器
                if (!fallbackEditor.hasAttribute('data-events-bound')) {
                    // 移除可能存在的旧监听器
                    fallbackEditor.removeEventListener('input', this._handleInputChange);
                    fallbackEditor.removeEventListener('keyup', this._handleKeyUp);
                    
                    // 创建新的监听器函数并绑定到实例
                    this._handleInputChange = () => {
                        console.log('textarea input事件触发');
                        this.handleContentChange();
                    };
                    
                    this._handleKeyUp = () => {
                        this.updateCursorPosition();
                    };
                    
                    // 添加事件监听器
                    fallbackEditor.addEventListener('input', this._handleInputChange);
                    fallbackEditor.addEventListener('keyup', this._handleKeyUp);
                    fallbackEditor.setAttribute('data-events-bound', 'true');
                    console.log('已为原生textarea添加事件监听器');
                    
                    // 测试事件监听器是否工作
                    setTimeout(() => {
                        console.log('测试事件监听器...');
                        fallbackEditor.dispatchEvent(new Event('input'));
                    }, 200);
                }
                
                // 立即更新状态，因为内容已经设置
                // 但首先确保原始内容已经正确设置
                setTimeout(() => {
                    this.handleContentChange();
                }, 100);
            }
            return;
        }
        
        try {
            if (this.editor && this.editor.setValue) {
                // CodeMirror 5 API
                this.editor.setValue(content);
                console.log('编辑器内容设置成功 (CodeMirror 5)');
                
                // 确保为CodeMirror 5添加change事件监听器
                if (this.editor && this.editor.on && !this.editor._changeListenerAdded) {
                    this.editor.on('change', () => {
                        this.handleContentChange();
                    });
                    this.editor._changeListenerAdded = true;
                }
            } else if (this.editor && this.editor.dispatch) {
                // CodeMirror 6 API
                this.editor.dispatch({
                    changes: {
                        from: 0,
                        to: this.editor.state.doc.length,
                        insert: content
                    }
                });
                console.log('编辑器内容设置成功 (CodeMirror 6)');
            } else {
                // 原生textarea
                const fallbackEditor = document.getElementById('fallback-editor');
                if (fallbackEditor) {
                    fallbackEditor.value = content;
                    console.log('编辑器内容设置成功 (原生textarea)');
                    
                    // 确保为原生textarea添加事件监听器
                    if (!fallbackEditor.hasAttribute('data-events-bound')) {
                        // 移除可能存在的旧监听器
                        fallbackEditor.removeEventListener('input', this._handleInputChange);
                        fallbackEditor.removeEventListener('keyup', this._handleKeyUp);
                        
                        // 创建新的监听器函数并绑定到实例
                        this._handleInputChange = () => {
                            console.log('textarea input事件触发');
                            this.handleContentChange();
                        };
                        
                        this._handleKeyUp = () => {
                            this.updateCursorPosition();
                        };
                        
                        // 添加事件监听器
                        fallbackEditor.addEventListener('input', this._handleInputChange);
                        fallbackEditor.addEventListener('keyup', this._handleKeyUp);
                        fallbackEditor.setAttribute('data-events-bound', 'true');
                        console.log('已为原生textarea添加事件监听器');
                        
                        // 测试事件监听器是否工作
                        setTimeout(() => {
                            console.log('测试事件监听器...');
                            fallbackEditor.dispatchEvent(new Event('input'));
                        }, 200);
                    }
                    
                    // 立即更新状态，因为内容已经设置
                    // 但首先确保原始内容已经正确设置
                    setTimeout(() => {
                        this.handleContentChange();
                    }, 100);
                }
            }
            
            // 设置语法模式（如果支持）
            if (mode && mode !== 'text' && this.editor && this.editor.setOption) {
                try {
                    this.editor.setOption('mode', mode);
                    console.log(`设置语法模式: ${mode}`);
                } catch (modeError) {
                    console.warn(`无法设置语法模式 ${mode}:`, modeError);
                }
            }
        } catch (error) {
            console.error('设置编辑器内容失败:', error);
            // 回退到fallback textarea
            const fallbackEditor = document.getElementById('fallback-editor');
            if (fallbackEditor) {
                fallbackEditor.value = content;
                console.log('回退到原生textarea设置内容');
            }
        }
    }
    
    updateFileInfo() {
        if (this.currentFile) {
            document.getElementById('file-name').textContent = this.currentFile.name;
            document.getElementById('file-path').textContent = this.currentFile.path;
            document.getElementById('file-encoding').textContent = `编码: ${this.currentFile.encoding}`;
            document.getElementById('file-size').textContent = `大小: ${this.formatFileSize(this.currentFile.size)}`;
            document.getElementById('line-count').textContent = `行数: ${this.currentFile.line_count}`;
        }
    }
    
    updateStatusBar() {
        document.getElementById('status-message').textContent = this.isModified ? '已修改' : '就绪';
        document.getElementById('last-saved').textContent = this.isModified ? '最后保存: 未保存' : '最后保存: 刚刚';
    }
    
    updateCursorPosition() {
        try {
            if (this.editor && this.editor.getCursor) {
                // CodeMirror 5 API
                const cursor = this.editor.getCursor();
                document.getElementById('cursor-position').textContent = `行: ${cursor.line + 1}, 列: ${cursor.ch + 1}`;
            } else if (this.editor && this.editor.state && this.editor.state.selection) {
                // CodeMirror 6 API
                const cursor = this.editor.state.selection.main.head;
                const line = this.editor.state.doc.lineAt(cursor);
                document.getElementById('cursor-position').textContent = `行: ${line.number}, 列: ${cursor - line.from + 1}`;
            } else {
                // 原生textarea
                const fallbackEditor = document.getElementById('fallback-editor');
                if (fallbackEditor) {
                    const text = fallbackEditor.value;
                    const cursorPos = fallbackEditor.selectionStart;
                    const lines = text.substring(0, cursorPos).split('\n');
                    const line = lines.length;
                    const col = lines[lines.length - 1].length + 1;
                    document.getElementById('cursor-position').textContent = `行: ${line}, 列: ${col}`;
                }
            }
        } catch (error) {
            console.warn('更新光标位置失败:', error);
        }
    }
    
    async saveFile() {
        if (!this.currentFile) {
            this.showNotification('没有打开的文件', 'warning');
            return;
        }
        
        if (!this.isModified) {
            this.showNotification('文件未修改', 'info');
            return;
        }
        
        try {
            this.showLoadingIndicator();
            
            let content = '';
            
            if (this.editor && this.editor.getValue) {
                // CodeMirror 5 API
                content = this.editor.getValue();
            } else if (this.editor && this.editor.state && this.editor.state.doc) {
                // CodeMirror 6 API
                content = this.editor.state.doc.toString();
            } else {
                // 原生textarea
                const fallbackEditor = document.getElementById('fallback-editor');
                if (fallbackEditor) {
                    content = fallbackEditor.value;
                }
            }
            
            const response = await fetch('/api/editor/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    path: this.currentFile.path,
                    content: content
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.originalContent = content;
                this.isModified = false;
                this.updateStatusBar();
                this.updateFileInfo();
                
                // 保存成功后，将当前内容作为新的历史记录起点
                this.clearHistory();
                this.addToHistory(content);
                
                this.showNotification('文件保存成功', 'success');
            } else {
                this.showNotification(result.message || '文件保存失败', 'error');
            }
        } catch (error) {
            console.error('保存文件失败:', error);
            this.showNotification('文件保存失败: ' + error.message, 'error');
        } finally {
            this.hideLoadingIndicator();
        }
    }
    
    handleContentChange() {
        let currentContent = '';
        
        if (this.editor && this.editor.getValue) {
            // CodeMirror 5 API
            currentContent = this.editor.getValue();
        } else if (this.editor && this.editor.state && this.editor.state.doc) {
            // CodeMirror 6 API
            currentContent = this.editor.state.doc.toString();
        } else {
            // 原生textarea
            const fallbackEditor = document.getElementById('fallback-editor');
            if (fallbackEditor) {
                currentContent = fallbackEditor.value;
            }
        }
        
        // 比较内容是否发生变化
        this.isModified = currentContent !== this.originalContent;
        
        // 如果不是撤销/重做操作，则添加到历史记录
        if (!this.isUndoRedoAction) {
            this.addToHistory(currentContent);
        }
        
        // 如果编辑器内容发生变化且不是搜索操作，清除搜索高亮
        if (!this.isUndoRedoAction && this.searchResults.length > 0) {
            // 延迟清除，避免在快速输入时频繁清除
            if (this._clearSearchTimeout) {
                clearTimeout(this._clearSearchTimeout);
            }
            this._clearSearchTimeout = setTimeout(() => {
                this.clearSearchHighlight();
                this.searchResults = [];
                this.currentSearchIndex = -1;
                this.updateSearchStatus();
            }, 1000); // 1秒后清除搜索高亮
        }
        
        // 更新状态栏
        this.updateStatusBar();
    }
    
    toggleSearchPanel() {
        const searchPanel = document.getElementById('search-panel');
        const replaceControls = document.getElementById('replace-controls');
        
        if (searchPanel.classList.contains('hidden')) {
            searchPanel.classList.remove('hidden');
            const searchInput = document.getElementById('search-input');
            if (searchInput) {
                // 清除之前的搜索状态
                this.clearSearchHighlight();
                this.searchResults = [];
                this.currentSearchIndex = -1;
                this.updateSearchStatus();
                
                searchInput.focus();
                searchInput.select(); // 选中现有内容
                
                // 添加搜索输入框的视觉反馈
                searchInput.style.boxShadow = '0 0 5px rgba(76, 175, 80, 0.3)';
                searchInput.style.transition = 'all 0.3s ease';
            }
            replaceControls.classList.add('hidden');
            
            // 移除搜索面板打开通知，减少干扰
        } else {
            this.hideSearchPanel();
        }
    }
    
    toggleReplacePanel() {
        const searchPanel = document.getElementById('search-panel');
        const replaceControls = document.getElementById('replace-controls');
        
        if (searchPanel.classList.contains('hidden')) {
            searchPanel.classList.remove('hidden');
            replaceControls.classList.remove('hidden');
        } else if (replaceControls.classList.contains('hidden')) {
            replaceControls.classList.remove('hidden');
        } else {
            replaceControls.classList.add('hidden');
        }
        
        if (!searchPanel.classList.contains('hidden')) {
            document.getElementById('search-input').focus();
        }
    }
    
    hideSearchPanel() {
        document.getElementById('search-panel').classList.add('hidden');
        this.clearSearchHighlight();
    }
    
    handleSearchInput(query) {
        // 防止重复搜索相同内容
        if (this.searchQuery === query) {
            return;
        }
        
        this.searchQuery = query;
        if (query.length > 0) {
            // 增加防抖时间，避免在用户输入过程中频繁搜索
            if (this.searchTimeout) {
                clearTimeout(this.searchTimeout);
            }
            this.searchTimeout = setTimeout(() => {
                // 只有当搜索框仍然有焦点时才执行搜索
                const searchInput = document.getElementById('search-input');
                if (searchInput && document.activeElement === searchInput) {
                    this.performSearch();
                }
            }, 800); // 增加到800ms，给用户更多输入时间
        } else {
            this.clearSearchHighlight();
            this.searchResults = [];
            this.currentSearchIndex = -1;
            this.updateSearchStatus();
        }
    }
    
    // 转义搜索字符串中的特殊字符
    escapeSearchString(str) {
        return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
    
    // 执行安全的搜索
    performSafeSearch() {
        console.log('performSafeSearch 被调用，searchQuery:', this.searchQuery);
        if (!this.searchQuery) {
            console.log('searchQuery 为空，返回');
            return;
        }
        
        try {
            console.log('开始执行搜索...');
            this.performSearch();
            
            // 搜索完成后，确保搜索输入框保持焦点
            setTimeout(() => {
                document.getElementById('search-input').focus();
            }, 100);
        } catch (error) {
            console.error('搜索出错:', error);
            this.showNotification('搜索出错，请检查搜索内容', 'error');
        }
    }
    
    performSearch() {
        if (!this.searchQuery) return;
        
        try {
            // 获取编辑器内容，兼容所有编辑器类型
            const content = this.getCurrentContent();
            if (!content || content.length === 0) {
                this.showNotification('编辑器内容为空', 'warning');
                return;
            }
            
            const searchTerm = this.searchQuery;
            const caseSensitive = document.getElementById('case-sensitive').checked;
            
            this.searchResults = [];
            let index = 0;
            
            if (caseSensitive) {
                while ((index = content.indexOf(searchTerm, index)) !== -1) {
                    this.searchResults.push(index);
                    index += searchTerm.length;
                }
            } else {
                const lowerContent = content.toLowerCase();
                const lowerSearchTerm = searchTerm.toLowerCase();
                while ((index = lowerContent.indexOf(lowerSearchTerm, index)) !== -1) {
                    this.searchResults.push(index);
                    index += searchTerm.length;
                }
            }
            
            // 保留关键调试信息，减少日志输出
            console.log('搜索结果数量:', this.searchResults.length);
            
            this.currentSearchIndex = this.searchResults.length > 0 ? 0 : -1;
            this.highlightSearchResults();
            this.updateSearchStatus();
            
            // 只在没有搜索结果时显示通知，有结果时静默处理
            if (this.searchResults.length === 0) {
                this.showNotification('未找到匹配项', 'info');
            }
        } catch (error) {
            console.error('搜索执行失败:', error);
            this.showNotification('搜索执行失败: ' + error.message, 'error');
        }
    }
    
    highlightSearchResults() {
        this.clearSearchHighlight();
        
        if (this.searchResults.length === 0) {
            return;
        }
        
        // 确保当前搜索索引正确设置
        if (this.currentSearchIndex < 0 && this.searchResults.length > 0) {
            this.currentSearchIndex = 0;
        }
        
        // 调试完成，移除详细日志
        
        // 一次性构建包含所有高亮的内容
        this.buildHighlightedContent();
        
        // 移除自动跳转，只高亮显示，不跳转
        // 用户可以通过上下箭头按钮手动导航
        
        this.updateSearchStatus();
    }
    
        clearSearchHighlight() {
        // 清除所有搜索高亮
        const highlights = document.querySelectorAll('.search-highlight, .current-search-highlight');
        highlights.forEach(highlight => {
            if (highlight.parentNode) {
                highlight.parentNode.replaceChild(
                    document.createTextNode(highlight.textContent),
                    highlight
                );
            }
        });
        
        // 清除 CodeMirror 5 高亮
        this.clearCodeMirror5Highlight();
        
        // 清除 CodeMirror 6 高亮
        this.clearCodeMirror6Highlight();
        
        // 隐藏高亮容器
        const highlightContainer = document.getElementById('highlight-container');
        if (highlightContainer) {
            highlightContainer.style.display = 'none';
            highlightContainer.innerHTML = '';
        }
        
        this.updateSearchStatus();
    }
    
    // 清除 CodeMirror 5 高亮
    clearCodeMirror5Highlight() {
        if (this._cm5Markers && this._cm5Markers.length > 0) {
            this._cm5Markers.forEach(marker => {
                try {
                    marker.clear();
                } catch (error) {
                    console.warn('清除CodeMirror 5标记失败:', error);
                }
            });
            this._cm5Markers = [];
        }
    }
    
    // 清除 CodeMirror 6 高亮
    clearCodeMirror6Highlight() {
        if (this.editor && this.editor.dispatch) {
            try {
                // 清除存储的装饰引用
                if (this._cm6Decorations) {
                    this._cm6Decorations = [];
                }
                
                // 重新加载编辑器状态来清除装饰
                const currentContent = this.editor.state.doc.toString();
                this.editor.dispatch({
                    changes: {
                        from: 0,
                        to: this.editor.state.doc.length,
                        insert: currentContent
                    }
                });
            } catch (error) {
                console.warn('清除CodeMirror 6装饰失败:', error);
            }
        }
    }
    
    // 构建包含所有高亮的内容
    buildHighlightedContent() {
        if (!this.searchQuery || this.searchResults.length === 0) return;
        
        // 构建高亮内容
        
        try {
            if (this.editor && this.editor.addOverlay) {
                // CodeMirror 5 高亮
                this.buildCodeMirror5Highlight();
            } else if (this.editor && this.editor.dispatch) {
                // CodeMirror 6 高亮
                this.buildCodeMirror6Highlight();
            } else {
                // 原生textarea高亮
                this.buildTextareaHighlight();
            }
        } catch (error) {
            console.warn('构建高亮内容失败:', error);
        }
    }
    
    // 高亮单个搜索结果（保留用于兼容性）
    highlightSearchResult(index, isCurrent = false) {
        // 这个方法现在主要用于单个高亮操作
        if (!this.searchQuery) return;
        
        try {
            if (this.editor && this.editor.addOverlay) {
                // CodeMirror 5 高亮
                this.highlightCodeMirror5(index, isCurrent);
            } else if (this.editor && this.editor.dispatch) {
                // CodeMirror 6 高亮
                this.highlightCodeMirror6(index, isCurrent);
            } else {
                // 原生textarea高亮
                this.highlightTextarea(index, isCurrent);
            }
        } catch (error) {
            console.warn('高亮搜索结果失败:', error);
        }
    }
    
    // CodeMirror 5 高亮
    highlightCodeMirror5(index, isCurrent) {
        if (!this.editor || !this.editor.addOverlay) return;
        
        try {
            // 创建高亮标记
            const searchTerm = this.searchQuery;
            const content = this.editor.getValue();
            const beforeText = content.substring(0, index);
            const lines = beforeText.split('\n');
            const lineNumber = lines.length - 1;
            const columnNumber = lines[lines.length - 1].length;
            
            // 使用 CodeMirror 5 的标记功能
            const marker = this.editor.markText(
                {line: lineNumber, ch: columnNumber},
                {line: lineNumber, ch: columnNumber + searchTerm.length},
                {
                    className: isCurrent ? 'current-search-highlight' : 'search-highlight',
                    css: isCurrent ? 'background-color: rgba(255, 87, 34, 0.8) !important; color: white !important;' : 'background-color: rgba(255, 255, 0, 0.6) !important; color: black !important;'
                }
            );
            
            // 标记创建完成
            
            // 存储标记引用以便后续清除
            if (!this._cm5Markers) this._cm5Markers = [];
            this._cm5Markers.push(marker);
            
        } catch (error) {
            console.warn('CodeMirror 5 高亮失败:', error);
        }
    }
    
    // CodeMirror 6 高亮
    highlightCodeMirror6(index, isCurrent) {
        if (!this.editor || !this.editor.dispatch) return;
        
        try {
            // 创建高亮标记
            const searchTerm = this.searchQuery;
            const content = this.editor.state.doc.toString();
            const beforeText = content.substring(0, index);
            const lines = beforeText.split('\n');
            const lineNumber = lines.length - 1;
            const columnNumber = lines[lines.length - 1].length;
            
            // 使用 CodeMirror 6 的装饰功能
            const from = this.editor.state.doc.line(lineNumber + 1).from + columnNumber;
            const to = from + searchTerm.length;
            
            // 创建装饰
            const decoration = Decoration.mark({
                class: isCurrent ? 'current-search-highlight' : 'search-highlight'
            }).range(from, to);
            
            // 存储装饰引用以便后续清除
            if (!this._cm6Decorations) this._cm6Decorations = [];
            this._cm6Decorations.push(decoration);
            
            // 应用装饰
            this.editor.dispatch({
                effects: StateEffect.appendConfig.of([
                    ViewPlugin.fromClass(class {
                        constructor(view) {
                            this.decorations = Decoration.set([decoration]);
                        }
                        update(update) {
                            if (update.docChanged) {
                                this.decorations = this.decorations.map(update.changes);
                            }
                        }
                    }, {
                        decorations: v => v.decorations
                    })
                ])
            });
            
        } catch (error) {
            console.warn('CodeMirror 6 高亮失败:', error);
        }
    }
    
    // 原生textarea高亮
    highlightTextarea(index, isCurrent) {
        const fallbackEditor = document.getElementById('fallback-editor');
        if (!fallbackEditor) return;
        
        // 创建高亮元素
        const content = fallbackEditor.value;
        const searchTerm = this.searchQuery;
        
        // 构建高亮后的内容
        const beforeText = content.substring(0, index);
        const searchText = content.substring(index, index + searchTerm.length);
        const afterText = content.substring(index + searchTerm.length);
        
        const highlightClass = isCurrent ? 'current-search-highlight' : 'search-highlight';
        const highlightedContent = beforeText + 
                                 `<span class="${highlightClass}">${searchText}</span>` + 
                                 afterText;
        
        // 创建临时显示区域
        this.showTextareaHighlight(highlightedContent);
    }
    
    // 构建CodeMirror 5高亮
    buildCodeMirror5Highlight() {
        if (!this.editor || !this.editor.addOverlay) return;
        
        try {
            // 清除之前的高亮
            this.clearCodeMirror5Highlight();
            
            // 为每个搜索结果添加高亮
            this.searchResults.forEach((index, i) => {
                // 修复：i 是数组索引，currentSearchIndex 也是数组索引，所以直接比较
                const isCurrent = (i === this.currentSearchIndex);
                // 高亮处理
                this.highlightCodeMirror5(index, isCurrent);
            });
            
        } catch (error) {
            console.warn('构建CodeMirror 5高亮失败:', error);
        }
    }
    
    // 构建CodeMirror 6高亮
    buildCodeMirror6Highlight() {
        if (!this.editor || !this.editor.dispatch) return;
        
        try {
            // 清除之前的高亮
            this.clearCodeMirror6Highlight();
            
            // 为每个搜索结果添加高亮
            this.searchResults.forEach((index, i) => {
                // 修复：i 是数组索引，currentSearchIndex 也是数组索引，所以直接比较
                const isCurrent = (i === this.currentSearchIndex);
                // 高亮处理
                this.highlightCodeMirror6(index, isCurrent);
            });
            
        } catch (error) {
            console.warn('构建CodeMirror 6高亮失败:', error);
        }
    }
    
    // 构建textarea高亮
    buildTextareaHighlight() {
        const fallbackEditor = document.getElementById('fallback-editor');
        if (!fallbackEditor) return;
        
        const content = fallbackEditor.value;
        const searchTerm = this.searchQuery;
        
        if (!content || !searchTerm) return;
        
        // 按位置排序搜索结果，确保高亮顺序正确
        const sortedResults = [...this.searchResults].sort((a, b) => a - b);
        
        let highlightedContent = '';
        let lastIndex = 0;
        
        // 遍历所有搜索结果，构建高亮内容
        sortedResults.forEach((index, i) => {
            // 修复：需要找到这个index在原始searchResults数组中的位置
            const originalIndex = this.searchResults.indexOf(index);
            const isCurrent = (originalIndex === this.currentSearchIndex);
            
            // 添加当前位置之前的内容
            highlightedContent += content.substring(lastIndex, index);
            
            // 添加高亮的搜索文本
            const searchText = content.substring(index, index + searchTerm.length);
            const highlightClass = isCurrent ? 'current-search-highlight' : 'search-highlight';
            highlightedContent += `<span class="${highlightClass}">${searchText}</span>`;
            
            lastIndex = index + searchTerm.length;
        });
        
        // 添加剩余内容
        highlightedContent += content.substring(lastIndex);
        
        // 显示高亮内容
        this.showTextareaHighlight(highlightedContent);
    }
    
    // 显示textarea高亮内容
    showTextareaHighlight(highlightedContent) {
        const fallbackEditor = document.getElementById('fallback-editor');
        if (!fallbackEditor) return;
        
        // 创建高亮显示区域
        let highlightContainer = document.getElementById('highlight-container');
        if (!highlightContainer) {
            highlightContainer = document.createElement('div');
            highlightContainer.id = 'highlight-container';
            highlightContainer.style.cssText = `
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                pointer-events: none;
                white-space: pre-wrap;
                font-family: inherit;
                font-size: inherit;
                line-height: inherit;
                padding: inherit;
                border: inherit;
                background: transparent;
                z-index: 1;
                overflow: hidden;
                user-select: none;
            `;
            fallbackEditor.parentNode.style.position = 'relative';
            fallbackEditor.parentNode.appendChild(highlightContainer);
        }
        
        // 设置高亮内容
        highlightContainer.innerHTML = highlightedContent;
        
        // 同步滚动
        highlightContainer.scrollTop = fallbackEditor.scrollTop;
        highlightContainer.scrollLeft = fallbackEditor.scrollLeft;
        
        // 监听滚动事件同步
        if (!fallbackEditor._scrollListener) {
            fallbackEditor._scrollListener = () => {
                highlightContainer.scrollTop = fallbackEditor.scrollTop;
                highlightContainer.scrollLeft = fallbackEditor.scrollLeft;
            };
            fallbackEditor.addEventListener('scroll', fallbackEditor._scrollListener);
        }
        
        // 确保高亮容器可见
        highlightContainer.style.display = 'block';
    }
    
    // 高亮当前搜索结果
    highlightCurrentSearchResult(index) {
        if (!this.searchQuery) return;
        
        // 获取编辑器内容
        const content = this.getCurrentContent();
        const searchTerm = this.searchQuery;
        
        // 计算行号和列号（仅用于显示位置信息，不跳转）
        const beforeText = content.substring(0, index);
        const lines = beforeText.split('\n');
        const lineNumber = lines.length - 1;
        const columnNumber = lines[lines.length - 1].length;
        
        // 移除自动跳转，只更新状态信息
        // this.scrollToPosition(lineNumber, columnNumber);
        
        // 可以在这里显示位置信息，但不跳转
        console.log(`当前匹配项位置: 第${lineNumber + 1}行，第${columnNumber + 1}列`);
    }
    
    // 滚动到指定位置
    scrollToPosition(lineNumber, columnNumber) {
        try {
            if (this.editor && this.editor.setCursor) {
                // CodeMirror 5 API
                this.editor.setCursor(lineNumber, columnNumber);
                this.editor.focus();
            } else if (this.editor && this.editor.dispatch) {
                // CodeMirror 6 API
                const line = this.editor.state.doc.line(lineNumber + 1);
                if (line) {
                    const pos = Math.min(line.from + columnNumber, line.to);
                    this.editor.dispatch({
                        selection: { anchor: pos, head: pos }
                    });
                    this.editor.focus();
                }
            } else {
                // 原生textarea
                const fallbackEditor = document.getElementById('fallback-editor');
                if (fallbackEditor) {
                    // 计算字符位置
                    const content = fallbackEditor.value;
                    const lines = content.split('\n');
                    let charPos = 0;
                    
                    for (let i = 0; i < lineNumber; i++) {
                        charPos += lines[i].length + 1; // +1 for newline
                    }
                    charPos += columnNumber;
                    
                    fallbackEditor.setSelectionRange(charPos, charPos);
                    fallbackEditor.focus();
                    
                    // 滚动到可见位置
                    const lineHeight = 20; // 估算行高
                    const visibleLines = Math.floor(fallbackEditor.clientHeight / lineHeight);
                    const scrollTop = Math.max(0, (lineNumber - visibleLines / 2) * lineHeight);
                    fallbackEditor.scrollTop = scrollTop;
                }
            }
        } catch (error) {
            console.warn('滚动到指定位置失败:', error);
        }
    }
    
    searchNext() {
        if (this.searchResults.length === 0) return;
        
        this.currentSearchIndex = (this.currentSearchIndex + 1) % this.searchResults.length;
        this.highlightSearchResults();
        this.updateSearchStatus();
        this.scrollToSearchResult(); // 恢复切换时的滚动
        
        // 确保搜索输入框保持焦点，防止编辑器捕获键盘事件
        setTimeout(() => {
            document.getElementById('search-input').focus();
        }, 100);
    }
    
    searchPrevious() {
        if (this.searchResults.length === 0) return;
        
        this.currentSearchIndex = this.currentSearchIndex <= 0 ? this.searchResults.length - 1 : this.currentSearchIndex - 1;
        this.highlightSearchResults();
        this.updateSearchStatus();
        this.scrollToSearchResult(); // 恢复切换时的滚动
        
        // 确保搜索输入框保持焦点，防止编辑器捕获键盘事件
        setTimeout(() => {
            document.getElementById('search-input').focus();
        }, 100);
    }
    
    scrollToSearchResult() {
        if (this.currentSearchIndex >= 0 && this.currentSearchIndex < this.searchResults.length) {
            const currentIndex = this.searchResults[this.currentSearchIndex];
            const content = this.getCurrentContent();
            const beforeText = content.substring(0, currentIndex);
            const lines = beforeText.split('\n');
            const lineNumber = lines.length - 1;
            const columnNumber = lines[lines.length - 1].length;
            
            // 滚动到搜索结果位置
            this.scrollToPosition(lineNumber, columnNumber);
            
            // 移除导航通知，减少干扰
        }
    }
    
    updateSearchStatus() {
        const searchInput = document.getElementById('search-input');
        const searchStatus = document.getElementById('search-status');
        const searchNextBtn = document.getElementById('search-next');
        const searchPrevBtn = document.getElementById('search-prev');
        
        if (this.searchResults.length > 0) {
            const status = `${this.currentSearchIndex + 1} / ${this.searchResults.length}`;
            if (searchInput) {
                searchInput.setAttribute('data-status', status);
                searchInput.placeholder = `搜索 (${status})`;
                searchInput.style.borderColor = '#4CAF50';
            }
            if (searchStatus) {
                searchStatus.textContent = status;
                searchStatus.style.display = 'inline';
                searchStatus.style.color = '#4CAF50';
            }
            
            // 启用导航按钮
            if (searchNextBtn) searchNextBtn.disabled = false;
            if (searchPrevBtn) searchPrevBtn.disabled = false;
            
            // 显示搜索结果位置信息
            this.showSearchLocationInfo();
        } else {
            if (searchInput) {
                searchInput.removeAttribute('data-status');
                searchInput.placeholder = '搜索...';
                searchInput.style.borderColor = '';
            }
            if (searchStatus) {
                searchStatus.style.display = 'none';
            }
            
            // 禁用导航按钮
            if (searchNextBtn) searchNextBtn.disabled = true;
            if (searchPrevBtn) searchPrevBtn.disabled = true;
        }
    }
    
    // 显示搜索结果位置信息
    showSearchLocationInfo() {
        if (this.searchResults.length === 0) return;
        
        const currentIndex = this.searchResults[this.currentSearchIndex];
        const content = this.getCurrentContent();
        const beforeText = content.substring(0, currentIndex);
        const lines = beforeText.split('\n');
        const lineNumber = lines.length;
        const columnNumber = lines[lines.length - 1].length + 1;
        
        // 在状态栏显示位置信息
        const statusElement = document.getElementById('search-location-status');
        if (statusElement) {
            statusElement.textContent = `位置: 第${lineNumber}行，第${columnNumber}列`;
            statusElement.style.display = 'inline';
        }
    }
    
    // 替换后更新搜索结果位置
    updateSearchResultsAfterReplace(replaceIndex, oldLength, newLength) {
        const lengthDiff = newLength - oldLength;
        
        // 更新后续搜索结果的位置
        for (let i = this.currentSearchIndex + 1; i < this.searchResults.length; i++) {
            if (this.searchResults[i] > replaceIndex) {
                this.searchResults[i] += lengthDiff;
            }
        }
        
        // 移除已替换的搜索结果
        this.searchResults.splice(this.currentSearchIndex, 1);
        
        // 调整当前搜索索引
        if (this.currentSearchIndex >= this.searchResults.length) {
            this.currentSearchIndex = this.searchResults.length - 1;
        }
        
        this.updateSearchStatus();
    }
    
    replaceCurrent() {
        if (this.currentSearchIndex < 0 || this.currentSearchIndex >= this.searchResults.length) {
            this.showNotification('没有选中的搜索结果', 'warning');
            return;
        }
        
        const replaceText = document.getElementById('replace-input').value;
        const searchText = this.searchQuery;
        
        if (!searchText || !replaceText) {
            this.showNotification('请输入搜索和替换内容', 'warning');
            return;
        }
        
        // 获取当前内容
        const currentContent = this.getCurrentContent();
        const searchIndex = this.searchResults[this.currentSearchIndex];
        
        // 执行替换
        const newContent = currentContent.substring(0, searchIndex) + 
                          replaceText + 
                          currentContent.substring(searchIndex + searchText.length);
        
        // 更新编辑器内容
        this.setContentWithoutHistory(newContent);
        
        // 更新搜索结果位置（因为内容长度可能改变）
        this.updateSearchResultsAfterReplace(searchIndex, searchText.length, replaceText.length);
        
        // 移动到下一个搜索结果
        this.searchNext();
        
        this.showNotification('已替换当前匹配项', 'success');
    }
    
    replaceAll() {
        const replaceText = document.getElementById('replace-input').value;
        const searchText = this.searchQuery;
        
        if (!searchText || !replaceText) {
            this.showNotification('请输入搜索和替换内容', 'warning');
            return;
        }
        
        // 获取当前内容
        const currentContent = this.getCurrentContent();
        
        // 执行全局替换（普通字符串替换）
        let newContent = currentContent;
        let replaceCount = 0;
        
        // 手动计算替换次数和执行替换
        const searchTextLower = searchText.toLowerCase();
        const contentLower = currentContent.toLowerCase();
        let index = 0;
        
        while ((index = contentLower.indexOf(searchTextLower, index)) !== -1) {
            replaceCount++;
            index += searchTextLower.length;
        }
        
        // 执行替换
        newContent = currentContent.split(searchText).join(replaceText);
        
        if (replaceCount === 0) {
            this.showNotification('未找到匹配项', 'info');
            return;
        }
        
        // 更新编辑器内容
        this.setContentWithoutHistory(newContent);
        
        // 清空搜索结果（因为内容已经改变）
        this.searchResults = [];
        this.currentSearchIndex = -1;
        this.updateSearchStatus();
        
        this.showNotification(`已替换 ${replaceCount} 处`, 'success');
        this.hideSearchPanel();
    }
    
    showGotoLineModal() {
        // 获取当前行数信息
        let maxLines = 1;
        let currentLine = 1;
        
        try {
            if (this.editor && this.editor.setCursor) {
                // CodeMirror 5 API
                maxLines = this.editor.lineCount();
                const cursor = this.editor.getCursor();
                currentLine = cursor.line + 1;
            } else if (this.editor && this.editor.state && this.editor.state.doc) {
                // CodeMirror 6 API
                maxLines = this.editor.state.doc.lines;
                const cursor = this.editor.state.selection.main.head;
                const line = this.editor.state.doc.lineAt(cursor);
                currentLine = line.number;
            } else {
                // 原生textarea
                const fallbackEditor = document.getElementById('fallback-editor');
                if (fallbackEditor) {
                    const content = fallbackEditor.value;
                    const lines = content.split('\n');
                    maxLines = lines.length;
                    
                    // 计算当前行号
                    const cursorPos = fallbackEditor.selectionStart;
                    const beforeText = content.substring(0, cursorPos);
                    const currentLines = beforeText.split('\n');
                    currentLine = currentLines.length;
                }
            }
        } catch (error) {
            console.warn('获取行数信息失败:', error);
        }
        
        // 显示模态框
        this.showModal('goto-line-modal');
        
        // 设置输入框的占位符和最大值
        const input = document.getElementById('goto-line-input');
        input.placeholder = `当前第${currentLine}行，共${maxLines}行`;
        input.max = maxLines;
        input.min = 1;
        
        // 预填入当前行号
        input.value = currentLine;
        input.select();
        input.focus();
        
        // 添加回车键支持
        input.onkeydown = (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.gotoLine();
            } else if (e.key === 'Escape') {
                e.preventDefault();
                this.hideModal('goto-line-modal');
            }
        };
    }
    
    gotoLine() {
        const lineNumber = parseInt(document.getElementById('goto-line-input').value);
        if (isNaN(lineNumber) || lineNumber < 1) {
            this.showNotification('请输入有效的行号', 'error');
            return;
        }
        
        try {
            if (this.editor && this.editor.setCursor) {
                // CodeMirror 5 API
                const maxLines = this.editor.lineCount();
                if (lineNumber > maxLines) {
                    this.showNotification(`行号超出范围 (1-${maxLines})`, 'error');
                    return;
                }
                
                // 跳转到指定行，列设为0（行首）
                this.editor.setCursor(lineNumber - 1, 0);
                this.editor.focus();
                
            } else if (this.editor && this.editor.state && this.editor.state.doc) {
                // CodeMirror 6 API
                const maxLines = this.editor.state.doc.lines;
                if (lineNumber > maxLines) {
                    this.showNotification(`行号超出范围 (1-${maxLines})`, 'error');
                    return;
                }
                
                const line = this.editor.state.doc.line(lineNumber);
                this.editor.dispatch({
                    selection: { anchor: line.from, head: line.from }
                });
                this.editor.focus();
                
            } else {
                // 原生textarea
                const fallbackEditor = document.getElementById('fallback-editor');
                if (fallbackEditor) {
                    const content = fallbackEditor.value;
                    const lines = content.split('\n');
                    const maxLines = lines.length;
                    
                    if (lineNumber > maxLines) {
                        this.showNotification(`行号超出范围 (1-${maxLines})`, 'error');
                        return;
                    }
                    
                    // 计算目标行的字符位置
                    let charPos = 0;
                    for (let i = 0; i < lineNumber - 1; i++) {
                        charPos += lines[i].length + 1; // +1 for newline
                    }
                    
                    // 设置光标位置并聚焦
                    fallbackEditor.setSelectionRange(charPos, charPos);
                    fallbackEditor.focus();
                    
                    // 滚动到可见位置
                    const lineHeight = 20; // 估算行高
                    const visibleLines = Math.floor(fallbackEditor.clientHeight / lineHeight);
                    const scrollTop = Math.max(0, (lineNumber - 1 - visibleLines / 2) * lineHeight);
                    fallbackEditor.scrollTop = scrollTop;
                } else {
                    this.showNotification('编辑器未准备好', 'warning');
                    return;
                }
            }
            
            this.hideModal('goto-line-modal');
            this.showNotification(`已跳转到第 ${lineNumber} 行`, 'success');
            
        } catch (error) {
            console.error('跳转行失败:', error);
            this.showNotification('跳转行失败: ' + error.message, 'error');
        }
    }
    
    // changeTheme函数已移除
    
    // toggleFullscreen函数已移除
    
    handleKeyboardShortcuts(e) {
        // Ctrl+S 保存
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            this.saveFile();
        }
        
        // Ctrl+Z 撤销
        if (e.ctrlKey && e.key === 'z') {
            e.preventDefault();
            this.undo();
        }
        
        // Ctrl+Y 重做
        if (e.ctrlKey && e.key === 'y') {
            e.preventDefault();
            this.redo();
        }
        
        // Ctrl+F 搜索
        if (e.ctrlKey && e.key === 'f') {
            e.preventDefault();
            this.toggleSearchPanel();
        }
        
        // Ctrl+H 替换
        if (e.ctrlKey && e.key === 'h') {
            e.preventDefault();
            this.toggleReplacePanel();
        }
        
        // Ctrl+G 跳转行
        if (e.ctrlKey && e.key === 'g') {
            e.preventDefault();
            this.showGotoLineModal();
        }
        
        // F11 全屏功能已移除
        
        // Escape 隐藏搜索面板
        if (e.key === 'Escape') {
            this.hideSearchPanel();
        }
        
        // Ctrl+Shift+N 切换撤销/重做通知
        if (e.ctrlKey && e.shiftKey && e.key === 'N') {
            e.preventDefault();
            this.toggleUndoRedoNotifications();
        }
    }
    
    handleBack() {
        if (this.isModified) {
            this.showSaveConfirmModal();
        } else {
            this.goBack();
        }
    }
    
    showSaveConfirmModal() {
        this.showModal('save-confirm-modal');
    }
    
    discardChanges() {
        if (this.editor && this.editor.state && this.editor.state.doc) {
            try {
                this.editor.dispatch({
                    changes: {
                        from: 0,
                        to: this.editor.state.doc.length,
                        insert: this.originalContent
                    }
                });
            } catch (error) {
                console.warn('丢弃更改失败:', error);
            }
        }
        this.isModified = false;
        this.updateStatusBar();
        this.goBack();
    }
    
    goBack() {
        // 返回文件管理器
        window.location.href = '/';
    }
    
    showModal(modalId) {
        document.getElementById(modalId).style.display = 'block';
        document.getElementById('overlay').classList.add('active');
    }
    
    hideModal(modalId) {
        document.getElementById(modalId).style.display = 'none';
        document.getElementById('overlay').classList.remove('active');
    }
    
    showNotification(message, type = 'info') {
        const container = document.getElementById('notification-container');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        container.appendChild(notification);
        
        // 自动移除通知
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }
    
    showLoadingIndicator() {
        document.getElementById('loading-indicator').classList.remove('hidden');
    }
    
    hideLoadingIndicator() {
        document.getElementById('loading-indicator').classList.add('hidden');
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // 撤销/重做系统方法
    addToHistory(content) {
        // 如果内容没有变化，不添加到历史记录
        if (this.undoStack.length > 0 && this.undoStack[this.undoStack.length - 1] === content) {
            return;
        }
        
        // 添加到撤销栈
        this.undoStack.push(content);
        
        // 限制历史记录大小
        if (this.undoStack.length > this.maxHistorySize) {
            this.undoStack.shift();
        }
        
        // 清空重做栈（因为有了新的操作）
        this.redoStack = [];
        
        // 更新按钮状态
        this.updateUndoRedoButtons();
    }
    
    undo() {
        if (this.undoStack.length <= 1) {
            this.showNotification('没有可撤销的操作', 'info');
            return;
        }
        
        // 获取当前内容
        const currentContent = this.getCurrentContent();
        
        // 从撤销栈中移除当前内容
        this.undoStack.pop();
        
        // 获取上一个内容
        const previousContent = this.undoStack[this.undoStack.length - 1];
        
        // 添加到重做栈
        this.redoStack.push(currentContent);
        
        // 设置标志，防止触发新的历史记录
        this.isUndoRedoAction = true;
        
        // 恢复内容
        this.setContentWithoutHistory(previousContent);
        
        // 重置标志
        this.isUndoRedoAction = false;
        
        // 更新按钮状态
        this.updateUndoRedoButtons();
        
        // 智能通知：只在间隔足够长时显示通知
        this.showSmartUndoRedoNotification('已撤销');
    }
    
    redo() {
        if (this.redoStack.length === 0) {
            this.showNotification('没有可重做的操作', 'info');
            return;
        }
        
        // 获取当前内容
        const currentContent = this.getCurrentContent();
        
        // 从重做栈中获取下一个内容
        const nextContent = this.redoStack.pop();
        
        // 将当前内容添加到撤销栈
        this.undoStack.push(currentContent);
        
        // 设置标志，防止触发新的历史记录
        this.isUndoRedoAction = true;
        
        // 恢复内容
        this.setContentWithoutHistory(nextContent);
        
        // 重置标志
        this.isUndoRedoAction = false;
        
        // 更新按钮状态
        this.updateUndoRedoButtons();
        
        // 智能通知：只在间隔足够长时显示通知
        this.showSmartUndoRedoNotification('已重做');
    }
    
    getCurrentContent() {
        try {
            if (this.editor && this.editor.getValue) {
                // CodeMirror 5 API
                return this.editor.getValue() || '';
            } else if (this.editor && this.editor.state && this.editor.state.doc) {
                // CodeMirror 6 API
                return this.editor.state.doc.toString() || '';
            } else {
                // 原生textarea
                const fallbackEditor = document.getElementById('fallback-editor');
                if (fallbackEditor) {
                    return fallbackEditor.value || '';
                }
            }
            return '';
        } catch (error) {
            console.error('获取编辑器内容失败:', error);
            return '';
        }
    }
    
    setContentWithoutHistory(content) {
        if (this.editor && this.editor.setValue) {
            // CodeMirror 5 API
            this.editor.setValue(content);
        } else if (this.editor && this.editor.dispatch) {
            // CodeMirror 6 API
            this.editor.dispatch({
                changes: {
                    from: 0,
                    to: this.editor.state.doc.length,
                    insert: content
                }
            });
        } else {
            // 原生textarea
            const fallbackEditor = document.getElementById('fallback-editor');
            if (fallbackEditor) {
                fallbackEditor.value = content;
            }
        }
        
        // 手动触发内容变化检测
        this.handleContentChange();
    }
    
    updateUndoRedoButtons() {
        const undoBtn = document.getElementById('undo-btn');
        const redoBtn = document.getElementById('redo-btn');
        
        // 更新撤销按钮状态
        if (undoBtn) {
            undoBtn.disabled = this.undoStack.length <= 1;
            undoBtn.title = this.undoStack.length <= 1 ? '没有可撤销的操作' : '撤销 (Ctrl+Z)';
        }
        
        // 更新重做按钮状态
        if (redoBtn) {
            redoBtn.disabled = this.redoStack.length === 0;
            redoBtn.title = this.redoStack.length === 0 ? '没有可重做的操作' : '重做 (Ctrl+Y)';
        }
    }
    
    clearHistory() {
        this.undoStack = [];
        this.redoStack = [];
        this.updateUndoRedoButtons();
    }
    
    // 智能撤销/重做通知系统
    showSmartUndoRedoNotification(message) {
        // 如果关闭了撤销/重做通知，则不显示
        if (!this.showUndoRedoNotifications) {
            return;
        }
        
        const now = Date.now();
        
        // 如果距离上次撤销/重做操作时间太短，则不显示通知
        if (now - this.lastUndoRedoTime < this.undoRedoNotificationThreshold) {
            return;
        }
        
        // 更新最后操作时间
        this.lastUndoRedoTime = now;
        
        // 显示通知
        this.showNotification(message, 'success');
    }
    
    // 批量撤销/重做操作（用于连续操作）
    batchUndoRedo(operations) {
        let hasChanges = false;
        
        operations.forEach(op => {
            if (op.type === 'undo' && this.undoStack.length > 1) {
                this.undo();
                hasChanges = true;
            } else if (op.type === 'redo' && this.redoStack.length > 0) {
                this.redo();
                hasChanges = true;
            }
        });
        
        // 批量操作完成后只显示一次通知
        if (hasChanges) {
            this.showNotification('批量操作完成', 'success');
        }
    }
    
    // 切换撤销/重做通知开关
    toggleUndoRedoNotifications() {
        this.showUndoRedoNotifications = !this.showUndoRedoNotifications;
        const status = this.showUndoRedoNotifications ? '开启' : '关闭';
        this.showNotification(`撤销/重做通知已${status}`, 'info');
        
        // 保存用户偏好到本地存储
        localStorage.setItem('showUndoRedoNotifications', this.showUndoRedoNotifications);
    }
    
    // 设置撤销/重做通知间隔
    setUndoRedoNotificationThreshold(threshold) {
        this.undoRedoNotificationThreshold = Math.max(0, threshold);
        this.showNotification(`通知间隔已设置为 ${this.undoRedoNotificationThreshold}ms`, 'info');
        
        // 保存用户偏好到本地存储
        localStorage.setItem('undoRedoNotificationThreshold', this.undoRedoNotificationThreshold);
    }
    
    // 从本地存储加载用户偏好
    loadUserPreferences() {
        const savedNotifications = localStorage.getItem('showUndoRedoNotifications');
        if (savedNotifications !== null) {
            this.showUndoRedoNotifications = savedNotifications === 'true';
        }
        
        const savedThreshold = localStorage.getItem('undoRedoNotificationThreshold');
        if (savedThreshold !== null) {
            this.undoRedoNotificationThreshold = parseInt(savedThreshold);
        }
    }
}

// 页面加载完成后初始化编辑器
document.addEventListener('DOMContentLoaded', () => {
    new FileEditor();
});

// 添加搜索高亮样式
const style = document.createElement('style');
style.textContent = `
    .search-highlight {
        background-color: rgba(255, 255, 0, 0.4) !important;
        border-radius: 3px;
        padding: 2px 4px;
        margin: 1px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        border: 1px solid rgba(255, 193, 7, 0.5);
    }
    
    .current-search-highlight {
        background-color: rgba(255, 87, 34, 0.8) !important;
        border-radius: 3px;
        padding: 2px 4px;
        margin: 1px 0;
        box-shadow: 0 2px 6px rgba(255, 87, 34, 0.4);
        border: 2px solid rgba(255, 87, 34, 0.9);
        font-weight: bold;
        color: white;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3);
    }
    
    .search-panel {
        transition: all 0.3s ease;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .search-panel.hidden {
        opacity: 0;
        transform: translateY(-10px);
        pointer-events: none;
    }
    
    #search-input {
        transition: all 0.3s ease;
        border: 2px solid #ddd;
        border-radius: 6px;
    }
    
    #search-input:focus {
        border-color: #4CAF50;
        box-shadow: 0 0 8px rgba(76, 175, 80, 0.3);
    }
    
    #search-input[data-status] {
        border-color: #4CAF50;
        background-color: rgba(76, 175, 80, 0.05);
    }
    
    .search-navigation-btn {
        transition: all 0.2s ease;
        border-radius: 6px;
        border: 1px solid #ddd;
    }
    
    .search-navigation-btn:hover:not(:disabled) {
        background-color: #f0f0f0;
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .search-navigation-btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
    
    #search-status {
        background-color: #4CAF50;
        color: white;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
        margin-left: 10px;
    }
    
    #search-location-status {
        background-color: #2196F3;
        color: white;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 11px;
        margin-left: 10px;
    }
    
    .highlight-container {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        pointer-events: none;
        white-space: pre-wrap;
        font-family: inherit;
        font-size: inherit;
        line-height: inherit;
        padding: inherit;
        border: inherit;
        background: transparent;
        z-index: 1;
        overflow: hidden;
    }
`;
document.head.appendChild(style);
