import csv
import requests
from datetime import datetime

def get_exchange_rate(date_str, base_currency, target_currency='NOK'):
    """Fetch historical exchange rate from base_currency to NOK unless base is already NOK."""
    if base_currency == target_currency:
        return 1.0  # No conversion needed
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        url = f"https://api.frankfurter.app/{date.isoformat()}"
        params = {'from': base_currency, 'to': target_currency}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        rate = data['rates'].get(target_currency)
        if rate is None:
            raise ValueError(f"No rate for {base_currency} to {target_currency} on {date_str}")
        return rate
    except Exception as e:
        print(f"Error fetching rate for {date_str} ({base_currency}): {e}")
        return 0.0

def format_currency(value, currency):
    return f"{currency} {value:,.0f}".replace(',', '\\,')

with open('grants.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    rows = list(reader)

with open('grants_table.tex', 'w') as texfile:
    texfile.write(r"\begin{longtable}{llr rllp{8cm}l}" + "\n")
    texfile.write(r"\textbf{Start} & \textbf{End} & \textbf{Total} & \textbf{My Share} & \textbf{Funding Agency} & \textbf{Role} & \textbf{Title} \\" + "\n")
    texfile.write(r"\hline" + "\n")

    for row in rows:
        start = row['Start Date'].strip()
        end = row['End Date'].strip()
        base = row['Currency'].strip().upper()
        funder = row['Funding Agency']
        role = row['Role']
        title = row['Title']

        total_orig = float(row['Total Amount'])
        my_amount = float(row['My Amount'])

        # Convert only if needed
        if base == 'NOK':
            my_nok = my_amount
        else:
            rate = get_exchange_rate(start, base)
            my_nok = my_amount * rate

        texfile.write(f"{start} & {end} & {format_currency(total_orig, base)} & {format_currency(my_nok, 'NOK')} & "
                      f"{funder} & {role} & {title} \\\\\n")

    texfile.write(r"\end{longtable}" + "\n")
