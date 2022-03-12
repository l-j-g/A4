# ASX DB: Manual Application Testing 

In addition to the type testing proivded in the test_app.py file, the following manual tests were conducted: 


### Endpoint Testing



| End point                                     | Response | Behaviour                                           |
| --------------------------------------------- | -------- | --------------------------------------------------- |
| '/'                                           | 200      | Display Homepage                                    |
| '/search/'                                    | 200      | Display Search Page                                 |
| '/search/groupBy=<'group'>&orderBy=<'direction'>' | 200      | Display results filtered in order                   |
| '/search/<'page'>'                              | 200      | Display next page of relevent results               |
| '/ticker/'                                    | 308      | Redirect to search page (no ticker provided)        |
| '/ticker/<'ticker'>'                            | 200      | Redirect to ticker info page                        |
| '/ticker/<bad_ticker>'                        | 308      | Redirect to search page (ticker could not be found) |
| '/ticker/<'ticker'>/info'                       | 200      | Display ticker info page                            |
| '/ticker/<'ticker'>/cash_flow'                  | 200      | Display ticker cash flow page                       |
| '/ticker/<'ticker'>/income_statement'           | 200      | Display ticker income statement page                |

 
## UI Testing

### Nav Bar:

Working as intended, displays either home page or search page.

### Search page: 
  
- Search ticker:
  - Ticker can be manually searched by entering ticker in the search bar.
  - If the ticker information about that ticker will be displayed.
  - If the ticker can not be found the user will be redirected to the search page. 
  - Working as intended.

- Filter:
  -  UI has been implemented but is not yet working.
  - BUG: Further development is required to implement the filter functionality.

- Results table:
  - Displays 25 results per page
  - Results are sorted by the table header in either asc or desc order.
  - Working as intended.

- Pagination:
  - Pagination is working as intended.
  - Optional Next and Previous buttons are displayed.
  - Page Key is stored in cookies allowing the user to navigate between pages.

### Ticker Page
- Nav Bar 
  - Working as intended.
  - Allows selection between ticker info, cash flow and income statement.

- Info/Cash Flow/Income Statement/Balancesheet
    - Database data is displayed in tabular forms
    - BUG: The table columns are not always in the correct order e.g. 2018, 2019, 2021, 2020 **Fixed 12/03**