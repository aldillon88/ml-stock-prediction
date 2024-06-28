# Function to replace patterns in a single string
def replace_patterns(text, replacements):
    for key, value in replacements.items():
        text = text.replace(key, value)
    return text


# Function to apply replace_patterns to DataFrame column names
# Takes in a dataframe and a dictionary where keys = old column name and values = desired column names
def replace_column_names(df, replacements):
	df2 = df.copy()
	df2.columns = [replace_patterns(col, replacements) for col in df.columns]
	return df2


def trim_and_lower(df):
	df2 = df.copy()

	df2.columns = [column.strip() for column in df2.columns]
	df2.columns = [column.strip().replace(" ", "_").lower() for column in df2.columns]

	df2 = df2.map(lambda x: x.replace("\xa0", " ") if isinstance(x, str) else x)
	df2 = df2.map(lambda x: x.strip() if isinstance(x, str) else x)
	df2 = df2.map(lambda x: x.lower() if isinstance(x, str) else x)

	return df2


def convert_data_type(df, cols, dtype):
    df2 = df.copy()
    for col in cols:
        try:
            df2[col] = df2[col].astype(dtype)
        except Exception as e:
            print(f"Error converting column {col}: {e}")
    return df2


def remove_outliers(df, group, column):
    grouped = df.groupby(group)
    cleaned_data = pd.DataFrame()

    for group_name, dataframe in grouped:
        q1 = dataframe[column].quantile(0.25)
        q3 = dataframe[column].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        data = dataframe[(dataframe[column] >= lower_bound) & (dataframe[column] <= upper_bound)]
        cleaned_data = pd.concat([cleaned_data, data])
    return cleaned_data
