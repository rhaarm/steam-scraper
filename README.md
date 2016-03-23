# steam-scraper
Scrapes Review comments from a Steam Game page. Returns JSON to screen by default.
http://store.steampowered.com/app/

# Usage
Get all reviews from an app?
```bash
>python3 steam_scraper.py --appid 290790
```

Limit to a sample size of 50 reviews?
```bash
>python3 steam_scraper.py --appid 290790 --sample 50
```

Write the JSON to file and not screen?
```bash
>python3 steam_scraper.py --appid 290790 -o output.json
>python3 steam_scraper.py --appid 290790 -o c:\path\to\output.json
>python3 steam_scraper.py --appid 290790 -o c:\path\to\output.json --sample 100
```