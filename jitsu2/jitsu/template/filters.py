FILTERS = {
    'FILTER_lower': lambda x: x.lower(),
    'FILTER_upper': lambda x: x.upper(),
    'FILTER_title': lambda x: x.title(),
    'FILTER_blue' : lambda x: '<blue>' + x + "</blue>",
    'FILTER_div' : lambda x: '<div>' + x + '</div>'
}