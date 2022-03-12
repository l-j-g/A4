import unittest
import os
from app import app

os.environ['TICKERS_TABLE'] = 'Tickers'

class TestSite(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.client = app.test_client()
    
    def test_landing(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'ASX_DB: Homepage', response.data)

    def test_ticker_index(self):
        # we use the client to make a request
        response = self.client.get("/search/")
        # Now we can perform tests on the response
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<h1>Search Ticker</h1>', response.data)
    
    def test_bad_search(self):
        response = self.client.post("/search/", data={"ticker": "XXXX"})
        self.assertEqual(response.status_code, 302)
        self.assertIn(b'Sorry, we could not', response.data)

    def test_get_ticker(self):
        response = self.client.get('/ticker/88E')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'ASX_DB: Ticker Details', response.data)

    def test_get_ticker_info(self):
        response = self.client.get('/ticker/88E/info')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'ASX_DB: Ticker Details', response.data)

    def test_get_ticker_cashflow(self):
        response = self.client.get('/ticker/88E/cash_flow')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'ASX_DB: Cash Flow', response.data)

    def test_get_balancesheet(self):
        response = self.client.get('/ticker/88E/balance_sheet')
        self.assertEqual(response.status_code, 200) 
        self.assertIn(b'ASX_DB: Balance Sheet', response.data)

    def test_get_IncomeStatement(self):
        response = self.client.get('/ticker/88E/income_statement')
        self.assertEqual(response.status_code, 200) 
        self.assertIn(b'ASX_DB: Income Statement', response.data)