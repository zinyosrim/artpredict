import re
from scrapy.item import Item, Field
from scrapy.loader.processors import Join, Compose, MapCompose, TakeFirst 
from artcrawlerHelper import strip_accents    # generic helpers for all spiders
from artcrawlerHelper import parse_style, parse_date, parse_created_year, parse_text, parse_integer, parse_dimensions_and_convert_to_cm
from artcrawlerHelper import parse_height, parse_width, parse_size_unit
from artcrawlerHelper import number_of_exhibitions_in_major_museums, provenance_includes_estate_or_museum
from artcrawlerHelper import parse_max_estimated_price, parse_min_estimated_price, parse_estimated_price_currency
from christiesparse import * # Christie's specific parse helpers
from phillipsparse import phillips_parse_sale_id, phillips_parse_sale_location, phillips_parse_sale_price, phillips_parse_sale_currency
from phillipsparse import phillips_parse_estimated_price_range, phillips_parse_image_url # Phillips specific parse helpers

class ChristiesLot(Item):
    key                    = Field() 
    auction_house_name     = Field() 
    sale_id                = Field()
    sale_title             = Field() 
    sale_date              = Field(input_processor = MapCompose(parse_date)) 
    sale_location          = Field() 
    lot_id                 = Field(input_processor = MapCompose(christies_parse_lot_id)) 
    artist_name            = Field(input_processor = MapCompose(christies_parse_name)) 
    artist_name_normalized = Field(input_processor = MapCompose(christies_parse_name, strip_accents)) 
    description            = Field(input_processor = Compose(parse_text)) 
    created_year           = Field(input_processor = Compose(parse_created_year)) 
    price                  = Field(input_processor = MapCompose(christies_parse_price)) 
    currency               = Field(input_processor = MapCompose(christies_parse_currency)) 
    title                  = Field()
    secondary_title        = Field()  
    notes                  = Field(input_processor = MapCompose(parse_text)) 
    style                  = Field(input_processor = MapCompose(parse_text, parse_style)) 
    exhibited_in           = Field(input_processor = MapCompose(christies_parse_exhibited_in)) 
    exhibited_in_museums   = Field(input_processor = MapCompose(christies_parse_exhibited_in, number_of_exhibitions_in_major_museums)) 
    provenance             = Field(input_processor = MapCompose(christies_parse_provenance)) 
    provenance_estate_of   = Field(input_processor = MapCompose(christies_parse_provenance, christies_parse_provenance_estate_of)) 
    height                 = Field(input_processor = MapCompose(christies_parse_height_and_width, christies_parse_height)) 
    width                  = Field(input_processor = MapCompose(christies_parse_height_and_width, christies_parse_width)) 
    size_unit              = Field(input_processor = MapCompose(christies_parse_height_and_width, christies_parse_size_unit))
    image_url              = Field(input_processor = MapCompose(christies_parse_image_url)) 
    max_estimated_price    = Field(input_processor = MapCompose(christies_parse_estimated_price_max)) 
    min_estimated_price    = Field(input_processor = MapCompose(christies_parse_estimated_price_min)) 
    estimate_currency      = Field(input_processor = MapCompose(christies_parse_estimated_price_currency))  

class PhillipsLot(Item):
    key                    = Field()
    url                    = Field()
    auction_house_name     = Field()
    sale_id                = Field(input_processor = MapCompose(phillips_parse_sale_id))
    sale_title             = Field() 
    sale_date              = Field(input_processor = MapCompose(parse_text, parse_date)) 
    sale_location          = Field(input_processor = MapCompose(parse_text, phillips_parse_sale_location)) 
    lot_id                 = Field(input_processor = MapCompose(parse_integer))
    artist_name            = Field() 
    artist_name_normalized = Field(input_processor = MapCompose(strip_accents)) 
    description            = Field(input_processor = MapCompose(parse_text)) 
    created_year           = Field(input_processor = MapCompose(parse_text, parse_created_year)) 
    price                  = Field(input_processor = MapCompose(parse_text, phillips_parse_sale_price)) 
    currency               = Field(input_processor = MapCompose(parse_text, phillips_parse_sale_currency)) 
    title                  = Field(input_processor = MapCompose(parse_text))
    secondary_title        = Field()  
    notes                  = Field(input_processor = MapCompose(parse_text)) 
    style                  = Field(input_processor = MapCompose(parse_text, parse_style)) 
    exhibited_in           = Field(input_processor = MapCompose(parse_text)) 
    exhibited_in_museums   = Field(input_processor = MapCompose(parse_text, number_of_exhibitions_in_major_museums)) 
    provenance             = Field(input_processor = MapCompose(parse_text)) 
    provenance_estate_of   = Field(input_processor = MapCompose(parse_text, provenance_includes_estate_or_museum)) 
    height                 = Field(input_processor = MapCompose(parse_text, parse_dimensions_and_convert_to_cm, parse_height)) 
    width                  = Field(input_processor = MapCompose(parse_text, parse_dimensions_and_convert_to_cm, parse_width)) 
    size_unit              = Field(input_processor = MapCompose(parse_text, parse_dimensions_and_convert_to_cm, parse_size_unit))
    image_url              = Field(input_processor = MapCompose(phillips_parse_image_url)) 
    max_estimated_price    = Field(input_processor = MapCompose(parse_text, phillips_parse_estimated_price_range, parse_max_estimated_price)) 
    min_estimated_price    = Field(input_processor = MapCompose(parse_text, phillips_parse_estimated_price_range, parse_min_estimated_price)) 
    estimate_currency      = Field(input_processor = MapCompose(parse_text, phillips_parse_estimated_price_range, parse_estimated_price_currency))  