import asyncio

from playwright.async_api import async_playwright
from rich.prompt import Prompt

from config_loader import load_config
from cookies_handler import load_cookies, save_cookies
from scraper import twitter_to_markdown


async def login_and_save_cookies(browser):
    context = await browser.new_context()
    await load_cookies(context)
    page = await context.new_page()
    home_page = 'https://x.com/home'

    try:
        await page.goto(home_page)
    except Exception as e:
        print(f"访问 {home_page} 出错：{e}")
        exit()

    if page.url == home_page:
        print("自动检测：已登录")
    else:
        Prompt.ask("请手动登录，并在完成后按回车键继续...")

    await save_cookies(context)
    return context


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await login_and_save_cookies(browser)
        config = load_config()
        proxies = {k: v for k, v in config['proxies'].items() if v}
        urls_to_scrape = config['urls_to_scrape']['urls']
        with_replies = config['with_replies']['enabled']
        tasks = [twitter_to_markdown(context, url, proxies, with_replies) for url in urls_to_scrape]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                print(f"抓取时出错: {result}")


if __name__ == '__main__':
    asyncio.run(main())
