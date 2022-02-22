# Dataflow Diagram

## 

Store the data in a DynamoDB table. 
A single table should be used for all data required by the application.

## Access Patterns 

entity : tickers

- CRUD operations 
- Find summary information of a ticker
- Find cash flow statements of a ticker
- Find balance sheet of a ticker
- Find a ticker by name

entity : users

- CRUD operations
- Find user by username 
- Find password for user
- For tickers that user follows


Entity 

ticker
summary
cash_flow
balance_sheet



