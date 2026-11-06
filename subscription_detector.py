import pandas as pd

# A payment counts as a subscription only if it repeats with similar
# amounts and at regular intervals.
AMOUNT_TOLERANCE = 0.10  # amounts may differ by up to 10%

# (name, expected days between payments, allowed difference in days)
INTERVALS = [
    ("Weekly", 7, 2),
    ("Monthly", 30, 5),
    ("Yearly", 365, 10),
]


def detect_recurring_payments(df):
    """Find merchants that look like subscriptions.

    A merchant is flagged when it has 2+ payments, the amounts are
    within 10% of each other, and the gaps between payments are
    roughly weekly, monthly or yearly.
    """

    columns = [
        "Merchant", "Frequency", "Occurrences",
        "Average_Amount", "Total_Amount",
    ]

    data = df.copy()

    # Ignore refunds and zero-value rows
    data = data[data["Total_Cost"] > 0]

    results = []

    for merchant, group in data.groupby("Merchant"):

        if len(group) < 2:
            continue

        amounts = group["Total_Cost"]
        average = amounts.mean()

        # Amounts must be similar
        if (amounts.max() - amounts.min()) > average * AMOUNT_TOLERANCE:
            continue

        # Gaps between payments must be regular
        dates = group["Date"].dropna().sort_values()
        gaps = dates.diff().dt.days.dropna()

        if gaps.empty:
            continue

        median_gap = gaps.median()

        for name, days, allowed in INTERVALS:

            if abs(median_gap - days) <= allowed:

                results.append({
                    "Merchant": merchant,
                    "Frequency": name,
                    "Occurrences": len(group),
                    "Average_Amount": round(average, 2),
                    "Total_Amount": round(amounts.sum(), 2),
                })
                break

    if not results:
        return pd.DataFrame(columns=columns)

    return (
        pd.DataFrame(results)
        .sort_values("Occurrences", ascending=False)
        .reset_index(drop=True)
    )