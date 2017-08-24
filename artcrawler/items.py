from scrapy.item import Item, Field
from scrapy.loader.processors import Join, Compose, MapCompose, TakeFirst 
from artcrawlerHelper import number_of_exhibitions_in_major_museums 
from artcrawlerHelper import parseHelper_style
from artcrawlerHelper import conversion_to_cm_factor
from artcrawlerHelper import strip_accents
import re


def parseHelper_name(response_xpath):
	# parse name
    try:
	    a_name = re.match(r'(.*)\b\s?\(', response_xpath)
	    return a_name[1] 
    except: return ""

def parseHelper_text(response_xpath):
	if response_xpath == None:
		return ""   
	else: return ''.join(response_xpath).replace('\n','').replace('\r','')

def parseHelper_created_year(response_xpath):
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

def parseHelper_lot_id(response_xpath):
	try:
		return re.match(r'(\d*)', response_xpath)[1]
	except: return ""


def parseHelper_price_and_currency(response_xpath):
	try:
		pattern_for_price = re.compile(r'''
			(\w{3})     #currency
			\s*([\d*\,]*\d*)  #number, thousands separated with commas
		''', re.VERBOSE)
		p =  pattern_for_price.match(response_xpath)
		price = int(p[2].replace(',', ''))
		currency = p[1]
	except:
		price = 0
		currency = ""
	return [price, currency]

def parseHelper_price(price_and_currency):
	try:
		pattern_for_price = re.compile(r'''
			(\w{3})     #currency
			\s*([\d*\,]*\d*)  #number, thousands separated with commas
		''', re.VERBOSE)
		p =  pattern_for_price.match(price_and_currency)
		return int(p[2].replace(',', ''))
	except:
		return 0


def parseHelper_currency(price_and_currency):
	try:
		pattern_for_price = re.compile(r'''
			(\w{3})     #currency
			\s*([\d*\,]*\d*)  #number, thousands separated with commas
		''', re.VERBOSE)
		p =  pattern_for_price.match(price_and_currency)
		return p[1]
	except:
		return ""

def parseHelper_exhibited_in(response_xpath):
	# parse exhibited in
    try:
        return response_xpath.replace('\n',' ').replace('\r','')
    except:
        return ""

def parseHelper_exhibited_in_museums(text):
	# parse exhibited in museums
    try:
        exhibited_in = text.replace('\n',' ').replace('\r','')
        return number_of_exhibitions_in_major_museum(exhibited_in.lower())
    except:
        return ""
        exhibited_in_museums = 0

def parseHelper_provenance(response_xpath):
    if response_xpath == None:
    	return "" 
    else: return response_xpath.replace('\n',' ').replace('\r','')


def parseHelper_provenance_estate_of(text):
	return text.lower().count('estate') > 0 or text.lower().count('museum') > 0

def parseHelper_height_and_width(response_xpath):
	try:
		return re.findall(r'(\d*(?:\,|\.)\d+|\d+)(?:\s*x\s*)?(\d*(?:\,|\.)\d+|\d+)?(?:\s*)(in|cm|mm)', response_xpath.lower(), re.I)
	except:
		return [0,0,""]

def parseHelper_height(height_and_width):
	try:
		return float(height_and_width[0])*conversion_to_cm_factor(height_and_width[2])
	except:
		return 0    
               
def parseHelper_width(height_and_width):
	try:
		return float(height_and_width[1])*conversion_to_cm_factor(height_and_width[2])
	except:
		return 0  

def parseHelper_size_unit(height_and_width):
		return height_and_width[2].lower()

def parseHelper_image_url(response_xpath):
    if "no-image" in response_xpath: return ""
    else: return response_xpath

def parseHelper_estimated_price_currency(response_xpath):
	try:
		pattern_for_prices = re.compile(r'''
		(\w{3})     #currency
		\s*([\d*\,]*\d*)  #number, thousands separated with commas
		''', re.VERBOSE)
		prices = pattern_for_prices.findall(response_xpath)
		return prices[0][0]	
	except: return [""]

