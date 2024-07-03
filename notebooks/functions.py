import pandas as pd
import os
import ssl
import certifi
import time
from urllib.request import urlopen
from urllib.parse import urlencode
import json

# Create a custom SSL context
context = ssl.create_default_context(cafile=certifi.where())

# Now you can access the environment variables
apikey = os.getenv('FMP_SECRET_KEY')


def company_profile_url(ticker, apikey=apikey):
	endpoint = 'https://financialmodelingprep.com/api/v3/profile/'
	url = f'{endpoint}{ticker}?apikey={apikey}'
	return url

def stock_screener(apikey=apikey, **kwargs):
	endpoint = 'https://financialmodelingprep.com/api/v3/stock-screener'
	params = {'apikey': apikey}
	params.update(kwargs)
	query_string = urlencode(params)
	url = f'{endpoint}?{query_string}'
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
				display(Image(image_data))
		except Exception as e:
			print(f"Error fetching image: {e}")


def get_indicators(ticker, indicators, timeframe='1day', period=14, apikey=apikey):
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
		df = df.set_index('date')
		df_list.append(df)

	final_df = pd.concat(df_list, axis=1, join='outer')
	final_df.index = pd.to_datetime(final_df.index)
		
	return final_df

def stock_summary_table(stock_data):
	columns = stock_data[0]
	table = pd.DataFrame(stock_data)[['symbol', 'name', 'price', 'marketCap', 'exchange']]
	melted = table.melt().set_index('variable', drop=True)
	return melted


def get_all_data(tickers):
	data = []
	for ticker in tickers:
		historical_data = get_jsonparsed_data(historical_url(ticker))
		data.append(historical_data)

	# List of keys to keep in each dictionary
	keys_to_keep = ['date', 'open', 'high', 'low', 'close', 'volume', 'vwap']

	for item in data:
		historical = item['historical']
		symbol = item['symbol']

		# Modify each entry in the historical list
		for entry in historical:
			entry['symbol'] = symbol
			# Keep only the necessary keys
			for key in list(entry.keys()):
				if key not in keys_to_keep and key != 'symbol':
					del entry[key]
	
	return data


def lagging_features_target(df):
	df = df.copy()
	df['minus_10_price'] = df.close.shift(10)
	df['minus_5_price'] = df.close.shift(5)
	df['minus_4_price'] = df.close.shift(4)
	df['minus_3_price'] = df.close.shift(3)
	df['minus_2_price'] = df.close.shift(2)
	df['target'] = df.close.shift(-3)
	df = df.dropna()
	return df