from datetime import datetime, date, time, timedelta
import logging
import re
import scrapy
from scrapy.loader import ItemLoader
from scrapy_splash import SplashRequest
from scrapy.loader.processors import TakeFirst 
from w3lib.html import replace_tags
from artcrawler.items import PhillipsLot

class PhillipsSpider(scrapy.Spider):
    name = "phillips" 

    def __init__(self):
        self.domain = 'http://www.phillips.com'
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:10.0) Gecko/20100101 Firefox/10.0"

    def start_requests_test(self):
        urls = ['http://www.phillips.com/detail/PABLO-PICASSO/UK030217/1', 
                'http://www.phillips.com/detail/WOLFGANG-TILLMANS/UK010417/2', 
                'http://www.phillips.com/detail/STERLING-RUBY/UK010517/217', 
                'http://www.phillips.com/detail/MARC-RIBOUD/UK040117/56',
                'http://www.phillips.com/detail/ANDY-WARHOL/HK010317/16',
                'http://www.phillips.com/detail/STEVEN-PIPPIN/NY010606/443',
                'http://www.phillips.com/detail/ROLEX/HK080117/1103A' ]

        for url in urls:
            yield SplashRequest(
                url,
                callback = self.parse_lot,
                args={
                    'wait': 1.5,
                    'ua': self.user_agent},  
            )    

    def start_requests(self):
        base_url = "https://www.phillips.com/auctions/past/page/"
        last_page = 40
        for i in range(1, last_page +1 ):        
            past_auctions_url = base_url + str(i)
            
            yield SplashRequest(
                past_auctions_url,
                callback = self.parse_past_auctions,
                args={
                    'wait': 4,
                    'ua': self.user_agent},  
            )
    
    def parse_past_auctions(self, response):
        for auctions in response.xpath('//ul[@id="main-list-backbone"]'):
            for auction in auctions.xpath('//a[contains(@class,"image-link")]/@href').extract():
                yield SplashRequest(
                    self.domain + auction,
                    self.parse_auction,
                    args={
                        'wait': 2.5,
                        'ua': self.user_agent},      
                )
        logging.info("Crawled " + response.url)

    def parse_auction(self, response):
        for lots in response.xpath('//ul[@id="main-list-backbone"]'):
            for lot in lots.xpath('//a[contains(@class,"image-link")]/@href').extract():
                yield SplashRequest(
                    self.domain + lot,
                    self.parse_lot,
                    args={
                       'wait': 1.5,
                       'ua': self.user_agent}      
                )
        logging.info("Parsed auction: " + response.url)

    def parse_lot(self, response):
        # Parse a Phillips auction lot page
        
        lot = ItemLoader(item=PhillipsLot(), response=response)
        lot.default_output_processor = TakeFirst()

        lot.add_value("auction_house_name", "Phillips")
        lot.add_value("url", response.url)
        lot.add_value("sale_id", response.url)
        lot.add_xpath("sale_title", '//div[@class="sale-title-banner"]/a/strong/text()')
        lot.add_xpath("sale_date", '//div[@class="sale-title-banner"]/a')
        lot.add_xpath("sale_location", '//div[@class="sale-title-banner"]/a')
        lot.add_xpath("lot_id", '//div[@class="lot-information"]/h1')
        lot.add_xpath("artist_name", '//div[@class="lot-information"]/a/h2/text()')
        lot.add_xpath("artist_name_normalized", '//div[@class="lot-information"]/a/h2/text()')
        
        description_xpath = '//div[@class="lot-information"]/p[not(@class)]'
        lot.add_xpath("description", description_xpath)

        lot.add_xpath("created_year", description_xpath)

        sale_price_and_currency_xpath = '//p[@class="sold"]/text()'
        lot.add_xpath("price", sale_price_and_currency_xpath)
        lot.add_xpath("currency", sale_price_and_currency_xpath)

        lot.add_xpath("title", '//div[@class="lot-information"]/p[@class="title"]/text()')
        lot.add_value("secondary_title", None)
        lot.add_xpath("notes", '//div[contains(@class, "lot-essay")]/p')
        lot.add_xpath("style", '//div[@class="lot-information"]/p[not(@class)]')

        exhibited_in_xpath = '//p[preceding-sibling::p[1]/strong="Exhibited"]'
        lot.add_xpath("exhibited_in", exhibited_in_xpath)
        lot.add_xpath("exhibited_in_museums", exhibited_in_xpath)

        provenance_xpath = '//p[preceding-sibling::p[1]/strong="Provenance"]/text()'
        lot.add_xpath("provenance", provenance_xpath)
        lot.add_xpath("provenance_estate_of", provenance_xpath)

        lot.add_xpath("height", description_xpath)
        lot.add_xpath("width", description_xpath)  
        lot.add_xpath("size_unit", description_xpath)      
        lot.add_value("key", datetime.now().isoformat().replace(':', '-').replace('.', '-'))
        lot.add_xpath("image_url", '//a[@class="modal-zoom"]/@zoomimagesrc')

        estimate_xpath = '//strong[contains(text(), "Estimate")]/..'
        lot.add_xpath("min_estimated_price", estimate_xpath)
        lot.add_xpath("max_estimated_price", estimate_xpath)
        lot.add_xpath("estimate_currency", estimate_xpath)

        yield lot.load_item()


    