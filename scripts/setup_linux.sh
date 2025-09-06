# 设置根目录
ROOT_DIR="/data/file_manage"

# 创建目录结构
mkdir -p $ROOT_DIR/home/users
mkdir -p $ROOT_DIR/home/shared
mkdir -p $ROOT_DIR/uploads
mkdir -p $ROOT_DIR/temp
mkdir -p $ROOT_DIR/downloads

# 设置权限
chmod 755 $ROOT_DIR
chmod 755 $ROOT_DIR/home
chmod 755 $ROOT_DIR/home/users
chmod 755 $ROOT_DIR/home/shared
chmod 755 $ROOT_DIR/uploads
chmod 777 $ROOT_DIR/temp
chmod 755 $ROOT_DIR/downloads

# 创建README文件
cat > $ROOT_DIR/README.txt << 'EOF'
File Manager System Root Directory

Directory Structure:
- home/users: User personal directories
- home/shared: Shared files directory
- uploads: Upload files directory
- temp: Temporary files directory
- downloads: Download files directory
EOF

echo "Directory setup completed!"
ls -la $ROOT_DIR