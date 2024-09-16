import asyncio
from datetime import datetime

from bs4 import BeautifulSoup
from playwright.async_api import expect

from cookies_handler import load_cookies
from markdowner import basic_info_to_markdown


async def get_final_url(page, short_url):
    try:
        await page.goto(short_url)
        final_url = page.url
        return final_url
    except Exception as e:
        print(f"尝试扩展短链接时出错: {e}")
        print("使用短链接，放弃扩展为实际链接")
        return short_url


async def get_text_by_xpath(page, xpath):
    try:
        text = await page.locator(xpath).inner_text()
        return text
    except Exception as e:
        print(f"获取元素 {xpath} 失败: {e}")
        return None


async def scrape_fullname(page):
    fullname_xpath = ('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div/div/div/div['
                      '2]/div/div[1]/div/div[1]/div/div/span/span[1]')
    fullname = await get_text_by_xpath(page, fullname_xpath)
    print(f"全名: {fullname}")
    return fullname


async def scrape_username(page):
    username_xpath = ('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div/div/div/div['
                      '2]/div/div/div/div[2]/div/div/div/span')
    username = await get_text_by_xpath(page, username_xpath)
    print(f"用户名: {username}")
    return username


async def scrape_posts_count(page):
    number_of_posts_xpath = ('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[1]/div['
                             '1]/div/div/div/div/div/div[2]/div/div')
    number_of_posts = await get_text_by_xpath(page, number_of_posts_xpath)
    print(f"帖子数量: {number_of_posts}")
    return number_of_posts


async def scrape_bio(page):
    bio_xpath = '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div/div/div/div[3]'
    bio = await get_text_by_xpath(page, bio_xpath)
    if bio:
        bio_lines = bio.split("\n")
        if bio_lines and bio_lines[-1] == "翻译简介":
            bio_lines = bio_lines[:-1]
        bio_cleaned = "\n".join(bio_lines)
        print(f"简介: {bio_cleaned}")
        return bio_cleaned
    return None


async def scrape_profile_header(soup, page):
    basic_info = {}

    user_profile_header_items = soup.find('div', attrs={'data-testid': 'UserProfileHeader_Items'})

    if user_profile_header_items:
        user_location = user_profile_header_items.find('span', attrs={'data-testid': 'UserLocation'})
        if user_location:
            print(f"位置: {user_location.text}")
            basic_info["user_location"] = user_location.text

        user_url = user_profile_header_items.find('a', attrs={'data-testid': 'UserUrl'})
        if user_url:
            user_href = user_url.get('href')
            print(f"短链接: {user_href}")
            final_url = await get_final_url(page, user_href)
            print(f"最终跳转地址: {final_url}")
            basic_info["user_url"] = final_url

        user_birthdate = user_profile_header_items.find('span', attrs={'data-testid': 'UserBirthday'})
        if user_birthdate:
            print(f"生日: {user_birthdate.text}")
            basic_info["user_birthdate"] = user_birthdate.text

        user_join_date = user_profile_header_items.find('span', attrs={'data-testid': 'UserJoinDate'})
        if user_join_date:
            print(f"注册时间: {user_join_date.text}")
            basic_info["user_join_date"] = user_join_date.text

    return basic_info


async def scrape_header_photo(page, url):
    await page.goto(f"{url}/header_photo")
    header_photo_xpath = '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div[1]/div/div/div/div/div/img'
    try:
        header_photo_src = await page.locator(header_photo_xpath).get_attribute('src', timeout=5000)
        print(f"背景图片 URL: {header_photo_src}")
        return header_photo_src
    except Exception as e:
        print(f"寻找背景图片时超时: {e}")
        return None


async def scrape_photo(page, url):
    await page.goto(f"{url}/photo")
    photo_xpath = '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div[1]/div/div/div/div/div/img'
    photo_src = await page.locator(photo_xpath).get_attribute('src')
    print(f"头像图片 URL: {photo_src}")
    return photo_src


async def scrape_basic_info(page, url):
    await asyncio.sleep(5)
    content = await page.content()
    soup = BeautifulSoup(content, 'lxml')

    basic_info = {"fullname": await scrape_fullname(page), "username": await scrape_username(page),
                  "number_of_posts": await scrape_posts_count(page), "bio": await scrape_bio(page)}

    profile_header_info = await scrape_profile_header(soup, page)
    basic_info.update(profile_header_info)

    basic_info["header_photo_src"] = await scrape_header_photo(page, url)
    basic_info["photo_src"] = await scrape_photo(page, url)

    return basic_info


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

    basic_info = await scrape_basic_info(page, url)
    print(f"基本信息收集：{basic_info}")
    folder_path = basic_info_to_markdown(basic_info)

    # folder_path = None  # await scrape_tweets(page, url, proxies, folder_path, with_replies)
