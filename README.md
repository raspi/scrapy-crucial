# scrapy-crucial

Web crawler for Crucial ([crucial.com](https://www.crucial.com))

## Requirements

* Python
* [Scrapy](https://scrapy.org/)

## Notes

* 30 day cache is used in `settings.py`

## Spiders

All items are downloaded as JSON in the `items/` directory.

### Memory modules for all motherboards from certain manufacturer

    scrapy crawl manufacturer -a product="supermicro/supermicro-motherboards"

This will generate `items/Memory/supermicro/<motherboard model>.json` which then lists all compatible memory modules for this motherboard.

### Memory modules for certain motherboard

    scrapy crawl motherboard -a product="supermicro/a2sdi-ln4f"

This will generate `items/Memory/supermicro/A2SDi-LN4F.json` which then lists all compatible memory modules for this motherboard.
