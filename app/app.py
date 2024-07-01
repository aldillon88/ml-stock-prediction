import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime

import sys
import os

from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import backend as be


def main():

	watchlist = ['AMZN', 'AAPL', 'GOOG', 'META','MSFT', 'NVDA', 'TSLA']
	
	# Other parameters
	today_date = datetime.today().strftime('%Y-%m-%d')
	params = {
		'from': '2024-01-01',
		'to': today_date
	}

	st.title('Stock Price Predictor')

	with st.sidebar:
		
		ticker = st.selectbox('Stock Watchlist', watchlist)

		if ticker:
			logo = be.display_company_logo(ticker)
			st.image(logo, width=150)
			summary_table = be.stock_summary_table(be.get_jsonparsed_data(be.company_profile_url(ticker)))
			st.table(summary_table)

		else:
			st.write('Select a stock symbol to get started...')
	

	if ticker:

		stock_data = be.combine_data(ticker, **params).sort_values(by='date')
		stock_data = stock_data.iloc[-30:]
		pred = be.predict(ticker, stock_data)
		#st.line_chart(pred, x=None, y='close')
		st.plotly_chart(be.make_chart(pred))


if __name__ == '__main__':
	main()

