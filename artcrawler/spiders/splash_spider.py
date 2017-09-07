import scrapy
from scrapy_splash import SplashRequest

class MySpider(scrapy.Spider):
	name = "splash"
	allowed_domains = ["phillips.com"]
	start_urls = ["https://www.phillips.com/detail/BRIDGET-RILEY/UK010417/19"]
	def start_requests(self):
		for url in self.start_urls:
			yield SplashRequest(
				url,
				self.parse,
				endpoint='render.json',
				args={'har': 1, 'html': 1}
			)
	def parse(self, response):
		print("1. PARSED", response.real_url, response.url)
		print("2. ",response.css("title").extract())
		print("3. ",response.data["har"]["log"]["pages"])
		print("4. ",response.headers.get('Content-Type'))
		print("5. ",response.xpath('//p[@class="title"]/text()').extract())
        # response.body is a result of render.html call; it
        # contains HTML processed by a browser.
        # ...#//*[@id="lot-details"]/li[19]/div[1]/div[3]

