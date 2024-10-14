import os
import glob
from pathlib import Path

def rename_images():
    # 支持的图片格式
    image_extensions = ('*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp')
    
    # 获取所有图片文件
    image_files = []
    for ext in image_extensions:
        image_files.extend(glob.glob(ext))
    
    if not image_files:
        print("当前目录未找到任何图片文件！")
        return
    
    # 确保不会超过20个文件
    if len(image_files) > 20:
        print(f"警告：当前目录包含 {len(image_files)} 个图片文件，将只处理前20个。")
        image_files = image_files[:20]
    
    # 排序文件以确保重命名的一致性
    image_files.sort()
    
    # 创建临时文件名，避免重命名冲突
    temp_names = {}
    for i, old_name in enumerate(image_files, 1):
        ext = Path(old_name).suffix
        temp_name = f"temp_{i}{ext}"
        temp_names[old_name] = temp_name
    
    # 第一轮：重命名为临时文件名
    for old_name, temp_name in temp_names.items():
        os.rename(old_name, temp_name)
    
    # 第二轮：重命名为最终的数字名称
    for i, (old_name, temp_name) in enumerate(temp_names.items(), 1):
        ext = Path(old_name).suffix
        new_name = f"{i}{ext}"
        os.rename(temp_name, new_name)
        print(f"已重命名：{old_name} -> {new_name}")

if __name__ == "__main__":
    print("开始重命名图片...")
    rename_images()
    print("重命名完成！")