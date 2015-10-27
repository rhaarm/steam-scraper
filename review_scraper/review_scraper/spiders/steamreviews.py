# -*- coding: utf-8 -*-

from scrapy import Spider
from scrapy.http import TextResponse
from review_scraper.items import ReviewScraperItem

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class SteamreviewsSpider(Spider):
    name = "steamreviews"
    allowed_domains = ["store.steampowered.com"]

    def __init__(self, appid, timeout=30, *args, **kwargs):
        super(SteamreviewsSpider, self).__init__(*args, **kwargs)
        self.appid = appid
        self.timeout = int(timeout)
        self.start_urls = ('http://store.steampowered.com/app/{appid}/'.format(appid=self.appid),)
        self.driver = webdriver.Firefox()

    def __del__(self, *args, **kwargs):
        self.driver.close()
        super(SteamreviewsSpider, self).__init__(*args, **kwargs)

    def select_age(self, *args, **kwargs):
        self.driver.find_element_by_xpath("//select[@id='ageYear']/option[@value='1990']").click()
        self.driver.find_element_by_xpath("//form[@id='agecheck_form']/a").click()

    def parse(self, response):
        self.driver.get(response.url)
        if 'agecheck' in self.driver.current_url:
            self.select_age()
            time.sleep(3)
        # this changes the Javascript on the page, I found that the "Load More" button only goes back 180 days
        # so in here it is changed to go back 365 days, I would change it based on how long the app has been around
        # TODO: dynamically determine the date range to go back
        # another issue is once the JS hits the end of comments, it will display that there are no more, but there maybe
        # more in another language, so the 'english' piece to the JS function needs to be changed to iterate through other
        # supported languages in Steam.
        # TODO: dynamically iterate through all supported languages
        self.driver.execute_script(
            "document.getElementById('LoadMoreReviewsall').getElementsByTagName('a')[0].setAttribute('onclick', \"LoadMoreReviews( {appid}, 5, 365, 'all', 'english' );\")".format(
                appid=self.appid))
        while True:
            try:
                # 30 second timeout window, if the JS takes longer to load more comments, then change.
                # the Timeout also triggers for the script to break out of the loop, which could terminate your script to
                # early depending on how many comments it takes to load.
                more_btn = WebDriverWait(self.driver, self.timeout).until(
                    EC.visibility_of_element_located((By.ID, "LoadMoreReviewsall")))
                more_btn.click()
            except TimeoutException as e:
                pass
            try:
                if self.driver.find_element_by_class_name('no_more_reviews'):
                    break
            except NoSuchElementException as e:
                pass
        # take the page source and put it in a Scrapy response
        response = TextResponse(url=response.url, body=self.driver.page_source, encoding='utf8')
        return self.parse_page(response)

    def parse_page(self, response):
        # Scrapes all of the reviews from the page.
        for selector in response.xpath('//div[@class="review_box"]'):
            item = ReviewScraperItem()
            item['helpful'] = ''.join(selector.xpath('div[@class="header"]/text()').extract()).strip('\t').strip('\n')

            item['user_profile'] = \
                selector.xpath('div/div[@class="leftcol"]/div[@class="persona_name"]/a/@href').extract()[0]
            try:
                item['user_name'] = \
                    selector.xpath('div/div[@class="leftcol"]/div[@class="persona_name"]/a/text()').extract()[0]
            except IndexError:
                item['user_name'] = ''
            item['user_num_owned_games'] = \
                selector.xpath('div/div[@class="leftcol"]/div[@class="num_owned_games"]/a/text()').extract()[0]
            item['user_reviews'] = \
                selector.xpath('div/div[@class="leftcol"]/div[@class="num_reviews"]/a/text()').extract()[0]

            item['recommended'] = selector.xpath(
                'div/div[@class="rightcol"]/div[@class="vote_header"]/div[@class="title ellipsis"]/a/text()').extract()[
                0]
            item['hours_played'] = selector.xpath(
                'div/div[@class="rightcol"]/div[@class="vote_header"]/div[@class="hours ellipsis"]/text()').extract()[0]
            item['posted_date'] = \
                selector.xpath('div/div[@class="rightcol"]/div[@class="postedDate"]/text()').extract()[0]
            item['content'] = selector.xpath('div/div[@class="rightcol"]/div[@class="content"]/text()').extract()[0]
            yield item



            # ReviewContentall*/leftcol/
            #     user_profile = Field()  # persona_name/a/href
            #     user_name = Field()  # persona_name/a/text
            #     user_num_owned_games = Field()  # num_owned_games/a/text
            #     user_reviews = Field()  # num_reviews/a/text
            #
            #     # ReviewContentall*/rightcol/
            #     recommended = Field()  # vote_header/title ellipsis/a/text
            #     hours_played = Field()  # vote_header/hours ellipsis/text
            #     posted_date = Field()  # vote_header/postedDate/text
            #     content = Field()  # vote_header/content/text
            # http://store.steampowered.com//appreviews/290790?start_offset=20&day_range=180&filter=positive&language=english
