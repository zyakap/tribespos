GST_SUPPLY_TYPES = {
    'TAXABLE':    {'rate': 10.0,  'code': 'T',  'label': 'Taxable Supply (10%)'},
    'ZERO_RATED': {'rate': 0.0,   'code': 'Z',  'label': 'Zero-Rated Supply'},
    'EXEMPT':     {'rate': 0.0,   'code': 'E',  'label': 'GST Exempt'},
    'OUT_OF_SCOPE': {'rate': 0.0, 'code': 'OS', 'label': 'Out of Scope'},
}

ZERO_RATED_CATEGORIES = ['exports', 'sale_of_going_concern']
EXEMPT_CATEGORIES = ['medical_services', 'educational_services', 'financial_services', 'residential_rent']
