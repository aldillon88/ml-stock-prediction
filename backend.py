import pandas as pd
import numpy as np
import streamlit as st

import os
import sys
import joblib
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
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#from notebooks import config


# Create a custom SSL context
context = ssl.create_default_context(cafile=certifi.where())

# Now you can access the environment variables
#apikey = os.getenv('FMP_SECRET_KEY')

# Access the API key from Streamlit secrets
#apikey = st.secrets["api"]["FMP_SECRET_KEY"]
apikey = st.secrets["FMP_SECRET_KEY"]

# Other variables
indicators = ['dema', 'tema', 'williams', 'rsi']
features = ['vwap', 'dema', 'tema', 'williams', 'rsi', 'minus_10_price', 'minus_5_price', 'minus_4_price', 'minus_3_price', 'minus_2_price']
close = ['close']


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

def historical_url(ticker, apikey=apikey, **kwargs):
	endpoint = 'https://financialmodelingprep.com/api/v3/historical-price-full/'
	params = {'apikey': apikey}
	params.update(kwargs)
	query_string = urlencode(params)
	url = f'{endpoint}{ticker}?{query_string}'
	return url

def technical_indicator_url(timeframe, ticker, ind_type, period, apikey=apikey, **kwargs):
	endpoint = 'https://financialmodelingprep.com/api/v3/technical_indicator/'
	params = {
		'apikey': apikey,
		'type': ind_type,
		'period': period
	}
	params.update(kwargs)
	query_string = urlencode(params)
	url = f'{endpoint}{timeframe}/{ticker}?{query_string}'
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


def get_indicators(ticker, indicators=indicators, timeframe='1day', period=14, apikey=apikey, **kwargs):
	urls = {}
	for indicator in indicators:
		url = technical_indicator_url(timeframe, ticker, indicator, period, apikey, **kwargs)
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


@st.cache_data
def stock_screener_table(ticker, **kwargs):
	screen = get_jsonparsed_data(stock_screener(**kwargs))
	df = pd.DataFrame(screen)[['symbol', 'companyName', 'exchangeShortName', 'country', 'beta']]
	df = df[~df.symbol.str.contains(ticker)].set_index('symbol')
	df.columns = ['Company', 'Exchange', 'Country', 'Beta']
	#df = df.drop(ticker)
	df = df.head(5)
	return df


def stock_summary_table(profile):
	#columns = profile[0]
	table = pd.DataFrame(profile)[['symbol', 'companyName', 'price', 'sector', 'industry', 'exchangeShortName', 'beta']]#.set_index('symbol', drop=True)
	melted = table.melt().set_index('variable', drop=True)
	return melted


def get_all_data(ticker, **kwargs):
	data = get_jsonparsed_data(historical_url(ticker, **kwargs))
	data = data['historical']
	
	# List of keys to keep in each dictionary
	keys_to_keep = ['date', 'open', 'high', 'low', 'close', 'volume', 'vwap']

	# Modify each entry in the historical list
	for entry in data:
			
		# Keep only the necessary keys
		for key in list(entry.keys()):
			if key not in keys_to_keep:
				del entry[key]

	data = pd.DataFrame(data).set_index('date', drop=True)
	data.index = pd.to_datetime(data.index)
	data = data.sort_index()
	return data


def lagging_features_target(df):
	df = df.copy()
	df['minus_10_price'] = df.close.shift(10)
	df['minus_5_price'] = df.close.shift(5)
	df['minus_4_price'] = df.close.shift(4)
	df['minus_3_price'] = df.close.shift(3)
	df['minus_2_price'] = df.close.shift(2)
	df = df.dropna()
	return df


@st.cache_data
def combine_data(ticker, **kwargs):
	price_data = get_all_data(ticker, **kwargs)
	ind_data = get_indicators(ticker, **kwargs)
	df = pd.concat([price_data, ind_data], axis=1)
	df = lagging_features_target(df)
	df = df.asfreq('D', method='ffill')
	return df


