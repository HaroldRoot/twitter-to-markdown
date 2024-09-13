import json
from pathlib import Path


def normalize_cookies(cookies):
    for cookie in cookies:
        cookie['sameSite'] = {'strict': 'Strict', 'lax': 'Lax', 'none': 'None'}.get(cookie.get('sameSite'), None)
        if cookie['sameSite'] not in ['Strict', 'Lax', 'None']:
            del cookie['sameSite']
    return cookies


async def save_cookies(context, file_path="cookies.json"):
    cookies = await context.cookies()
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(cookies, f, ensure_ascii=False, indent=4)
    print(f"Cookies 已成功保存到 {file_path}")


async def load_cookies(context, file_path="cookies.json"):
    if Path(file_path).exists():
        with open(file_path, "r", encoding="utf-8") as f:
            cookies = json.load(f)
        cookies = normalize_cookies(cookies)
        await context.add_cookies(cookies)
        print(f"Cookies 已加载到浏览器 context 中")
    else:
        print(f"Cookie 文件 {file_path} 不存在，无法加载")
