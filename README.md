# Yellow Pages Scraper 2.0

This repository contains a Python-language web scraper for `yellowpages.com` to quickly collect a large amount of user-defined business data using the `requests` library.

The code in its current represents a significant departure from the originally forked library and features the following improvements:

- Graceful handling of `503` HTTP responses caused by implementation of Cloudflare DNS proxying by `yellowpages.com`
- Support for custom multipage content input user-defined start and end page
- Modified input parameter nomenclature and format to support more consistent function
- Retry mechanisms to prevent ungraceful exits, graceful exit processes for continued resource inavailability

Nonetheless, we wish to extend our humble thanks to [ScrapeHero](https://github.com/scrapehero) for providing the foundation upon which this toolkit was created.

Yellow Pages Scraper 2.0 extracts the following fields, if they are available:

```python
business_name,
telephone,
rank,
website,
zipcode,
```

`yellowpages.com` does not make business email addresses publically available.

## Prerequisites

All required libraries are found in `requirements.txt`. Please install them using whichever package manager you prefer.

## Usage

Yellow Pages web scraper is launched with the following command

```bash
python scrape.py "keyword" "location" x y
```

Where:

- `"keyword"` is the type of business to query
- `"location"` is the human-readable city and state to query
- `x` is the first page to query
- `y` is the last page to query

Thus, a complete request looks like this:

```bash
python scrape.py "restaurant" "Seattle, WA" 1 5
```

The above input queries the first five pages of restaurants in Seattle, Washington.

## Output

The output of Yellow Pages Scraper 2.0 is a comma-separated values (CSV) file named based on the input parameters.

Continuing with the example above, the CSV output is:

`restaurant-seattle-wa-yellowpages.csv`