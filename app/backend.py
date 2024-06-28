import pandas as pd
import numpy as np

import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from fmp_python.fmp import FMP
import ssl
import time
from urllib.request import urlopen
from urllib.parse import urlencode
import certifi
import json
from IPython.display import Image, display

import matplotlib.pyplot as plt
import plotly.express as px

from notebooks import config
from notebooks.functions import trim_and_lower


# Create a custom SSL context
context = ssl.create_default_context(cafile=certifi.where())

# Now you can access the environment variables
apikey = os.getenv('FMP_SECRET_KEY')


def stock_screener(apikey=apikey, **kwargs):
	endpoint = 'https://financialmodelingprep.com/api/v3/stock-screener'
	params = {'apikey': apikey}
	params.update(kwargs)
	query_string = urlencode(params)
	url = f'{endpoint}?{query_string}'
	return url

def company_profile_url(ticker, apikey=apikey):
	endpoint = 'https://financialmodelingprep.com/api/v3/profile/'
	url = f'{endpoint}{ticker}?apikey={apikey}'
	return url

def full_quote_url(ticker, apikey=apikey):
	endpoint = 'https://financialmodelingprep.com/api/v3/quote/'
	url = f'{endpoint}{ticker}?apikey={apikey}'
	return url

def historical_url(ticker, apikey=apikey):
	endpoint = 'https://financialmodelingprep.com/api/v3/historical-price-full/'
	url = f'{endpoint}{ticker}?apikey={apikey}'
	return url

def technical_indicator_url(timeframe, ticker, ind_type, period, apikey=apikey):
	endpoint = 'https://financialmodelingprep.com/api/v3/technical_indicator/'
	ticker = ticker
	url = f'{endpoint}{timeframe}/{ticker}?type={ind_type}&period={period}&apikey={apikey}'
	return url

def historical_rating_url(ticker, apikey=apikey):
	endpoint = 'https://financialmodelingprep.com/api/v3/historical-rating/'
	url = f'{endpoint}{ticker}?apikey={apikey}'
	return url

def get_jsonparsed_data(url, retries=3, timeout=10):
	"""
	Fetch JSON data from the provided URL and return it as a Python dictionary.
	
	Parameters
	----------
	url : str
		The URL to fetch data from.
	retries : int
		The number of retries for the request in case of failure.
	timeout : int
		The timeout for the request in seconds.

	Returns
	-------
	dict
		The parsed JSON data.
	"""
	context = ssl.create_default_context(cafile=certifi.where())
	for attempt in range(retries):
		try:
			with urlopen(url, context=context, timeout=timeout) as response:
				data = response.read().decode("utf-8")
				return json.loads(data)
		except Exception as e:
			print(f"Attempt {attempt + 1} failed: {e}")
			if attempt < retries - 1:
				time.sleep(2 ** attempt)  # Exponential backoff
			else:
				raise

def display_company_logo(ticker, apikey=apikey, retries=3, timeout=10):
	endpoint = 'https://financialmodelingprep.com/image-stock/'
	url = f'{endpoint}{ticker}.png?apikey={apikey}'
	for attempt in range(retries):
		try:
			with urlopen(url, context=context) as response:
				image_data = response.read()
				return image_data
		except Exception as e:
			print(f"Error fetching image: {e}")
			if attempt < retries - 1:
				print(f'Retrying... ({attempt + 1} / {retries})')
			else:
				raise
	return None


def get_indicators(timeframe, ticker, indicators, period, apikey=apikey):
	urls = {}
	for indicator in indicators:
		url = technical_indicator_url(timeframe, ticker, indicator, period, apikey)
		urls[indicator] = url
	
	ind_data = {}
	for key, value in urls.items():
		data = get_jsonparsed_data(value)
		filtered_data = [{'date': entry['date'], key: entry[key]} for entry in data if key in entry]
		ind_data[key] = filtered_data
	
	df_list = []
	for indicator, data in ind_data.items():
		df = pd.DataFrame(data)
		#display(df.head(2))
		df = df.set_index('date')
		#display(df.head(2))
		df_list.append(df)

	final_df = pd.concat(df_list, axis=1, join='outer')
		
	return final_df


#def stock_summary_table(stock_data):
#	columns = stock_data[0]
#	table = pd.DataFrame(stock_data)[['symbol', 'name', 'price', 'marketCap', 'exchange']].set_index('symbol', drop=True)
#	return table


def stock_summary_table(stock_data):
	columns = stock_data[0]
	table = pd.DataFrame(stock_data)[['symbol', 'companyName', 'price', 'sector', 'industry', 'exchangeShortName', 'beta']]#.set_index('symbol', drop=True)
	melted = table.melt().set_index('variable', drop=True)
	return melted

