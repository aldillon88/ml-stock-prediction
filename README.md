# Stock price prediction with machine learning 

### Introduction
This project attempts to predict what the price of a stock will be up to three days after the current day. The predictions are based on historical price movement data that is retrieved from a reputable financial data API.

### Installation and setup

#### Code and Resources Used
Python 3.9.6
Jupyter Notebook 7.2.1

#### Packages Used
General purpose: `os`, `ssl`, `certifi`, `json`, `time`, `urllib`, `sys`, `pathlib`, `joblib`, `pickle`, `tempfile`. 
Data Manipulation: `pandas`, `numpy`, `datetime`. 
Data Visualization: `plotly`. 
Machine Learning: `sklearn`, `optuna`, `xgboost`. 
User Interface: `streamlit`. 
Other: `IPython`, `kaleido`. 

#### Installation
1. Clone this repository:
	1. `git clone https://github.com/aldillon88/ml-stock-prediction.git`.
2. Create a virtual environment and activate it:
	1. `python -m venv venv-final-project`
	2. `source venv-final-project/bin/activate`.
3. Install the required packages:
	1. `pip install -r requirements.txt`.
4. Setup Git Large File Storage and track kaleido:
	1. `git lfs install`
	2. `git lfs track "venv-final-project/lib/python3.9/site-packages/kaleido/executable/bin/kaleido"`
	3. `git add .gitattributes`
	4. `git commit -m "Track large file with Git LFS"`
5. Push changes to the repository:
	1. `git rm --cached venv-final-project/lib/python3.9/site-packages/kaleido/executable/bin/kaleido`
	2. `git add venv-final-project/lib/python3.9/site-packages/kaleido/executable/bin/kaleido`
	3. `git commit -m "Add large file to LFS"`
	4. `git push origin main --force`
6. Run the Streamlit app:
	1. `streamlit run app.py`

### Data Retrieval
* The data for this project is provided by the [Financial Modeling Prep API](https://site.financialmodelingprep.com/), which is free with some limitations, including 250 API calls per day and access to a subset of the API endpoints.
* Data is returned in JSON format before being converted to pandas dataframes in the code.
* The FMP API key should be set as an environment variable FMP_SECRET_KEY. You can set it in your terminal session like so: `export FMP_SECRET_KEY=your_api_key_here`.

### Machine Learning
* This project includes a distinct ML model/scaler for each distinct stock in the list: `watchlist = ['AMZN', 'AAPL', 'GOOG', 'META','MSFT', 'NVDA', 'TSLA']`.
* The model utilises the SKLearn `StackingRegressor` to leverage multiple complimentary ML algorithms, with `LinearRegression()`, `XGBRegressor()` and `SVM()` used as base learners and `LinearRegression()` as the meta model. Normalization is achieved through `MinMaxScaler`.
* The `Optuna` package was used for hyperparameter selection, making that process far less manual. Further experimentation could be done with this package to further improve the results of the models.

### Streamlit App
* The UI of this project is built with Streamlit, which makes the process very easy for a person without web development skills. The Streamlit app is split into two files: `app.py` and `backend.py`.
* Users of the app can select a stock symbol from a dropdown selector, which then triggers all of the API calls in the `backend.py` file. The data retrieved via API is then processed, normalized and passed through the ML model applicable to the chosen stock. The predictions are then shown in a chart in the frontend.
* In addition to the predictions chart, the Relative Strength Index (RSI) is also charted. This is a common technical indicator used by traders to show whether a stock is potentially oversold or overbought.
* Underneath the charts is a list of stocks that are similar to the one chosen. This list is also retrieved via the API with the use of some additional parameters to refine the list and ensure its relevance.

### Project Structure
|---project\
|&nbsp;&nbsp;|---app\
|&nbsp;&nbsp;&nbsp;|---__init__.py\
|&nbsp;&nbsp;&nbsp;|---app.py\
|&nbsp;&nbsp;&nbsp;|---backend.py\
|		|---data\
|			|---clean\
|				|---alphabet_training_data.csv\
|				|---amazon_training_data.csv\
|				|---apple_training_data.csv\
|				|---meta_training_data.csv\
|				|---meta_training_data.csv\
|				|---nvidia_training_data.csv\
|				|---tesla_training_data.csv\
|			|---raw\
|		|---images\
|		|---models\
|			|---alphabet_stacking_regressor_model.pkl\
|			|---amazon_stacking_regressor_model.pkl\
|			|---apple_stacking_regressor_model.pkl\
|			|---meta_stacking_regressor_model.pkl\
|			|---microsoft_stacking_regressor_model.pkl\
|			|---nvidia_stacking_regressor_model.pkl\
|			|---tesla_stacking_regressor_model.pkl\
|		|---notebooks\
|			|---__init__.py\
|			|---config.py\
|			|---functions.py\
|			|---model_training.ipynb\
|			|---training_data_collection.ipynb\
|		|---scalers\
|			|---alphabet_normalizer.pkl\
|			|---amazon_normalizer.pkl\
|			|---apple_normalizer.pkl\
|			|---meta_normalizer.pkl\
|			|---microsoft_normalizer.pkl\
|			|---nvidia_normalizer.pkl\
|			|---tesla_normalizer.pkl\
|		|---slides\
|			|---tickertrend.pdf\
|		|---venv\
|		|---README.md\
|		|---requirements-dev.in\
|		|---requirements-dev.txt\
|		|---requirements.in\
|		|---requirements.txt


