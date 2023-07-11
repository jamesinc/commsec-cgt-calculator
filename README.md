# CommSec CGT calculator

Use this tool at your own risk. I make no guarantees about its accuracy or
completeness, and I know there are edge-cases that this tool will not
handle. **Caveat emptor!**

This tool calculates your net income in terms of your Capital Gains Tax (CGT)
obligations. Shares that were sold less than twelve months after their
purchase are taxed at 100% of the profit, and shares held for twelve months
or longer are discounted 50% for tax purposes.

By scanning your CommSec transaction history, this tool is able to calculate
the age of each share at the time it was sold.

To use the tool, you will need to export your entire CommSec transaction history
from the beginning of time. This is in Portfolio > Accounts > Transactions,
then enter a date range that starts before you opened your CommSec account,
and ends after the FY you are calcualting your CGT obligations for. Hit Search,
Download the result as a CSV, and use this tool to parse it like so:

```sh
pipenv install
pipenv run python calculate_cgt.py --txn-data data.csv
```