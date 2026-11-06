import re

from config import CATEGORY_KEYWORDS


def categorise_merchant(merchant):
    """Return the category for a merchant name.

    Keywords are matched as whole words, so "ola" matches "OLA CABS"
    but not "Chocolate". If nothing matches, the category is "Other".
    """

    merchant = str(merchant).lower()

    for category, keywords in CATEGORY_KEYWORDS.items():

        for keyword in keywords:

            pattern = rf"\b{re.escape(keyword)}\b"

            if re.search(pattern, merchant):
                return category

    return "Other"


def categorise_transactions(df):
    """Add a Category column to the DataFrame."""

    df = df.copy()

    df["Category"] = df["Merchant"].apply(categorise_merchant)

    return df