import re


orderable_date_regex = re.compile(r"(\d{2})\.(\d{2}).(\d{4})")
def orderable_date(d):
    if isinstance(d, str) and orderable_date_regex.match(d):
        return int(orderable_date_regex.sub(r"\3\2\1",d))
    else:
        return float("nan")
orderable_dates = lambda dates: [orderable_date(d) for d in dates]

camel_to_snake_case_regex = re.compile(r"([A-Z]+)")

def camel_to_snake_case(s):
    return ''.join(['_'+c.lower() if c.isupper() else c for c in s]).lstrip('_')