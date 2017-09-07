# Library of parsers for extracting lot attributes from a Christie's auction lot entry

import re
import dateparser

def christies_parse_name(response_xpath):
	'''Parses the Name of an Artist if it's in the form Vincent van Gogh (1853-1890)
	
	Arguments:
		response_xpath xPath of Title
	
	Returns:
		String -- Name of Artist
	'''
	try:
	    a_name = re.match(r'(.*)\b\s?\(', response_xpath)
	    return a_name[1]
	except: return ""

def christies_parse_sale_date(response_xpath):
	'''Parses the sale date of a lot
	
	Arguments:
		response_xpath xPath of Title
	
	Returns:
		String -- date
	'''
	
	# sale was on a single day
	try:
		r = dateparser.parse(response_xpath).date().isoformat()
	except:
		pass
	# sale was on many days
	try:
		d = re.search(r'\d{1,2}\s\w*\s\d{4}', response_xpath)[0]
		r = dateparser.parse(d).date().isoformat()
	except:
		print(response_xpath, 'nicht parsbar')
		return ""

	return(r)


def christies_parse_created_year(response_xpath):
	'''Returns the year of creation of an artwork
	
	Parses the input xpath for creation related keywords and returns a following 4 digit number 
	
	Arguments:
		response_xpath 
	
	Returns:
		4 digit integer
	'''
	if response_xpath:
		pattern_for_created = re.compile(r'''
                                 (?:painted|signed|dated|executed|completed|painted|signed|circa)
                                 \b.{1,20}
                                 (\d{4})''',flags= re.IGNORECASE | re.VERBOSE )
		digits = pattern_for_created.findall(''.join(response_xpath))
		try:
			return int(digits[-1])
		except IndexError:
			return 0

def christies_parse_lot_id(response_xpath):
	'''Returns the id of an auction lot
	
	Arguments:
		response_xpath 
	
	Returns:
		string id
	'''
	try:
		return re.match(r'(\d*)', response_xpath)[1]
	except: return ""


def christies_parse_price_and_currency(response_xpath):
	'''Parses a string for price of an artwork
	
	Arguments:
		response_xpath -- Input string containing price

	Returns:
		List if two elements [int, string] -- [price, currency] price is integer, currency is 3 letter currency symbol 
	'''
	try:
		pattern_for_price = re.compile(r'''
			(\w{3})     #currency
			\s*([\d*\,]*\d*)  #number, thousands separated with commas
		''', re.VERBOSE)
		p =  pattern_for_price.match(response_xpath)
		price = int(p[2].replace(',', '')) # remove commas separating thousands
		currency = p[1] # 3 letter currency symbol
	except:
		price = 0
		currency = ""
	return [price, currency]

def christies_parse_price(price_and_currency):
	try:
		pattern_for_price = re.compile(r'''
			(\w{3})     #currency
			\s*([\d*\,]*\d*)  #number, thousands separated with commas
		''', re.VERBOSE)
		p =  pattern_for_price.match(price_and_currency)
		return int(p[2].replace(',', ''))
	except:
		return 0


def christies_parse_currency(price_and_currency):
	try:
		pattern_for_price = re.compile(r'''
			(\w{3})     #currency
			\s*([\d*\,]*\d*)  #number, thousands separated with commas
		''', re.VERBOSE)
		p =  pattern_for_price.match(price_and_currency)
		return p[1]
	except:
		return ""

def christies_parse_exhibited_in(response_xpath):
	# parse exhibited in
    try:
        return response_xpath.replace('\n',' ').replace('\r','')
    except:
        return ""

def christies_parse_provenance(response_xpath):
    if response_xpath == None:
    	return "" 
    else: return response_xpath.replace('\n',' ').replace('\r','')


def christies_parse_provenance_estate_of(text):
	return text.lower().count('estate') > 0 or text.lower().count('museum') > 0

def christies_parse_height_and_width(response_xpath):
	try:
		return re.findall(r'(\d*(?:\,|\.)\d+|\d+)(?:\s*x\s*)?(\d*(?:\,|\.)\d+|\d+)?(?:\s*)(in|cm|mm)', response_xpath.lower(), re.I)
	except:
		return [0,0,""]

def christies_parse_height(height_and_width):
	try:
		return float(height_and_width[0])*conversion_to_cm_factor(height_and_width[2])
	except:
		return 0    
               
def christies_parse_width(height_and_width):
	try:
		return float(height_and_width[1])*conversion_to_cm_factor(height_and_width[2])
	except:
		return 0  

def christies_parse_size_unit(height_and_width):
		return height_and_width[2].lower()

def christies_parse_image_url(response_xpath):
    if "no-image" in response_xpath: return ""
    else: return response_xpath

def christies_parse_estimated_price_currency(response_xpath):
	try:
		pattern_for_prices = re.compile(r'''
		(\w{3})     #currency
		\s*([\d*\,]*\d*)  #number, thousands separated with commas
		''', re.VERBOSE)
		prices = pattern_for_prices.findall(response_xpath)
		return prices[0][0]	
	except: return [""]

def christies_parse_estimated_price_min(response_xpath):
	try:
		pattern_for_prices = re.compile(r'''
		(\w{3})     #currency
		\s*([\d*\,]*\d*)  #number, thousands separated with commas
		''', re.VERBOSE)
		prices = pattern_for_prices.findall(response_xpath)
		return int(prices[0][1].replace(',', ''))
	except: return 0

def christies_parse_estimated_price_max(response_xpath):
	try:
		pattern_for_prices = re.compile(r'''
		(\w{3})     #currency
		\s*([\d*\,]*\d*)  #number, thousands separated with commas
		''', re.VERBOSE)
		prices = pattern_for_prices.findall(response_xpath)
		return int(prices[1][1].replace(',', ''))
	except: return 0
