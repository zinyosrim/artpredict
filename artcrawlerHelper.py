import unicodedata
import re

def conversion_to_cm_factor(length_unit):
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

def strip_accents(string_with_accents):
    '''Normalize input string by removing accents but keeping Umlauts'''
    try:
        return ''.join(c for c in unicodedata.normalize('NFD', string_with_accents)
            if not unicodedata.name(c).endswith('ACCENT')) 
    except:
        return string_with_accents

def year_month_iterator(start_month, start_year, end_month, end_year):
    ym_start    = 12 * start_year + start_month - 1
    ym_end      = 12 * end_year + end_month - 1
    for ym in range(ym_start, ym_end):
        y, m = divmod(ym, 12)
        yield y, m+1

def strip_accents(string_with_accents):
	'''Normalize input string by removing accents but keeping Umlauts'''
	try:
		return ''.join(c for c in unicodedata.normalize('NFD', string_with_accents)
			if not unicodedata.name(c).endswith('ACCENT')) 
	except:
		return string_with_accents

def number_of_exhibitions_in_major_museums(text):
	'''Parse input text and return count of occurences'''
	museum_keywords = ["museum", "musée", "museo", "beyeler", "thannhauser", "gmurzynska", 
	                   "georges petit", "matthiesen", "tate modern", "somerset house", "wilanów palace", 
	                   "the national art center", "Galleria degli Uffizi", "National Portrait Gallery", 
	                   "Art Institute of Chicago", "Saatchi Gallery", "Wawel Royal Castle", "Galleria dell'Accademia", 
	                   "National Galler", "Grand Palais", "Tretyakov", "Tate Britain", "Royal Academy of Arts", "Minneapolis Institute of Art"]
	n = 0
	for keyword in museum_keywords:
		n += text.lower().count(keyword)
	return n

def parseHelper_created_year(description):
    if description:
        pattern_for_created = re.compile(r'''\b
                                 (?:painted|signed|dated|executed|completed|painted|signed|circa)
                                 \b.{1,20}
                                 (\d{4})''',flags= re.IGNORECASE | re.VERBOSE )
        digits = pattern_for_created.findall(description)          
        try:
            return int(digits[-1])
        except IndexError:
            return 0

def parseHelper_style(text):
    if text:
        t = text.lower()
        if 'oil on canvas' in t: return 'oil on canvas'
        if 'oil on board' in t: return 'oil on board'
        if 'oil on paper' in t: return 'oil on paper'
        if 'tempera on canvas' in t: return 'tempera on canvas'
        if 'tempera on board' in t: return 'tempera on board'
        if 'tempera on paper' in t: return 'tempera on paper'
        if 'drawing' in t: return 'drawing'
        if ('water' in t) and (('colour' in t) or ('color' in t)): return 'water color'
        if 'pastel' in t: return 'pastel'
        if 'bronze' in t: return 'bronze'
        if 'marble' in t: return 'marble'
        if 'acrylic on canvas' in t: return 'acrylic on canvas'
        if 'acrylic on paper' in t: return 'acrylic on paper'
        if 'pen on paper' in t: return 'pen on paper'
        if 'ink on paper' in t: return 'ink on paper'
        if 'paper' in t: return 'paper'
        if 'canvas' in t: return 'canvas'
        if 'acryllic' in t: return '<a href=""></a>cryllic'
        return '' 