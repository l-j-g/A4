# Application Architecture Diagram


![Serverless Application Architecture Diagram](/A/imgs/SLAA.svg)

The application will be built using AWS serverless architecture.

1. General users will interface with the application with a web browser. Administrators will interact with the application through a API platform and authorized API key. 

2. AWS Route53 and CloudFront will be used to host the application. Route53 will provide DNS to assign a domain name to the application. CloudFront will provide a Content Delivery Network (CDN) for the application, by caching content at edge locations.

3. Calls to the application will be made through API Gateway. The API gateway will route the calls to the appropriate lambda function. It will also be used to validate the developers API key.

4. The developer API will be used to create, update and delete data in the database. The developer API will only be accessible with a developer API. To add or update data the api will utilise the Yahoo Finance API to retrieve data and store it in the database.

5. The query API will be used to query existing data in the database, it will have read-only access.

6. The Yahoo Finance API will be the source of truth for the data that is used in the application. The python packages `yfinance` or `yahoo_fin` will be used to retrieve data from Yahoo.

7. A DynamoDB table will be used to store the data. DynamoDB is a NoSQL database which offers high performance, scalability and reliability. DynamoDB groups data into collections of related tables. Each item has a unique key and a set of attributes. Other than the key and attributes DynamoDB tables are schema-less, making it suitable for storing assorted financial data for listed companies that may conform to various accounting standards.

8. A VPC gateway will allow the application to be deployed to a cloud environment. The VPC will be used to provide a secure connection between the application and the database.

9. Static content will be served from an S3 bucket. The bucket will be used to store content such as images, CSS and HTML templates.

# Dataflow Diagram

![Serverless Dataflow Diagram](/A/imgs/ASXSLDFD.drawio.svg)

The dataflow diagram shows how data is utilised by the application.

There are two entities that interact with data in the application:

- Developers: developers can create, update and delete company tickers that are stored in the application database. Developers interface with the application through the developer API with an API key. They are able to make Create, Read Update and Delete calls to modify the data in the database used to store application data.

- Users: users interface with the application through the web browser. The application will provide a web interface for users to view and interact with the data in the database. Users will have ready only access to the website database and can view data for a ticker, cash flow statements, balance sheet and summary information. The application will also provide functionality to visualize the data they have selected in a graph.
