# Application Architecture Diagram


![Serverless Application Architecture Diagram](/A/imgs/SLArch.drawio.svg)

The application will be built using AWS serverless architecture. This will allow the application to automatically scale and reduce operation cost as billing is paid for by the number of requests made and the required computation.

1. General users will interface with the application with a web browser. Administrators will interact with the application through a API platform and authorized API key which will provide CRUD functionality.

2. AWS Route53 and CloudFront will be used to host the application. Route53 will provide DNS to assign a domain name to the application. CloudFront will provide a Content Delivery Network (CDN) for the application, by caching content at edge locations.

3. Calls to the application will be made through API Gateway. The API gateway will route the calls to the appropriate lambda function. It will also be used to validate the developers API key.

4. The CRUD API is intended for use by developers and administrators of the application and will be used to create, update and delete data in the database. The developer API will only be accessible with an authorised developer API key. To add or update data the api will connect to the Yahoo Finance API to retrieve data and store it in the database.

5. The view API will be used to query existing data in the database and route user views through flask. This API will have read-only access and will be exposed to the public for interacting with the application.

6. The Yahoo Finance API will be the source of truth for the data that is used in the application. The python packages `yfinance` or `yahoo_fin` will be used to retrieve data from Yahoo.

7. A DynamoDB table will be used to store the data. DynamoDB is a NoSQL database which offers high performance, scalability and reliability. DynamoDB groups data into collections of related tables. Each item has a unique key and a set of attributes. Other than the key and attributes DynamoDB tables are schema-less, making it suitable for storing assorted financial data for listed companies that may conform to various accounting standards.

# Dataflow Diagram

![Serverless Dataflow Diagram](/A/imgs/SLDFD.drawio.svg)

The dataflow diagram shows how data is utilised by the application.

There are two entities that interact with data in the application:

- Developers: developers can create, update and delete company tickers that are stored in the application database. Developers interface with the application through the developer API with an API key. They are able to make Create, Read Update and Delete calls to modify the data in the database used to store application data.

- Users: users interface with the application through the web browser. The application will provide a web interface for users to view and interact with the data in the database. Users will have read only access to the website database and can view data for a ticker, cash flow statements, balance sheet and summary information. The application will also provide functionality to visualize the data they have selected in a graph.
