
import json
import re

from functools import lru_cache
from decimal import Decimal, InvalidOperation
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


# ==========================================
# 1. CURRENCY API CONFIGURATION
# ==========================================

API_BASE_URL = "https://api.frankfurter.dev/v2"


# ==========================================
# 2. CURRENCY CONVERSION
# ==========================================

def convert_currency(amount, from_currency, to_currency):

    # Convert currency codes to uppercase
    from_currency = str(from_currency).strip().upper()
    to_currency = str(to_currency).strip().upper()

    # Validate currency codes
    if not re.fullmatch(r"[A-Z]{3}", from_currency):
        raise ValueError("Invalid source currency code.")

    if not re.fullmatch(r"[A-Z]{3}", to_currency):
        raise ValueError("Invalid target currency code.")

    # Validate amount
    try:
        amount = Decimal(str(amount))

    except (InvalidOperation, ValueError):
        raise ValueError("Please provide a valid amount.")

    if not amount.is_finite() or amount < 0:
        raise ValueError("Amount must be a non-negative number.")

    # Same currency conversion
    if from_currency == to_currency:

        return {
            "amount": float(amount),
            "from_currency": from_currency,
            "to_currency": to_currency,
            "exchange_rate": 1.0,
            "converted_amount": float(amount),
            "rate_date": None
        }

    # Construct API URL
    api_url = (
        f"{API_BASE_URL}/rate/"
        f"{from_currency}/{to_currency}"
    )

    try:

        # Request exchange rate
        with urlopen(api_url, timeout=10) as response:

            data = json.loads(
                response.read().decode("utf-8")
            )

    except HTTPError as error:

        if error.code == 404:
            raise ValueError(
                "The requested currency pair is not supported."
            )

        if error.code == 429:
            raise ConnectionError(
                "The currency API is receiving too many requests. "
                "Please try again later."
            )

        if error.code >= 500:
            raise ConnectionError(
                "The currency API is temporarily unavailable. "
                "Please try again later."
            )

        raise ConnectionError(
            f"Currency API returned HTTP error {error.code}."
        )

    except (URLError, TimeoutError, OSError) as error:

        raise ConnectionError(
            "Unable to connect to the currency exchange API."
        ) from error

    # Check API response
    if "rate" not in data:

        raise ValueError(
            "Exchange rate information is unavailable."
        )

    # Calculate converted amount
    exchange_rate = Decimal(str(data["rate"]))

    converted_amount = (
        amount * exchange_rate
    ).quantize(Decimal("0.01"))

    # Return conversion information
    return {
        "amount": float(amount),
        "from_currency": from_currency,
        "to_currency": to_currency,
        "exchange_rate": float(exchange_rate),
        "converted_amount": float(converted_amount),
        "rate_date": data.get("date")
    }

# ==========================================
# 3. CURRENCY NAME MAPPING
# ==========================================

CURRENCY_ALIASES = {
    "usd": "USD",
    "dollar": "USD",
    "dollars": "USD",
    "us dollar": "USD",
    "us dollars": "USD",

    "myr": "MYR",
    "ringgit": "MYR",
    "malaysian ringgit": "MYR",

    "sgd": "SGD",
    "singapore dollar": "SGD",
    "singapore dollars": "SGD",

    "eur": "EUR",
    "euro": "EUR",
    "euros": "EUR",

    "gbp": "GBP",
    "pound": "GBP",
    "pounds": "GBP",
    "british pound": "GBP",

    "jpy": "JPY",
    "yen": "JPY",
    "japanese yen": "JPY",

    "aud": "AUD",
    "australian dollar": "AUD",
    "australian dollars": "AUD",

    "cad": "CAD",
    "canadian dollar": "CAD",
    "canadian dollars": "CAD",

    "cny": "CNY",
    "yuan": "CNY",
    "chinese yuan": "CNY",

    "thb": "THB",
    "baht": "THB",
    "thai baht": "THB",

    "idr": "IDR",
    "rupiah": "IDR",
    "indonesian rupiah": "IDR",

    "inr": "INR",
    "rupee": "INR",
    "rupees": "INR",
    "indian rupee": "INR"
}
# ==========================================
# 4. AUTOMATIC CURRENCY NAME RETRIEVAL
# ==========================================

@lru_cache(maxsize=1)
def get_currency_aliases():

    # Start with our manually defined currency aliases
    aliases = CURRENCY_ALIASES.copy()

    # Request the supported currencies from Frankfurter
    api_url = f"{API_BASE_URL}/currencies"

    try:

        with urlopen(api_url, timeout=10) as response:

            currencies = json.loads(
                response.read().decode("utf-8")
            )

        # Add currency codes and official names automatically
        for currency in currencies:

            if currency.get("type") != "currency":
                continue

            currency_code = currency["iso_code"]
            currency_name = currency["name"].lower()

            aliases[currency_code.lower()] = currency_code
            aliases[currency_name] = currency_code

    except (HTTPError, URLError, TimeoutError, OSError, ValueError, KeyError):

        # Continue using manual aliases if the API is unavailable
        pass

    return aliases
# ==========================================
# 5. CURRENCY QUESTION DETECTION
# ==========================================

def parse_currency_question(user_question):

    # Convert question to lowercase
    question = user_question.lower().strip()

    # Sort aliases by length (longest first)
    # This helps recognise names such as "malaysian ringgit"
    # before shorter names such as "ringgit"
    currency_aliases = get_currency_aliases()

    aliases = sorted(
        currency_aliases.keys(),
        key=len,
        reverse=True
    )

    # Create a pattern to recognise currency names
    alias_pattern = (
        r"(?<![a-z])(?:"
        + "|".join(re.escape(alias) for alias in aliases)
        + r")(?![a-z])"
    )

    # Find all currency names in the question
    currency_matches = list(
        re.finditer(alias_pattern, question)
    )

    # Find the amount in the question
    amount_match = re.search(
        r"(?<!\w)(\d+(?:,\d{3})*(?:\.\d+)?|\.\d+)(?!\w)",
        question
    )

    # Check whether an amount was provided
    if not amount_match:
        return None

    # Check whether at least two currencies were provided
    if len(currency_matches) < 2:
        return None

    # Extract the amount
    amount = amount_match.group(1).replace(",", "")

    # Extract source and target currencies
    source_name = currency_matches[0].group()
    target_name = currency_matches[1].group()

    # Convert currency names into currency codes
    from_currency = currency_aliases[source_name]
    to_currency = currency_aliases[target_name]

    # Return the extracted information
    return {
        "amount": amount,
        "from_currency": from_currency,
        "to_currency": to_currency
    }