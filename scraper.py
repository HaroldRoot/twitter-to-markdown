import asyncio

from bs4 import BeautifulSoup

from cookies_handler import load_cookies


async def scrape_basic_info(page, url):
    await asyncio.sleep(5)
    content = await page.content()
    soup = BeautifulSoup(content, 'lxml')
    basic_info = {}

    fullname_xpath = ('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div/div/div/div['
                      '2]/div/div[1]/div/div[1]/div/div/span/span[1]')
    fullname = await page.locator(fullname_xpath).inner_text()
    print(f"全名: {fullname}")
    basic_info["fullname"] = fullname

    username_xpath = ('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div/div/div/div['
                      '2]/div/div/div/div[2]/div/div/div/span')
    username = await page.locator(username_xpath).inner_text()
    print(f"用户名: {username}")
    basic_info["username"] = username

    number_of_posts_xpath = ('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[1]/div['
                             '1]/div/div/div/div/div/div[2]/div/div')
    number_of_posts = await page.locator(number_of_posts_xpath).inner_text()
    print(f"帖子数量: {number_of_posts}")
    basic_info["number_of_posts"] = number_of_posts

    bio_xpath = ('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div/div/div/div['
                 '3]/div/div/span')
    bio = await page.locator(bio_xpath).inner_text()
    print(f"简介: {bio}")
    basic_info["bio"] = bio

    user_profile_header_items = soup.find('div', attrs={'data-testid': 'UserProfileHeader_Items'})

    if user_profile_header_items:
        user_location = user_profile_header_items.find('span', attrs={'data-testid': 'UserLocation'})
        if user_location:
            print(f"位置: {user_location.text}")
            basic_info["user_location"] = user_location.text

        user_url = user_profile_header_items.find('a', attrs={'data-testid': 'UserUrl'})
        if user_url:
            print(f"网站: {user_url.text}")
            basic_info["user_url"] = user_url.text

        user_birthdate = user_profile_header_items.find('span', attrs={'data-testid': 'UserBirthday'})
        if user_birthdate:
            print(f"生日: {user_birthdate.text}")
            basic_info["user_birthdate"] = user_birthdate.text

        user_join_date = user_profile_header_items.find('span', attrs={'data-testid': 'UserJoinDate'})
        if user_join_date:
            print(f"加入推特的日期: {user_join_date.text}")
            basic_info["user_join_date"] = user_join_date.text

    await page.goto(f"{url}/header_photo")
    header_photo_xpath = '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div[1]/div/div/div/div/div/img'
    header_photo_src = await page.locator(header_photo_xpath).get_attribute('src')
    print(f"背景图片 URL: {header_photo_src}")
    basic_info["header_photo_src"] = header_photo_src

    await page.goto(f"{url}/photo")
    photo_xpath = '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div[1]/div/div/div/div/div/img'
    photo_src = await page.locator(photo_xpath).get_attribute('src')
    print(f"头像图片 URL: {photo_src}")
    basic_info["photo_src"] = photo_src

    return basic_info


async def scrape_tweets(context, url, proxies):
    async_name = asyncio.current_task().get_name()
    await load_cookies(context)
    page = await context.new_page()
    await page.goto(url)
    print(async_name)
    basic_info = await scrape_basic_info(page, url)
    print(basic_info)


async def twitter_to_markdown(context, url, proxies):
    await scrape_tweets(context, url, proxies)
