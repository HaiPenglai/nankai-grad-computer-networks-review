import os
import re

def generate_github_anchor(text):
    """生成符合 GitHub 规则的锚点链接"""
    # 转小写，移除特殊字符，空格换成连字符
    anchor = text.lower().strip()
    anchor = re.sub(r'[^\w\s\-]', '', anchor)
    anchor = anchor.replace(' ', '-')
    return anchor

def update_toc(readme_path="README.md"):
    if not os.path.exists(readme_path):
        print(f"错误: 未找到 {readme_path}")
        return

    with open(readme_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    toc_list = []
    content_start_idx = -1
    
    # 1. 提取所有标题并生成 TOC 条目
    for line in lines:
        match = re.match(r'^(#{1,6})\s+(.*)', line)
        if match:
            level = len(match.group(1))
            title_text = match.group(2).strip()
            anchor = generate_github_anchor(title_text)
            # 根据层级缩进，-1是因为一级标题不缩进
            indent = "  " * (level - 1)
            toc_list.append(f"{indent}- [{title_text}](#{anchor})")

    # 2. 找到 [TOC] 的位置并更新内容
    new_content = []
    skip_old_toc = False
    found_toc_tag = False

    for line in lines:
        if "[TOC]" in line:
            new_content.append(line) # 保留 [TOC] 标识
            new_content.append("\n" + "\n".join(toc_list) + "\n\n")
            skip_old_toc = True # 开始跳过旧目录内容
            found_toc_tag = True
            continue
        
        # 如果正在跳过旧 TOC，直到遇到下一个标题或分割线才停止跳过
        if skip_old_toc:
            if line.startswith('#') or line.startswith('---'):
                skip_old_toc = False
                new_content.append(line)
            continue
        
        new_content.append(line)

    if not found_toc_tag:
        print("提示: README 中未找到 [TOC] 标识，未生成目录。")
    else:
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.writelines(new_content)
        print("成功: README 目录已更新。")

def clean_assets(assets_dir="assets"):
    if not os.path.exists(assets_dir):
        print(f"提示: 未找到 {assets_dir} 文件夹，跳过图片清理。")
        return

    # 1. 获取当前目录下所有 md 文件中引用的图片名
    referenced_images = set()
    md_files = [f for f in os.listdir('.') if f.endswith('.md') and os.path.isfile(f)]
    
    # 匹配模式：![...](...assets/filename.ext) 或 <img src="...assets/filename.ext">
    img_pattern = re.compile(r'!?\[.*?\]\(.*?assets/(.*?)\)|<img.*?src=.*?assets/(.*?)"')

    for md_file in md_files:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            matches = img_pattern.findall(content)
            for m in matches:
                # findall 返回元组，取出非空的分组
                img_name = m[0] if m[0] else m[1]
                referenced_images.add(img_name)

    # 2. 检查 assets 目录并删除未引用的文件
    all_assets = os.listdir(assets_dir)
    deleted_count = 0
    
    print(f"正在检查 assets，共有 {len(all_assets)} 个文件...")
    for asset_file in all_assets:
        if asset_file not in referenced_images:
            file_path = os.path.join(assets_dir, asset_file)
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                    print(f"已删除冗余图片: {asset_file}")
                    deleted_count += 1
                except Exception as e:
                    print(f"删除失败 {asset_file}: {e}")

    print(f"清理完成，共删除 {deleted_count} 个冗余文件。")

if __name__ == "__main__":
    print("--- 开始执行脚本 ---")
    update_toc()     # 任务1: 更新目录
    clean_assets()   # 任务2: 清理图片
    print("--- 执行完毕 ---")