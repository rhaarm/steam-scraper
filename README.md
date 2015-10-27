# steam-scraper
Scrapes Review comments from a Steam Game page.

Using [Scrapy](http://scrapy.org/) and [Selenium](http://selenium-python.readthedocs.org/)
Requires Python 2.7, because of Scrapy... :(

# Usage 

If scrapy is installed, you just simply run.
```bash
>scrapy runspider spiders\steamreviews.py -a appid={Steam Game App Id}

# increase the timeout between loads in seconds? 
# This will cause the script to wait {seconds} minutes at the end of loading all comments, do not kill script.
>scrapy runspider spiders\steamreviews.py -a appid={Steam Game App Id} timeout=600
```

If you wish to have this go to an output file, here is output CSV format.
```bash
>scrapy runspider spiders\steamreviews.py -a appid={Steam Game App Id} -o output.csv
```
Or JSON output
```bash
>scrapy runspider spiders\steamreviews.py -a appid={Steam Game App Id} -o output.json
```
The name of the file can be changed as well, see also the supported extension on [scrapy's website](http://doc.scrapy.org/en/1.0/topics/feed-exports.html?highlight=output)

# How it works?
The script will execute a FireFox engine with Selenium, allowing for any AJAX and JS to be executed. Then once the page source fully loaded it will execute the scrapy extraction. 
