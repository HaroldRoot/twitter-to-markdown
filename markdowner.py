from datetime import datetime
from mimetypes import guess_extension
from pathlib import Path

import requests


def save_image(url, attachments_dir: Path):
    if not url:
        return "没有图片"

    file_name = url.split("/")[-1]

    try:
        response = requests.get(url)
        response.raise_for_status()

        if '.' not in file_name:
            content_type = response.headers.get("Content-Type", "")
            extension = guess_extension(content_type) or ".jpg"
            file_name += extension

        file_path = attachments_dir / file_name

        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"下载图片成功: {file_name}")

    except requests.RequestException as e:
        print(f"下载图片出错 {url}: {e}")
        return "下载图片失败"

    return f"![[{file_name}]]"


def basic_info_to_markdown(basic_info: dict[str, str]):
    fullname = basic_info.get("fullname", "")
    username = basic_info.get("username", "")
    current_time = datetime.now().strftime("%Y%m%d%H%M")
    folder_name = f"{fullname} {username} - {current_time}"

    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    folder_path = results_dir / folder_name
    folder_path.mkdir(exist_ok=True)
    print(f"文件夹已创建: {folder_path}")

    fields = [("fullname", "全名"), ("username", "用户名"), ("number_of_posts", "帖子数量"),
              ("user_join_date", "注册时间"), ("user_birthdate", "生日"), ("user_url", "网站"),
              ("user_location", "位置")]

    table_rows = ("| Key | Value |\n"
                  "| --- | ----- |\n")

    for key, label in fields:
        value = basic_info.get(key, "")
        if value:
            table_rows += f"| {label} | {value} |\n"

    bio = "\n# 简介\n\n" + basic_info.get("bio", "") + "\n\n"

    attachments_dir = folder_path / "attachments"
    attachments_dir.mkdir(exist_ok=True)

    header_photo = "\n# 背景图片\n\n" + save_image(basic_info.get("header_photo_src", ""), attachments_dir) + "\n\n"
    photo = "\n# 头像图片\n\n" + save_image(basic_info.get("photo_src", ""), attachments_dir) + "\n\n"

    md_content = table_rows + bio + header_photo + photo

    file_path = folder_path / "基本信息.md"

    try:
        with file_path.open("w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"基本信息保存成功：{file_path}")
    except IOError as e:
        print(f"基本信息保存失败：{e}")

    return folder_path
