import json

import scrapy

from crucial.items import *


class BaseSpider(scrapy.Spider):
    allowed_domains = [
        'crucial.com',
        'www.crucial.com',
    ]

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError

    def parse_motherboard(self, response: scrapy.http.Response):
        if '/compatible-upgrade-for/' not in response.url:
            raise LookupError("Invalid url?")

        prodinfo = response.xpath("/html/head/title/text()").get().split(" | ")[1:-1]

        prods = Memory({
            "_manufacturer": prodinfo[0],
            "_model": prodinfo[-1],
            'modules': [],
        })

        for script in response.xpath("//script[@type='text/javascript']/text()").getall():
            # Find memory modules list from javascript

            if 'prodListJSmemory' not in script:
                # Not a memory module listing
                continue

            src = script.strip()
            src = src[src.find("["):]
            src = src.rstrip(";")
            src = src.rstrip("'")
            src = bytes(src, "raw_unicode_escape").decode("unicode_escape")

            modules = []
            for idx, item in enumerate(json.loads(src)):
                item['specs'] = item['specs'].strip("• ").split(" • ")
                modules.append(item)

            prods['modules'] = modules

        if len(prods['modules']) > 0:
            yield prods


class ManufacturerSpider(BaseSpider):
    name = 'manufacturer'

    start_urls = [
        'https://www.crucial.com/content/crucial/en-us/home/store/advisor/jcr:content/maincontent/zurbrow_copy_copy_co/zurbcolumn1/content/zurbrow/zurbcolumn1/content/threestepupgradeadvi.modelslistdata.json?productlineid=supermicro-motherboards',
    ]

    def parse(self, response: scrapy.http.Response):
        data = json.loads(response.body)['result']
        manufacturer = data['manufacturer']

        for model in data['models']:
            name = model['name']

            if ' ' in name:
                continue

            yield scrapy.Request(
                f"https://www.crucial.com/compatible-upgrade-for/{manufacturer.lower()}/{name.lower()}",
                callback=self.parse_motherboard,
            )


class MotherboardSpider(BaseSpider):
    name = 'motherboard'

    start_urls = [
        'https://www.crucial.com/compatible-upgrade-for/',
    ]

    def __init__(self, product: str = ""):
        if product == "":
            product = None

        if product is None:
            raise ValueError("Invalid product given")

        self.start_urls = [
            f'https://www.crucial.com/compatible-upgrade-for/{product}',
        ]

    def parse(self, response: scrapy.http.Response):
        yield scrapy.Request(response.url, callback=self.parse_motherboard)
