# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class ReviewScraperItem(Item):
    # header
    helpful = Field()  # /text

    # ReviewContentall*/leftcol/
    user_profile = Field()  # persona_name/a/href
    user_name = Field()  # persona_name/a/text
    user_num_owned_games = Field()  # num_owned_games/a/text
    user_reviews = Field()  # num_reviews/a/text

    # ReviewContentall*/rightcol/
    recommended = Field()  # vote_header/title ellipsis/a/text
    hours_played = Field()  # vote_header/hours ellipsis/text
    posted_date = Field()  # vote_header/postedDate/text
    content = Field()  # vote_header/content/text
