# Library of parsers for extracting lot attributes from a Phillips auction lot entry

import re
import dateparser
import logging
from w3lib.html import replace_tags

def phillips_parse_sale_id(url):
	try:
		return re.search(r'(?:\/)([aA-zZ\d]*)(?:\/)([aA-zZ\d]*)$', url)[1]
	except:
		logging.warning("Could not parse sale_id from lot URL: " + url)

def phillips_parse_sale_location(text):
	t = text.lower()
	if "london" in t:
		return "London"
	elif "new york" in t:
		return "New York"
	elif "geneva" in t:
		return "Geneva"
	elif "hong kong" in t:
		return "Hong Kong"
	else:
		logging.warning("Can't parse sale_location from " + text)
		return ""

def phillips_parse_sale_price(price_and_currency_as_string):
	if price_and_currency_as_string == None:
		return 0
	try:
		pattern_for_price = re.compile(r'''
            .*
            (£|GBP|\$|USD|HK\$|HKD|CHF|EUR|€)     #currency
            \s*([\d*\,]*\d*)  #number, thousands separated with commas
        ''', re.VERBOSE)
		p =  pattern_for_price.match(price_and_currency_as_string)
		price = int(p[2].replace(',', '')) # remove commas separating thousands
		if   p[1] in ("£", "GBP"): currency = "GBP"
		elif p[1] in ("$", "USD"): currency = "USD"
		elif p[1] in ("HK$", "HKD"): currency = "HKD"
		elif p[1] in ("CHF"): currency = "CHF"
		elif p[1] in ("€", "EUR"): currency = "EUR"
		else: price = 0	
		return price
	except:
		logging.WARNING('Could not parse sale_price')
		return 0

def phillips_parse_sale_currency(price_and_currency_as_string):
	if price_and_currency_as_string == None:
		return ""
	try:
		pattern_for_price = re.compile(r'''
			.*
			(£|GBP|\$|USD|HK\$|HKD|CHF|EUR|€)     #currency
			\s*([\d*\,]*\d*)  #number, thousands separated with commas
		''', re.VERBOSE)
		p =  pattern_for_price.match(price_and_currency_as_string)
		price = int(p[2].replace(',', '')) # remove commas separating thousands
		if   p[1] in ("£", "GBP"): currency = "GBP"
		elif p[1] in ("$", "USD"): currency = "USD"
		elif p[1] in ("HK$", "HKD"): currency = "HKD"
		elif p[1] in ("CHF"): currency = "CHF"
		elif p[1] in ("€", "EUR"): currency = "EUR"
		else: currency = ""		
		return currency
	except:
		logging.WARNING('Could not parse sale_currency')
		return ""

def phillips_parse_estimated_price_range(text_including_estimated_price):
	'''Parses a string for price of an artwork
	
	Arguments:
		price_and_currency_as_string -- Input string containing price

	Returns:
		List if two elements [int, string] -- [price, currency] price is integer, currency is 3 letter currency symbol 
	'''
	estimate = dict()
	try:	
		pattern_for_estimate = re.compile(r'''
            .*
			(£|GBP|\$|USD|HK\$|HKD|CHF|EUR|€)     #currency
			\s*
            ([\d*\,]*\d*)  # min price, number, thousands separated with commas
			\s*-?\s*
			([\d*\,]*\d*) # max price, number, thousands separated with commas
		''', re.VERBOSE)
		p =  pattern_for_estimate.match(text_including_estimated_price)
		estimate["min_estimated_price"] = int(p[2].replace(',', '')) # remove commas separating thousands
		estimate["max_estimated_price"] = int(p[3].replace(',', '')) # remove commas separating thousands
		if p[1] in ("£", "GBP"): estimate["currency"] = "GBP"
		if p[1] in ("$", "USD"): estimate["currency"] = "USD"
		if p[1] in ("HK$", "HKD"): estimate["currency"] = "HKD"
		if p[1] in ("CHF"): estimate["currency"] = "CHF"
		if p[1] in ("€", "EUR"): estimate["currency"] = "EUR"
	except:
		estimate["min_estimated_price"] = 0
		estimate["max_estimated_price"] = 0
		estimate["currency"] = ""
	return estimate

def phillips_parse_image_url(path):
	if path == None:
		logging.warning("Can't parse image_url!")
		return ""

	return path


