import unicodedata
import re
from w3lib.html import remove_tags, replace_tags
import logging
import dateparser

def conversion_to_cm_factor(length_unit):
    '''Returns the conversion factor to cm for a given length unit
    
    Arguments:
        length_unit cm, mm or in
    
    Returns:
        float -- conversion factor
    '''
    length_unit = length_unit.lower()
    if length_unit == "cm":
        factor = 1
    elif length_unit == "mm":
        factor = 0.1
    elif length_unit == "in":
        factor = 2.54
    else:
        factor = 0
    return factor


def year_month_iterator(start_month, start_year, end_month, end_year):
    '''Iterator which yields for given start and end Month/Year combination year and month
    
    Arguments:
        start_month integer
        start_year integer
        end_month integer
        end_year integer
    
    Yields:
        integer -- year, month
    '''
    ym_start    = 12 * start_year + start_month - 1
    ym_end      = 12 * end_year + end_month - 1
    for ym in range(ym_start, ym_end):
        y, m = divmod(ym, 12)
        yield y, m+1

def strip_accents(string_with_accents):
	'''Normalizes a given text by converting letters with accent to without accent: Degás -> Degas
    
    Arguments:
        string_with_accents
    
    Returns:
        String
    '''
	try:
		return ''.join(c for c in unicodedata.normalize('NFD', string_with_accents)
			if not unicodedata.name(c).endswith('ACCENT')) 
	except:
		return string_with_accents


def number_of_exhibitions_in_major_museums(text):
    '''Parse input text and return count of occurences of Museum related keywords
    
    Arguments:
        text 
    
    Returns:
        Integer -- number of occurences of museum keywords 
    '''
    
    museum_keywords = ["museum", "musée", "museo", "beyeler", "thannhauser", "gmurzynska", 
                   "georges petit", "matthiesen", "tate modern", "somerset house", "wilanów palace", 
                   "the national art center", "galleria degli uffizi", "national portrait gallery", 
                   "art institute of chicago", "saatchi gallery", "wawel royal castle", "galleria dell'accademia", 
                   "national galler", "grand palais", "tretyako", "tate britain", "royal academy of arts", "minneapolis institute of art"]
    n = 0
    
    try:
        for keyword in museum_keywords:
            n += text.lower().count(keyword)
        return n
    except:
        return 0

def parse_text(text):
    '''Removes line breaks, HTML tags, leading/trailing spaces from text as a list and returns cleaned-up string
    
    Arguments:
        List of Strings

    Returns:
        string
    '''  
    
    try:
        return replace_tags(' '.join(text.split())).strip()
    except: 
        return ""

def parse_created_year(text):
    '''Returns the year of creation of an artwork
    
    Parses the input xpath for creation related keywords and returns a following 4 digit number 
    
    Arguments:
        text
    
    Returns:
        4 digit integer
    '''
    if text:
        pattern_for_created = re.compile(r'''
                                 (?:painted|signed|dated|executed|completed|painted|signed|circa)
                                 \b.{1,20}
                                 (\d{4})''',flags= re.IGNORECASE | re.VERBOSE )
        digits = pattern_for_created.findall(''.join(text))
        try:
            return int(digits[-1])
        except IndexError:
            return 0

def parse_date(text):
    '''Parses the sale date of a lot
    
    Arguments:
        String
    
    Returns:
        String -- date
    '''
    
    # first try
    try:
        return dateparser.parse(text).date().isoformat()
    except:
        pass
    # second try
    try:
        d = re.search(r'\d{1,2}\s\w*\s\d{4}', text)[0]
        return dateparser.parse(d).date().isoformat()
    except:
        logging.warning("Date can't be parsed from String: " + '"' + text + '"' )
        return ""


def provenance_includes_estate_or_museum(text):
    '''Check the provenance text for occurance of "museum" or "estate"
    
    Arguments:
        text String -- String including provenance information

    Returns:
        boolean
    '''
    if text == None: 
        return False
    else: 
        return text.lower().count('estate') > 0 or text.lower().count('museum') > 0