def parseHelper_estimated_price_min(response_xpath):
	try:
		pattern_for_prices = re.compile(r'''
		(\w{3})     #currency
		\s*([\d*\,]*\d*)  #number, thousands separated with commas
		''', re.VERBOSE)
		prices = pattern_for_prices.findall(response_xpath)
		return int(prices[0][1].replace(',', ''))
	except: return 0

def parseHelper_estimated_price_max(response_xpath):
	try:
		pattern_for_prices = re.compile(r'''
		(\w{3})     #currency
		\s*([\d*\,]*\d*)  #number, thousands separated with commas
		''', re.VERBOSE)
		prices = pattern_for_prices.findall(response_xpath)
		return int(prices[1][1].replace(',', ''))
	except: return 0

class Lot(Item):  
    key = Field(
    	output_processor = TakeFirst()) 
    auction_house_name = Field(
    	output_processor = TakeFirst()) 
    sale_id = Field(
    	output_processor = TakeFirst()) 
    sale_title = Field(
    	output_processor = TakeFirst()) 
    sale_date = Field(
    	output_processor = TakeFirst()) 
    sale_location = Field(
    	output_processor = TakeFirst()) 
    lot_id = Field(
    	input_processor  = MapCompose(parseHelper_lot_id),
    	output_processor = TakeFirst()) 
    artist_name = Field(
    	input_processor = MapCompose(parseHelper_name), 
    	output_processor = TakeFirst()) 
    artist_name_normalized = Field(
    	input_processor = MapCompose(parseHelper_name, strip_accents), 
    	output_processor = TakeFirst()) 
    description = Field(
    	input_processor = Compose(parseHelper_text), 
    	output_processor = TakeFirst()) 
    created_year = Field(
    	input_processor = Compose(parseHelper_created_year), 
    	output_processor = TakeFirst()) 
    price = Field(
    	input_processor = MapCompose(parseHelper_price), 
    	output_processor = TakeFirst()) 
    currency = Field(
    	input_processor  = MapCompose(parseHelper_currency), 
    	output_processor = TakeFirst()) 
    title = Field(
    	output_processor = TakeFirst())
    secondary_title = Field(
    	output_processor = TakeFirst())  
    notes = Field(
    	input_processor  = MapCompose(parseHelper_text),
    	output_processor = TakeFirst()) 
    style = Field(
    	input_processor  = MapCompose(parseHelper_text, parseHelper_style), 
    	output_processor = TakeFirst()) 
    exhibited_in = Field(
    	input_processor  = MapCompose(parseHelper_exhibited_in), 
    	output_processor = TakeFirst()) 
    exhibited_in_museums = Field(
    	input_processor  = MapCompose(parseHelper_exhibited_in, parseHelper_exhibited_in_museums), 
    	output_processor = TakeFirst()) 
    provenance = Field(
    	input_processor  = MapCompose(parseHelper_provenance), 
    	output_processor = TakeFirst()) 
    provenance_estate_of = Field(
    	input_processor  = MapCompose(parseHelper_provenance, parseHelper_provenance_estate_of), 
    	output_processor = TakeFirst()) 
    height = Field(
    	input_processor  = MapCompose(parseHelper_height_and_width, parseHelper_height), 
    	output_processor = TakeFirst()) 
    width = Field(
    	input_processor  = MapCompose(parseHelper_height_and_width, parseHelper_width), 
    	output_processor = TakeFirst()) 
    size_unit = Field(
    	input_processor  = MapCompose(parseHelper_height_and_width, parseHelper_size_unit), 
    	output_processor = TakeFirst())
    image_url = Field(
    	input_processor  = MapCompose(parseHelper_image_url), 
    	output_processor = TakeFirst()) 
    max_estimated_price  = Field(
    	input_processor  = MapCompose(parseHelper_estimated_price_max), 
    	output_processor = TakeFirst()) 
    min_estimated_price  = Field(
    	input_processor  = MapCompose(parseHelper_estimated_price_min), 
    	output_processor = TakeFirst()) 
    estimate_currency = Field(
    	input_processor  = MapCompose(parseHelper_estimated_price_currency), 
    	output_processor = TakeFirst())  