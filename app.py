from flask import Flask, request, render_template
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import process


app = Flask(__name__, static_folder='static', template_folder='templates')

# Load data ---------------------------------------------------
try:
    top_9_data = pd.read_csv('models/top_9_highest_rated_items.csv', sep=',')
    cleaned_data = pd.read_csv('models/cleaned_data.csv', sep=',')
except Exception as e:
    print(f"Error loading data: {e}")
    top_9_data = pd.DataFrame()  # Create empty DataFrame as a fallback
    cleaned_data = pd.DataFrame()

# Truncate function
def truncate(text, length):
    if len(text) > length:
        return text[:length] + "..."
    else:

        return text

def content_based_recommendation(data, item_name, top_n=10):
    product_names = data['Product Name'].tolist()
    best_match, confidence = process.extractOne(item_name, product_names)


    # TF-IDF recommendation
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    data['Product Tags'] = data['Product Tags'].fillna('')
    tfidf_train = data.copy()
    tfidf_matrix_content = tfidf_vectorizer.fit_transform(tfidf_train['Product Tags'])
    cosine_similarity_content = cosine_similarity(tfidf_matrix_content, tfidf_matrix_content)
    
    item_index = tfidf_train[tfidf_train['Product Name'] == best_match].index[0]
    similar_items = list(enumerate(cosine_similarity_content[item_index]))
    similar_items = sorted(similar_items, key=lambda x: x[1], reverse=True)
    top_similar_items = similar_items[1:top_n+1]

    recommended_item_indices = [x[0] for x in top_similar_items]
    recommended_item_details = tfidf_train.iloc[recommended_item_indices][['Product Name', 'Product Description', 'Product Image Url', 'Product Rating', 
                                                                           'Product Reviews Count',
                                                                           'Product Brand', 'Product Price']]
    
    return recommended_item_details



# List of image URLs
product_urls = [
    "static/prod1.jpg",
    "static/prod2.jpeg",
    "static/prod3.jpeg",
    "static/prod4.jpeg",
    "static/prod5.png",
    "static/prod6.jpeg",
    "static/prod7.jpeg",
    "static/prod8.jpeg",
    "static/prod9.jpeg",
]

# Routes
@app.route('/')
def index():
    trending_products = [
        {"index": i, **row} for i, row in enumerate(top_9_data.to_dict('records'))
    ]
    return render_template(
        'index.html',
        trending_products=trending_products,
        truncate=truncate,
        producturls=product_urls,
    )


@app.route('/main')
def main():
    return render_template('main.html')

@app.route("/index")
def indexredirect():
    trending_products = [
        {"index": i, **row} for i, row in enumerate(top_9_data.to_dict('records'))
    ]
    return render_template(
        'index.html',
        trending_products=trending_products,
        truncate=truncate,
        producturls=product_urls,
    )

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/recommendations", methods=['POST', 'GET'])
def recommendations():
    if request.method == 'POST':
        prod = request.form.get('product', '')  # Default to empty string if missing

        content_based_rec = content_based_recommendation(cleaned_data, prod, top_n=10)
        print(f"Product: {prod}")

        if content_based_rec.empty:
            message = "No recommendations available for this product."
            return render_template('main.html',message=message, truncate=truncate)
        else:
            print("Recommendations:", content_based_rec)

            content_based_rec = content_based_rec.to_dict('records')  # Convert DataFrame to list of dicts
            return render_template('main.html', content_based_rec=content_based_rec, truncate=truncate)





if __name__ == '__main__':
    app.run(debug=True)

