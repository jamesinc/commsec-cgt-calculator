#
# This tool works by accumulating all your (ASX) shares and ETF units over time and executing sale transactions against
# the accumulated holdings by date, respecting the FIFO model.
# https://www.ato.gov.au/Individuals/Capital-gains-tax/CGT-discount/#The12monthownershiprequirement

import csv
import argparse
from datetime import datetime
import re
from dateutil.relativedelta import relativedelta

parser = argparse.ArgumentParser("commsec-cgt")

parser.add_argument("--txn-data", help="CSV dump of your transaction history from CommSec (from beginning of time)")

args = parser.parse_args()

with open(args.txn_data) as fh:
  reader = csv.reader(fh, delimiter=',', quotechar="'")
  txn_rows = []

  for row in reader:
    if row[2][0] in ["B", "S"]:
      txn_rows.append(row)


  parsed_rows = []

holdings = {}
txn_regex = re.compile(r"([B|S])\s([0-9]+)\s([A-Z]+)\s@\s([0-9]+\.[0-9]+)")

for row in reversed(txn_rows):
  trans_date = datetime.strptime(row[0], r"%d/%m/%Y")
  action, unit_qty, ticker_code, unit_price = txn_regex.match(row[2]).groups()
  unit_qty = int(unit_qty)

  if not ticker_code in holdings:
    holdings[ticker_code] = []

  if action == "B":
    # Buying units
    holdings[ticker_code] += [{
      "purchase_price": float(unit_price),
      "purchase_date": trans_date
    }] * unit_qty

    print(f"Bought {unit_qty} units of {ticker_code} on {trans_date:%d/%m/%Y}")

  elif action == "S":
    # Selling units
    sell_price = float(unit_price)
    profit = 0
    cgt = 0
    units_being_sold = [holdings[ticker_code].pop(0) for _ in range(0, unit_qty)]

    # Now work out profit on each unit being sold + CGT applicable
    for unit in units_being_sold:
      unit_profit = sell_price - unit["purchase_price"]
      gross_profit_this_unit = sell_price - unit["purchase_price"]
      profit += gross_profit_this_unit
      cgt_this_unit = gross_profit_this_unit

      if unit_profit > 0:
        # To qualify for a CGT discount, you have to hold the asset for 12 months, not including the day
        # you purchased it or the day you sold it.
        if trans_date > unit["purchase_date"] + relativedelta(days=1) + relativedelta(months=12):
          cgt_this_unit = cgt_this_unit/2

      cgt += max([0, cgt_this_unit])

    print(f"Sold {unit_qty} units of {ticker_code} on {trans_date:%d/%m/%Y}")

    if unit_profit > 0:
      print(f"CAPITAL GAIN: $ {round(profit,2):.2f}")
      print(f"CGT FOR TAX:  $ {round(cgt,2):.2f}")
    else:
      print(f"CAPITAL LOSS: $ {round(profit,2):.2f}")

  else:
    raise ValueError(f"Action {action} was not understood (excpected 'B' or 'S')")