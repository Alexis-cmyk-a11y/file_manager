/**
 * JavaScript 演示文件
 * 展示在线编辑器的功能
 */

// 类定义
class FileEditor {
    constructor() {
        this.name = '在线编辑器';
        this.version = '2.0.0';
        this.features = [
            '语法高亮',
            '主题切换',
            '智能搜索',
            '自动保存',
            '多语言支持'
        ];
    }
    
    // 获取编辑器信息
    getInfo() {
        return {
            name: this.name,
            version: this.version,
            features: this.features
        };
    }
    
    // 搜索功能
    search(query, caseSensitive = false) {
        const flags = caseSensitive ? 'g' : 'gi';
        const regex = new RegExp(query, flags);
        return this.content.match(regex);
    }
    
    // 保存文件
    save(content) {
        console.log('保存文件:', content);
        return true;
    }
}

// 创建编辑器实例
const editor = new FileEditor();

// 显示编辑器信息
console.log('编辑器信息:', editor.getInfo());

// 演示搜索功能
const searchResults = editor.search('功能');
console.log('搜索结果:', searchResults);

// 演示保存功能
editor.save('这是新的内容');

// 导出编辑器
export default FileEditor;
