import asyncio
from datetime import datetime

from bs4 import BeautifulSoup
from playwright.async_api import expect

from cookies_handler import load_cookies
from markdowner import profile_to_markdown
from profile_scraper import ProfileScraper


async def scrape_tweets(page, url, proxies, folder_path, with_replies):
    async_name = asyncio.current_task().get_name()

    if with_replies:
        url += "/with_replies"
    print(f"{async_name} ->", "=" * 60)
    print(f"{async_name} -> 开始爬取 {url}")
    await page.goto(url)

    EXPECTED_SCROLL_COUNT = 999
    for scroll_count in range(1, EXPECTED_SCROLL_COUNT):
        await expect(page.locator('article').nth(0)).to_be_visible(timeout=100000)

        article_count = await page.locator('article').count()

        for index in range(article_count):
            print(f"{async_name} ->", "=" * 60)
            print(f"{async_name} -> 第 {scroll_count} 次滚动，正在获取推文...({index + 1}/{article_count})")

            article = page.locator("article").first

            if scroll_count >= 88:
                soup = BeautifulSoup(await article.inner_html(), "lxml")

                try:
                    if 'style="text-overflow: unset;">Ad</span>' in str(soup):
                        raise ValueError("遇到广告，跳过")

                    time_element = soup.find("time")
                    publish_time = time_element.get("datetime")
                    publish_url = "https://x.com" + time_element.find_parent().get("href")

                    author = soup.find("div", attrs={"data-testid": "User-Name"}).find_all('span')[0].get_text()
                    author += soup.find("div", attrs={"data-testid": "User-Name"}).find_all('span')[-2].get_text()

                    tweet_text = soup.find("div", attrs={"data-testid": "tweetText"})
                    publish_content = tweet_text.get_text() if tweet_text else ""

                    tweet_photo = soup.find("div", attrs={"data-testid": "tweetPhoto"})
                    publish_images = [img.get("src") for img in tweet_photo.find_all("img")] if tweet_photo else []

                    print(f"{async_name} ->", "发布时间：",
                          datetime.strptime(publish_time, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y年%m月%d日 %H:%M:%S"))
                    print(f"{async_name} ->", "发布者：", author)
                    print(f"{async_name} ->", "推文地址：", publish_url)
                    print(f"{async_name} ->", "推文内容：", publish_content)
                    print(f"{async_name} ->", "推文图片：", publish_images)

                except ValueError as e:
                    print(f"{async_name} -> 第 {scroll_count} 次滚动，({index + 1}/{article_count}) 推文获取出错：", str(e))

            await article.locator("xpath=../../..").first.evaluate("(element) => element.remove()")

            await asyncio.sleep(1)


async def twitter_to_markdown(context, url, proxies, with_replies):
    asyncio.current_task().set_name(url.split('/')[-1])
    async_name = asyncio.current_task().get_name()
    print(f"任务名称：{async_name}")

    await load_cookies(context)
    page = await context.new_page()
    await page.goto(url)

    # profile_scraper = ProfileScraper()
    # profile = await profile_scraper.scrape_profile(page, url)
    # print(f"基本信息收集：{profile}")
    # folder_path = profile_to_markdown(profile)

    folder_path = None
    await scrape_tweets(page, url, proxies, folder_path, with_replies)
