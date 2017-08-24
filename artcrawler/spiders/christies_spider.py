import dateparser
import re
import scrapy

from artcrawler.items import Lot
from artcrawlerHelper import number_of_exhibitions_in_major_museums
from artcrawlerHelper import strip_accents
from artcrawlerHelper import year_month_iterator
from artcrawlerHelper import parseHelper_created_year
from artcrawlerHelper import parseHelper_style
from artcrawlerHelper import conversion_to_cm_factor
from datetime import datetime, date, time, timedelta
from scrapy.http import TextResponse
from scrapy.loader import ItemLoader
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

class QuotesSpider(scrapy.Spider):
    name = "christies"
    allowed_domains = ["christies.com"]

    def __init__(self):
        self.driver = webdriver.Firefox()
        self.delay = 10
        self.domain = 'http://www.christies.com'

    def start_requests(self):
        urls = []
        for year, month in year_month_iterator( 1, 1998, 12, 2005 ):
            urls.append(self.domain + "/results/?month=" + str(month) + "&year=" + str(year) + "&locations=&scids=&pg=1&action=&initialpageload=false" ) 
        for year, month in year_month_iterator( 1, 2006, 7, 2017 ):
            urls.append(self.domain + "/results/?month=" + str(month) + "&year=" + str(year) + "&locations=&scids=5|7|11|17&pg=1&action=&initialpageload=false" )      
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_past_auction_results_page)

    def parse_past_auction_results_page(self, response):   
        for url in response.xpath("//ul[@class='auction-links']/li/a/@href"):
            yield scrapy.Request(url="http://christies.com" + url.extract(), callback=self.parse_past_auction_sale_lots_page)
    
    def parse_past_auction_sale_lots_page(self, response):                   
        self.driver.get(response.url)
        element = WebDriverWait(self.driver, self.delay).until(EC.presence_of_element_located((By.CLASS_NAME, "load-all")))

        while True:
            try:
                loadMoreButton = self.driver.find_element_by_xpath('//*[@id="loadMoreUpcomingPast"]')
                loadMoreButton.click()
                self.driver.implicitly_wait(self.delay) 
            except Exception as e:
                print(e)
                break

        resp = TextResponse(url=response.url, body=self.driver.page_source, encoding='utf-8')
        for url in resp.xpath('//*[@id="ResultContainer"]/li/div/div[1]/a[1]/@href'):
            yield scrapy.Request(url=url.extract(), callback=self.parse_lot)

    def parse_lot(self, response):
        
        lot = ItemLoader(item=Lot(), response=response)

        lot.add_value("auction_house_name", "Christie's")
        lot.add_value("sale_id", response.xpath('//*[@id="main_center_0_lnkSaleNumber"]/text()').extract_first())
        lot.add_value("sale_title", strip_accents(response.xpath('//*[@id="main_center_0_lblSaleTitle"]/text()').extract_first()))
        lot.add_value("sale_date", dateparser.parse(response.xpath('//*[@id="main_center_0_lblSaleDate"]/text()').extract_first()).date().isoformat())
        lot.add_value("sale_location", response.xpath('//*[@id="main_center_0_lblSaleLocation"]/text()').extract_first())
        lot.add_value("lot_id", response.xpath('//*[@id="main_center_0_lblLotNumber"]/text()').extract_first())
        lot.add_value("artist_name", response.xpath('//*[@id="main_center_0_lblLotPrimaryTitle"]/text()').extract_first())
        lot.add_value("artist_name_normalized", response.xpath('//*[@id="main_center_0_lblLotPrimaryTitle"]/text()').extract_first())
        lot.add_value("description", response.xpath('//*[@id="main_center_0_lblLotDescription"]/text()').extract())
        lot.add_value("created_year", response.xpath('//*[@id="main_center_0_lblLotDescription"]/text()').extract())
        lot.add_value("price", response.xpath('//*[@id="main_center_0_lblPriceRealizedPrimary"]/text()').extract_first())
        lot.add_value("currency", response.xpath('//*[@id="main_center_0_lblPriceRealizedPrimary"]/text()').extract_first())
        lot.add_value("title", strip_accents(response.xpath('//*[@id="main_center_0_lblLotPrimaryTitle"]/text()').extract_first()))
        lot.add_value("secondary_title", strip_accents(response.xpath('//*[@id="main_center_0_lblLotSecondaryTitle"]/text()').extract_first()))
        lot.add_value("notes", response.xpath('//*[@id="main_center_0_lblLotNotes"]/text()').extract())
        lot.add_value("style", response.xpath('//*[@id="main_center_0_lblLotDescription"]/text()').extract())
        lot.add_value("exhibited_in", response.xpath('//*[@id="main_center_0_lblExhibited"]/text()').extract())
        lot.add_value("exhibited_in_museums", response.xpath('//*[@id="main_center_0_lblExhibited"]/text()').extract())
        lot.add_value("provenance", response.xpath('//*[@id="main_center_0_lblLotProvenance"]/text()').extract())
        lot.add_value("provenance_estate_of", response.xpath('//*[@id="main_center_0_lblLotProvenance"]/text()').extract())
        lot.add_value("height", response.xpath('//*[@id="main_center_0_lblLotDescription"]/text()').extract())
        lot.add_value("width", response.xpath('//*[@id="main_center_0_lblLotDescription"]/text()').extract())
        lot.add_value("size_unit", response.xpath('//*[@id="main_center_0_lblLotDescription"]/text()').extract())
        lot.add_value("key", datetime.now().isoformat().replace(':', '-').replace('.', '-'))
        lot.add_value("image_url", response.xpath('//*[@id="imgLotImage"]/@src').extract_first())
        lot.add_value("max_estimated_price", response.xpath('//*[@id="main_center_0_lblPriceEstimatedPrimary"]/text()').extract_first())
        lot.add_value("min_estimated_price", response.xpath('//*[@id="main_center_0_lblPriceEstimatedPrimary"]/text()').extract_first())
        lot.add_value("estimate_currency", response.xpath('//*[@id="main_center_0_lblPriceEstimatedPrimary"]/text()').extract_first())

        yield lot.load_item()
    
    def closed(self, reason):
        self.driver.close()


