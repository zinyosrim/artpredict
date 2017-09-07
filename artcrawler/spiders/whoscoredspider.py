# -*- coding: utf-8 -*-
import json
from six.moves.urllib.parse import urljoin

import scrapy


class WhoscoredspiderSpider(scrapy.Spider):
    name = "whoscoredspider"
    allowed_domains = ["whoscored.com"]
    start_urls = (
        'https://www.whoscored.com/Regions/81/Tournaments/3/Seasons/4336/Stages/9192/Fixtures/Germany-Bundesliga-2014-2015',
    )

    def start_requests(self):
        script = """
        function main(splash)
            local url = splash.args.url
            assert(splash:go(url))
            assert(splash:wait(1))

            -- go back 1 month in time and wait a little (1 second)
            assert(splash:runjs("$('#date-controller > a:first-child').click()"))
            assert(splash:wait(1))

            -- return result as a JSON object
            return {
                html = splash:html(),
                -- we don't need screenshot or network activity
                --png = splash:png(),
                --har = splash:har(),
            }
        end
        """
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse_result, meta={
                'splash': {
                    'args': {'lua_source': script},
                    'endpoint': 'execute',
                }
            })

    def parse_result(self, response):

        # fetch base URL because response url is the Splash endpoint
        baseurl = response.meta["splash"]["args"]["url"]

        # decode JSON response
        splash_json = json.loads(response.body_as_unicode())

        # and build a new selector from the response "html" key from that object
        selector = scrapy.Selector(text=splash_json["html"], type="html")

        # loop on the table row
        for table in selector.css('table#tournament-fixture'):

            # seperating on each date (<tr> elements with a <th>)
            for cnt, header in enumerate(table.css('tr.rowgroupheader'), start=1):
                self.logger.info("date: %s" % header.xpath('string()').extract_first())

                # after each date, look for sibling <tr> elements
                # that have only N preceding tr/th,
                # N being the number of headers seen so far
                for row in header.xpath('''
                        ./following-sibling::tr[not(th/@colspan)]
                                               [count(preceding-sibling::tr[th/@colspan])=%d]''' % cnt):
                    self.logger.info("record: %s" % row.xpath('string()').extract_first())
                    match_report_href = row.css('td > a.match-report::attr(href)').extract_first()
                    if match_report_href:
                        self.logger.info("match report: %s" % urljoin(baseurl, match_report_href))