#!/usr/bin/env python3

from datetime import date, datetime, timedelta
from calendar import monthrange

def add_months(sourcedate, months):
  month_num = sourcedate.month
  if month_num + months > 12:
    month_num = month_num + months - 12
    year = sourcedate.year + 1
  elif month_num + months < 1:
    month_num = month_num + months + 12
    year = sourcedate.year - 1
  else:
    month_num = month_num + months
    year = sourcedate.year
  return date(year, month_num, sourcedate.day)

def find_payday_for(given_date):
  # paid on second to last day of month
  day = monthrange(given_date.year, given_date.month)[1]
  work_days_sub = 0

  while True:
    prop_date = date(given_date.year, given_date.month, day)
    weekday = prop_date.weekday()
    if work_days_sub == 1 and weekday < 5:
      return prop_date
    day -= 1
    if weekday < 5:
      work_days_sub += 1
    if day < 0:
      raise Exception(f"Failed to find pay day for {given_date}")

def find_paydays():
  current = date.today()
  paydays = []

  for i in range(-6, 12):
    paydays.append(find_payday_for(add_months(current, i)))

  return paydays

if __name__ == "__main__":
  for payday in find_paydays():
    month_name = payday.strftime("%B")
    print(f"{payday:%Y-%m-%d} Pay day for {month_name} {payday.year}")