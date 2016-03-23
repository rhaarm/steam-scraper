"""
-- Name: steam_scraper/steam_scraper
-- User: RyanH
-- Date: 3/22/2016 9:10 AM
--
"""
import json
import time
from datetime import datetime

import re
import requests
from collections import namedtuple
from lxml import html
import settings

STEAMURLS = {'STORE': 'http://store.steampowered.com/app/{appid}',
             'DATA': 'http://store.steampowered.com//appreviews/{appid}'}
STEAM_INITIAL_DATE = datetime(year=2003, month=9, day=12)

browse_all_rex = re.compile('Browse all (?P<count>[\d,]+) reviews', re.IGNORECASE)


def days_since_release():
    return (datetime.utcnow() - STEAM_INITIAL_DATE).days


ReviewScraperItem = namedtuple("ReviewScraperItem",
                               ['review_url', 'helpful', 'user_profile', 'user_name', 'user_num_owned_games',
                                'user_reviews', 'recommended', 'hours_played', 'posted_date', 'content'])


class SteamReviews(object):
    def __init__(self, session, appid, sample_size=-1):
        self.session = session
        self.appid = appid
        self.sampe_size = sample_size
        self.idx = 0
        self.data_url = STEAMURLS['DATA'].format(appid=appid)
        self.store_url = STEAMURLS['STORE'].format(appid=appid)
        self.reviews = {}
        self._maxreviews = None
        self.default_headers = {'User-Agent': settings.USER_AGENT}

    @property
    def maxreviews(self):
        if self._maxreviews is None:
            r = self.session.get(self.store_url, headers=self.default_headers)
            html = self.html_response(r.content)
            self._maxreviews = int(browse_all_rex.search(
                self.selector_path(html, '//*[@id="ViewAllReviewsall"]/a/text()')[0]).group('count').replace(',', ''))
            if self._maxreviews is None:
                self._maxreviews = 5
        return self._maxreviews

    def build_params(self, **kwargs):
        kwargs['start_offset'] = kwargs.get('start_offset', 0)
        kwargs['day_range'] = kwargs.get('day_range', days_since_release())
        kwargs['language'] = kwargs.get('language', 'english')
        kwargs['filter'] = kwargs.get('filter', 'all')
        return kwargs

    def data_request(self, start_offset, **kwargs):
        return self.session.get(self.data_url, params=self.build_params(start_offset=start_offset, **kwargs),
                                headers=self.default_headers.update({'X-Requested-With': 'XMLHttpRequest'}))

    @classmethod
    def html_response(cls, response):
        return html.fromstring(response)

    def scrape(self):
        self.last_item = None
        while True:
            r = self.data_request(self.idx)
            j = r.json()

            for item in self.parse_page(self.html_response(j['html'])):
                self.reviews[item.review_url] = item._asdict()
                self.idx += 1
                if len(self) >= self.sampe_size or len(self) >= self.maxreviews:
                    return self.reviews.values()
                self.last_item = item

            print(self.idx, len(self), r.url, self.last_item)

    @classmethod
    def selector_path(cls, selector, path):
        data = selector.xpath(path)
        if not data:
            return [None]
        return data

    @classmethod
    def parse_select(cls, selector):
        helpful = ''.join(cls.selector_path(selector, 'div[@class="header"]/text()'))
        user_profile = cls.selector_path(selector, 'div/div[@class="leftcol"]/div[@class="persona_name"]/a/@href')[0]
        user_name = cls.selector_path(selector, 'div/div[@class="leftcol"]/div[@class="persona_name"]/a/text()')[0]
        user_num_owned_games = cls.selector_path(selector,
                                                 'div/div[@class="leftcol"]/div[@class="num_owned_games"]/a/text()')[0]
        user_reviews = cls.selector_path(selector, 'div/div[@class="leftcol"]/div[@class="num_reviews"]/a/text()')[0]
        recommended = cls.selector_path(selector,
                                        'div/div[@class="rightcol"]/div[@class="vote_header"]/div[@class="title ellipsis"]/a/text()')[
            0]
        hours_played = cls.selector_path(selector,
                                         'div/div[@class="rightcol"]/div[@class="vote_header"]/div[@class="hours ellipsis"]/text()')[
            0]
        posted_date = cls.selector_path(selector, 'div/div[@class="rightcol"]/div[@class="postedDate"]/text()')[0]
        content = cls.selector_path(selector, 'div/div[@class="rightcol"]/div[@class="content"]/text()')[0]
        review_url = cls.selector_path(selector,
                                       'div/div[@class="rightcol"]/div[@class="vote_header"]/div[@class="title ellipsis"]/a/@href')[
            0]
        return ReviewScraperItem(helpful=helpful, user_profile=user_profile, user_name=user_name,
                                 user_num_owned_games=user_num_owned_games, user_reviews=user_reviews,
                                 recommended=recommended, hours_played=hours_played, posted_date=posted_date,
                                 content=content, review_url=review_url)

    @classmethod
    def parse_page(cls, response):
        # parses all of the reviews from the page.
        for selector in response.xpath('//div[@class="review_box"]'):
            yield cls.parse_select(selector)

    def __len__(self):
        return len(self.reviews)


def steam_languages():
    r = requests.get(r'http://store.steampowered.com/')
    return [a.attrib['href'].strip('?l=') for a in
            html.fromstring(r.content).xpath('//*[@id="language_dropdown"]/div/a')]


if __name__ == '__main__':
    st = time.time()
    try:
        appid = "290790"
        with open(r'D:\code\steam_scraper\custom_scraper\reviews.json', 'w+', encoding='utf8') as f:
            session = requests.session()
            sr = SteamReviews(session, appid, 5)
            json.dump(list(sr.scrape()), f, ensure_ascii=False, indent=1)
            print(len(sr))
    finally:
        print(time.time() - st)
