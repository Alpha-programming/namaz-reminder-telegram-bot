muslim_countries = {
    "Afghanistan": "AF",
    "Albania": "AL",
    "Algeria": "DZ",
    "Azerbaijan": "AZ",
    "Bahrain": "BH",
    "Bangladesh": "BD",
    "Brunei": "BN",
    "Burkina Faso": "BF",
    "Chad": "TD",
    "Comoros": "KM",
    "Djibouti": "DJ",
    "Egypt": "EG",
    "Gambia": "GM",
    "Guinea": "GN",
    "Indonesia": "ID",
    "Iran": "IR",
    "Iraq": "IQ",
    "Jordan": "JO",
    "Kazakhstan": "KZ",
    "Kuwait": "KW",
    "Kyrgyzstan": "KG",
    "Lebanon": "LB",
    "Libya": "LY",
    "Malaysia": "MY",
    "Maldives": "MV",
    "Mali": "ML",
    "Mauritania": "MR",
    "Morocco": "MA",
    "Niger": "NE",
    "Oman": "OM",
    "Pakistan": "PK",
    "Palestine": "PS",
    "Qatar": "QA",
    "Saudi Arabia": "SA",
    "Senegal": "SN",
    "Sierra Leone": "SL",
    "Somalia": "SO",
    'South Korea': 'KR',
    "Sudan": "SD",
    "Syria": "SY",
    "Tajikistan": "TJ",
    "Tunisia": "TN",
    "Turkey": "TR",
    "Turkmenistan": "TM",
    "United Arab Emirates": "AE",
    "Uzbekistan": "UZ",
    "Western Sahara": "EH",
    "Yemen": "YE"
}

import requests
def get_cities_for_country(country_code):
    username = "alpha_programming"
    url = f"http://api.geonames.org/searchJSON?country={country_code}&featureClass=P&maxRows=10&username={username}"

    response = requests.get(url)
    data = response.json()

    if "geonames" in data:
        cities = [city["name"] for city in data["geonames"]]

        return cities


    return []