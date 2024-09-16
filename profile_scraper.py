import asyncio

from bs4 import BeautifulSoup


class ProfileScraper:
    @staticmethod
    async def get_final_url(page, short_url):
        try:
            await page.goto(short_url)
            final_url = page.url
            return final_url
        except Exception as e:
            print(f"尝试扩展短链接时出错: {e}")
            print("使用短链接，放弃扩展为实际链接")
            return short_url

    @staticmethod
    async def get_text_by_xpath(page, xpath):
        try:
            text = await page.locator(xpath).inner_text()
            return text
        except Exception as e:
            print(f"获取元素 {xpath} 失败: {e}")
            return None

    async def scrape_fullname(self, page):
        fullname_xpath = ('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div/div/div/div['
                          '2]/div/div[1]/div/div[1]/div/div/span/span[1]')
        fullname = await self.get_text_by_xpath(page, fullname_xpath)
        print(f"全名: {fullname}")
        return fullname

    async def scrape_username(self, page):
        username_xpath = ('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div/div/div/div['
                          '2]/div/div/div/div[2]/div/div/div/span')
        username = await self.get_text_by_xpath(page, username_xpath)
        print(f"用户名: {username}")
        return username

    async def scrape_posts_count(self, page):
        number_of_posts_xpath = ('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[1]/div['
                                 '1]/div/div/div/div/div/div[2]/div/div')
        number_of_posts = await self.get_text_by_xpath(page, number_of_posts_xpath)
        print(f"帖子数量: {number_of_posts}")
        return number_of_posts

    async def scrape_bio(self, page):
        bio_xpath = '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div/div/div/div[3]'
        bio = await self.get_text_by_xpath(page, bio_xpath)
        if bio:
            bio_lines = bio.split("\n")
            if bio_lines and bio_lines[-1] == "翻译简介":
                bio_lines = bio_lines[:-1]
            bio_cleaned = "\n".join(bio_lines)
            print(f"简介: {bio_cleaned}")
            return bio_cleaned
        return None

    async def scrape_profile_header(self, soup, page):
        profile = {}

        user_profile_header_items = soup.find('div', attrs={'data-testid': 'UserProfileHeader_Items'})

        if user_profile_header_items:
            user_location = user_profile_header_items.find('span', attrs={'data-testid': 'UserLocation'})
            if user_location:
                print(f"位置: {user_location.text}")
                profile["user_location"] = user_location.text

            user_url = user_profile_header_items.find('a', attrs={'data-testid': 'UserUrl'})
            if user_url:
                user_href = user_url.get('href')
                print(f"短链接: {user_href}")
                final_url = await self.get_final_url(page, user_href)
                print(f"最终跳转地址: {final_url}")
                profile["user_url"] = final_url

            user_birthdate = user_profile_header_items.find('span', attrs={'data-testid': 'UserBirthday'})
            if user_birthdate:
                print(f"生日: {user_birthdate.text}")
                profile["user_birthdate"] = user_birthdate.text

            user_join_date = user_profile_header_items.find('span', attrs={'data-testid': 'UserJoinDate'})
            if user_join_date:
                print(f"注册时间: {user_join_date.text}")
                profile["user_join_date"] = user_join_date.text

        return profile

    @staticmethod
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

    @staticmethod
    async def scrape_photo(page, url):
        await page.goto(f"{url}/photo")
        photo_xpath = '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div[1]/div/div/div/div/div/img'
        photo_src = await page.locator(photo_xpath).get_attribute('src')
        print(f"头像图片 URL: {photo_src}")
        return photo_src

    async def scrape_profile(self, page, url):
        await asyncio.sleep(5)
        content = await page.content()
        soup = BeautifulSoup(content, 'lxml')

        profile = {"fullname": await self.scrape_fullname(page), "username": await self.scrape_username(page),
                   "number_of_posts": await self.scrape_posts_count(page), "bio": await self.scrape_bio(page)}

        profile_header_info = await self.scrape_profile_header(soup, page)
        profile.update(profile_header_info)

        profile["header_photo_src"] = await self.scrape_header_photo(page, url)
        profile["photo_src"] = await self.scrape_photo(page, url)

        return profile