def parse_dimensions_and_convert_to_cm(text_with_decimals_and_fractions):
    '''Parses a text for dimensions and length units and return the dimensions in cm
    
    Parse the description text of an artwork for size information and return width and height in cm 
    
    Arguments:
        text_with_decimals_and_fractions String -- Text includung some dimension information

    Returns:
        [height, width, "cm"] in [float, float, string]
    '''
    try:
        text_no_fractions = re.sub(r'(\d+)\s+(\d+)/(\d+)', lambda m: str(float(int(m.group(1)) + int(m.group(2))/int(m.group(3)))), text_with_decimals_and_fractions)
        height_and_width = re.findall(r'(\d*(?:\,|\.)\d+|\d+)(?:\s*x\s*)?(\d*(?:\,|\.)\d+|\d+)?(?:\s*)(in|cm|mm)', text_no_fractions.lower(), re.I)[0]

        length_unit = height_and_width[2].lower()
        if length_unit == "cm":
            factor = 1
        elif length_unit == "mm":
            factor = 0.1
        elif length_unit == "in":
            factor = 2.54
        else:
            factor = 0

        return {"height": float(height_and_width[0])*factor, "width": float(height_and_width[1])*factor, "size_unit": "cm"}
    except:
        return {"height": 0, "width": 0, "size_unit": ""}

def parse_height(height_and_width):
    try:
        return float(height_and_width["height"])*conversion_to_cm_factor(height_and_width["size_unit"])
    except:
        return 0    
               
def parse_width(height_and_width):
    try:
        return float(height_and_width["width"])*conversion_to_cm_factor(height_and_width["size_unit"])
    except:
        return 0 

def parse_size_unit(height_and_width):
    try:
        return height_and_width["size_unit"]
    except:
        return ""

def parse_integer(text):
    try:
        return re.findall(r'\d+', text)[0]
    except:
        return None

def parse_style(text):
    '''Returns the style/media of an artwork
    
    Searches the input text for style/media related keywords from specific to generic and returns the first occurence
    
    Arguments:
        text including style/media information

    Returns:
        style/media
    '''
    if text:
        t = text.lower()
        if 'oil on canvas' in t: return 'oil on canvas'
        if 'oil on board' in t: return 'oil on board'
        if 'oil on paper' in t: return 'oil on paper'
        if 'tempera on canvas' in t: return 'tempera on canvas'
        if 'tempera on board' in t: return 'tempera on board'
        if 'tempera on paper' in t: return 'tempera on paper'
        if 'drawing' in t: return 'drawing'
        if (('water' in t) and ('colo' in t)) or ('aquarel' in t): return 'water color'
        if 'gouache on paper' in t: return 'gouache on paper'
        if 'pastel' in t: return 'pastel'
        if 'lithograph' in t: return 'lithograph'
        if 'etching' in t: return 'etching'
        if 'screenprint' in t: return 'screenprint'
        if 'print' in t: return 'print'
        if 'bronze' in t: return 'bronze'
        if 'marble' in t: return 'marble'
        if 'acrylic on canvas' in t: return 'acrylic on canvas'
        if 'acrylic on paper' in t: return 'acrylic on paper'
        if 'pen on paper' in t: return 'pen on paper'
        if 'ink on paper' in t: return 'ink on paper'
        if 'print' in t: return 'print'
        if 'acryllic' in t: return 'acryllic'
        if 'gouache' in t: return 'gouache'
        if 'paper' in t: return 'paper'
        if 'canvas' in t: return 'canvas'
        return '' 

def parse_max_estimated_price(estimate):
    return estimate["max_estimated_price"]

def parse_min_estimated_price(estimate):
    return estimate["min_estimated_price"]

def parse_estimated_price_currency(estimate):
    return estimate["currency"]