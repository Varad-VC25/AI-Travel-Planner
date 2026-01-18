import requests
from typing import List, Dict

# --- Data: Country to Currency Mapping ---
# This serves both as your list of countries and your currency lookup
COUNTRY_CURRENCY_MAP = {
    "Afghanistan": "AFN", "Albania": "ALL", "Algeria": "DZD", "Andorra": "EUR", "Angola": "AOA",
    "Argentina": "ARS", "Armenia": "AMD", "Australia": "AUD", "Austria": "EUR", "Azerbaijan": "AZN",
    "Bahamas": "BSD", "Bahrain": "BHD", "Bangladesh": "BDT", "Barbados": "BBD", "Belarus": "BYN",
    "Belgium": "EUR", "Belize": "BZD", "Benin": "XOF", "Bhutan": "BTN", "Bolivia": "BOB",
    "Bosnia and Herzegovina": "BAM", "Botswana": "BWP", "Brazil": "BRL", "Brunei": "BND", "Bulgaria": "BGN",
    "Burkina Faso": "XOF", "Burundi": "BIF", "Cambodia": "KHR", "Cameroon": "XAF", "Canada": "CAD",
    "Central African Republic": "XAF", "Chad": "XAF", "Chile": "CLP", "China": "CNY", "Colombia": "COP",
    "Comoros": "KMF", "Congo (Crazzaville)": "XAF", "Congo (Kinshasa)": "CDF", "Costa Rica": "CRC",
    "Cote d'Ivoire": "XOF", "Croatia": "EUR", "Cuba": "CUP", "Cyprus": "EUR", "Czechia": "CZK",
    "Denmark": "DKK", "Djibouti": "DJF", "Dominica": "XCD", "Dominican Republic": "DOP", "Ecuador": "USD",
    "Egypt": "EGP", "El Salvador": "USD", "Equatorial Guinea": "XAF", "Eritrea": "ERN", "Estonia": "EUR",
    "Eswatini": "SZL", "Ethiopia": "ETB", "Fiji": "FJD", "Finland": "EUR", "France": "EUR",
    "Gabon": "XAF", "Gambia": "GMD", "Georgia": "GEL", "Germany": "EUR", "Ghana": "GHS",
    "Greece": "EUR", "Grenada": "XCD", "Guatemala": "GTQ", "Guinea": "GNF", "Guinea-Bissau": "XOF",
    "Guyana": "GYD", "Haiti": "HTG", "Honduras": "HNL", "Hungary": "HUF", "Iceland": "ISK",
    "India": "INR", "Indonesia": "IDR", "Iran": "IRR", "Iraq": "IQD", "Ireland": "EUR",
    "Israel": "ILS", "Italy": "EUR", "Jamaica": "JMD", "Japan": "JPY", "Jordan": "JOD",
    "Kazakhstan": "KZT", "Kenya": "KES", "Kiribati": "AUD", "Kosovo": "EUR", "Kuwait": "KWD",
    "Kyrgyzstan": "KGS", "Laos": "LAK", "Latvia": "EUR", "Lebanon": "LBP", "Lesotho": "LSL",
    "Liberia": "LRD", "Libya": "LYD", "Liechtenstein": "CHF", "Lithuania": "EUR", "Luxembourg": "EUR",
    "Madagascar": "MGA", "Malawi": "MWK", "Malaysia": "MYR", "Maldives": "MVR", "Mali": "XOF",
    "Malta": "EUR", "Mauritania": "MRU", "Mauritius": "MUR", "Mexico": "MXN", "Micronesia": "USD",
    "Moldova": "MDL", "Monaco": "EUR", "Mongolia": "MNT", "Montenegro": "EUR", "Morocco": "MAD",
    "Mozambique": "MZN", "Myanmar": "MMK", "Namibia": "NAD", "Nauru": "AUD", "Nepal": "NPR",
    "Netherlands": "EUR", "New Zealand": "NZD", "Nicaragua": "NIO", "Niger": "XOF", "Nigeria": "NGN",
    "North Korea": "KPW", "North Macedonia": "MKD", "Norway": "NOK", "Oman": "OMR", "Pakistan": "PKR",
    "Palau": "USD", "Panama": "PAB", "Papua New Guinea": "PGK", "Paraguay": "PYG", "Peru": "PEN",
    "Philippines": "PHP", "Poland": "PLN", "Portugal": "EUR", "Qatar": "QAR", "Romania": "RON",
    "Russia": "RUB", "Rwanda": "RWF", "Saint Kitts and Nevis": "XCD", "Saint Lucia": "XCD",
    "Saint Vincent and the Grenadines": "XCD", "Samoa": "WST", "San Marino": "EUR", "Sao Tome and Principe": "STN",
    "Saudi Arabia": "SAR", "Senegal": "XOF", "Serbia": "RSD", "Seychelles": "SCR", "Sierra Leone": "SLL",
    "Singapore": "SGD", "Slovakia": "EUR", "Slovenia": "EUR", "Solomon Islands": "SBD", "Somalia": "SOS",
    "South Africa": "ZAR", "South Korea": "KRW", "South Sudan": "SSP", "Spain": "EUR", "Sri Lanka": "LKR",
    "Sudan": "SDG", "Suriname": "SRD", "Sweden": "SEK", "Switzerland": "CHF", "Syria": "SYP",
    "Taiwan": "TWD", "Tajikistan": "TJS", "Tanzania": "TZS", "Thailand": "THB", "Timor-Leste": "USD",
    "Togo": "XOF", "Tonga": "TOP", "Trinidad and Tobago": "TTD", "Tunisia": "TND", "Turkey": "TRY",
    "Turkmenistan": "TMT", "Tuvalu": "AUD", "Uganda": "UGX", "Ukraine": "UAH", "United Arab Emirates": "AED",
    "United Kingdom": "GBP", "United States of America": "USD", "Uruguay": "UYU", "Uzbekistan": "UZS",
    "Vanuatu": "VUV", "Venezuela": "VES", "Vietnam": "VND", "Yemen": "YER", "Zambia": "ZMW", "Zimbabwe": "ZWL"
}

def get_currency_for_country(country: str) -> str:
    return COUNTRY_CURRENCY_MAP.get(country, "USD")

def convert_currency(amount: float, from_curr: str, to_curr: str) -> float:
    try:
        url = f"https://open.er-api.com/v6/latest/{from_curr}"
        response = requests.get(url)
        data = response.json()
        if data["result"] == "success":
            rate = data["rates"].get(to_curr, 1.0)
            return round(amount * rate, 2)
    except Exception:
        pass
    return amount

def calculate_budget_split(total_budget: float, days: int, interests: List[str], travelers: int = 1, currency: str = "USD") -> Dict:
    # Base split logic
    split = {
        "Accommodation": 0.30,
        "Food": 0.25,
        "Transport": 0.20,
        "Activities": 0.15,
        "Misc": 0.10
    }
    
    # Interest-based adjustments
    if "Adventure" in interests or "Culture" in interests:
        split["Activities"] += 0.05
        split["Accommodation"] -= 0.05
        
    if "Food" in interests:
        split["Food"] += 0.05
        split["Misc"] -= 0.05

    budget_breakdown = {k: round(v * total_budget, 2) for k, v in split.items()}
    daily_per_person = round((total_budget / travelers) / days, 2)
    
    return {
        "total": total_budget,
        "currency": currency,
        "days": days,
        "travelers": travelers,
        "breakdown": budget_breakdown,
        "daily_per_person": daily_per_person
    }