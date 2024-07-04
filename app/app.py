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

	st.title('Ticker Trend')
	st.subheader('Charts & Predictions', divider='rainbow')

	with st.sidebar:
		
		ticker = st.selectbox('Stock Watchlist', watchlist)

		if ticker:
			logo = be.display_company_logo(ticker)
			st.image(logo, width=150)
			profile = be.get_jsonparsed_data(be.company_profile_url(ticker))
			summary_table = be.stock_summary_table(profile)
			st.table(summary_table)

			# testing stuff
			st.write(profile[0]['description'])

		else:
			st.write('Select a stock symbol to get started...')

		#st.button('Clear Cache', on_click=be.combine_data.clear())
	

	if ticker:

		stock_data = be.combine_data(ticker, **params).sort_values(by='date')
		stock_data = stock_data.iloc[-30:]
		pred = be.predict(ticker, stock_data)
		st.plotly_chart(be.make_chart(pred, stock_data))
		#st.table(summary_table)
		#st.write(profile)

		st.subheader('Similar Stocks', divider='rainbow')

		screener_params = {
			'industry': profile[0]['industry'].lower(),
			'limit': 6,
			'isEtf': str(profile[0]['isEtf']).lower(),
			'isActivelyTrading': str(profile[0]['isActivelyTrading']).lower()
		}

		#st.write(screener_params)
		st.table(be.stock_screener_table(ticker, **screener_params))
		


if __name__ == '__main__':
	main()

