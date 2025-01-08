import pandas as pd
import spacy
from spacy.lang.en.stop_words import STOP_WORDS

# Load Data
original_data = pd.read_csv('marketing_sample_for_walmart_com-walmart_com_product_review__20200701_20201231__5k_data.tsv', sep='\t')
data = original_data.copy()

# Initialize Spacy
nlp = spacy.load('en_core_web_sm')

# Functions
def drop_column_na(data):
    threshold = len(data) * (1 / 4)  # Explicit float division
    data.dropna(axis=1, thresh=threshold, inplace=True)
    return data

def clean_text(text):
    doc = nlp(text.lower())
    tags = [token.text for token in doc if token.text.isalnum() and token.text not in STOP_WORDS]
    return ', '.join(tags)

# Data Cleaning
drop_column_na(data)
data.rename(columns= {'Uniq Id': "Unique ID"}, inplace = True)
data.drop('Product Available Inventory', axis=1, errors='ignore', inplace=True)
data.drop(['Product Currency', 'Retailer', 'Product Company Type Source'], axis=1, errors='ignore', inplace=True)
data.drop(['Joining Key', 'Product Url', 'Market', 'Crawl Timestamp'], axis=1, errors='ignore', inplace=True)

data['Unique ID'] = data['Unique ID'].astype(str).str.extract(r'(\d+)').astype(float)
data['Product Id'] = data['Product Id'].astype(str).str.extract(r'(\d+)').astype(float)


column_to_extract_from = ['Product Category', 'Product Description', 'Product Tags']
for column in column_to_extract_from:
    data[column] = data[column].astype(str)
    data[column] = data[column].apply(clean_text)


# Top 9 Products
top_9 = data.dropna(subset=['Product Rating', 'Product Reviews Count']) \
            .sort_values(by=['Product Rating', 'Product Reviews Count'], ascending=[False, False]) \
            .head(9)

# Save Results
top_9.to_csv('top_9_highest_rated_items.csv', index=False)
data.to_csv('cleaned_data.csv', index=False)