def predict_df(pred, close):
	predictions = close.copy()
	predictions['prediction'] = pred
	full_index = pd.date_range(start=predictions.index.min(), end=predictions.index.max() + pd.Timedelta(days=3), freq='D')
	predictions = predictions.reindex(full_index)
	predictions['prediction'] = predictions['prediction'].shift(3)
	predictions.close = predictions.close.fillna(predictions.prediction)
	return predictions[['close']]


def feature_close_split(df, features=features, close=close):
	features = df[features]
	close = df[close]
	return features, close
	

def predict(ticker, df):
	features, close = feature_close_split(df)
	models = {
		'GOOG': 'alphabet_stacking_regressor_model.pkl',
		'AMZN': 'amazon_stacking_regressor_model.pkl',
		'AAPL': 'apple_stacking_regressor_model.pkl',
		'META': 'meta_stacking_regressor_model.pkl',
		'MSFT': 'microsoft_stacking_regressor_model.pkl',
		'NVDA': 'nvidia_stacking_regressor_model.pkl',
		'TSLA': 'tesla_stacking_regressor_model.pkl'
	}

	scalers = {
		'GOOG': 'alphabet_normalizer.pkl',
		'AMZN': 'amazon_normalizer.pkl',
		'AAPL': 'apple_normalizer.pkl',
		'META': 'meta_normalizer.pkl',
		'MSFT': 'microsoft_normalizer.pkl',
		'NVDA': 'nvidia_normalizer.pkl',
		'TSLA': 'tesla_normalizer.pkl'
	}

	scaler = joblib.load('scalers/' + scalers[ticker])
	model = joblib.load('models/' + models[ticker])

	# Normalize features
	features_norm = scaler.transform(features)
	features_norm_df = pd.DataFrame(features_norm, columns=features.columns, index=features.index)

	# Make predictions
	pred = model.predict(features_norm_df)

	df = predict_df(pred, close)

	return df


def make_chart(df, stock_data):
	predicted_points = 3
	rsi = stock_data['rsi']
	rsi = rsi.reindex(df.index)
	
	fig = go.Figure()

	# Create the subplots
	fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_heights=[0.75, 0.25]
					)
	
	# Add the actual data line
	fig.add_trace(go.Scatter(x=df.index[:-predicted_points], y=df['close'][:-predicted_points], mode='lines', name='Actual'),row=1, col=1)
	
	# Add the predicted data line
	fig.add_trace(go.Scatter(x=df.index[-predicted_points-1:], y=df['close'][-predicted_points-1:], mode='lines', name='Predicted', line=dict(color='green')),row=1, col=1)
	
	# Add rsi line
	fig.add_trace(go.Scatter(x=df.index[:-predicted_points], y=rsi, mode='lines', name='RSI'),row=2, col=1)

	# Add oversold and overbought markers
	oversold = 30
	overbought = 70

	fig.add_hline(
		y=oversold,
		line_dash='dot',
		line_color='green',
		label=dict(
			text='oversold',
			textposition='start',
			font=dict(size=10, color='green'),
			yanchor='top',
		),
		row=2,
		col=1
	)

	fig.add_hline(
		y=overbought,
		line_dash="dot",
		line_color='red',
		label=dict(
			text="overbought",
			textposition="start",
			font=dict(size=10, color="red"),
			yanchor="bottom",
		),
		row=2,
		col=1
	)


	fig.add_vrect(
		x0=df.index[-predicted_points-1], x1=df.index[-1],
		fillcolor="green", opacity=0.2,
		layer="below", line_width=0,
		xref="x", yref="paper"
	)
	
	fig.update_layout(
		#xaxis_title='Date',
		yaxis=dict(
			title='Price',
			titlefont=dict(size=12),
		),

		yaxis2=dict(
			title='RSI',
			titlefont=dict(size=12),
			range=[0, 100],
			dtick=20
		),
		height=600
	)

	return fig