from flask import Flask, render_template, request
import numpy as np
import logging
import pickle

# Load the necessary DataFrames
popular_df = pickle.load(open("data/processed/popular_df.pkl", "rb"))
ratings_pivot_table = pickle.load(open("data/processed/ratings_pivot_table.pkl", "rb"))
books = pickle.load(open("data/processed/books.pkl", "rb"))
similarity_scores = pickle.load(open("data/processed/similarity_scores.pkl", "rb"))

# Flask app setup
app = Flask(__name__)

# Logging setup
logging.basicConfig(level=logging.INFO)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# Home page route
@app.route("/", methods=["GET", "POST"])
def index():
    app.logger.info("Index endpoint was reached")
    data = None  # To hold recommended books, if any

    if request.method == "POST":
        # Get the book title entered by the user
        user_input = request.form.get("user_input")

        # Get the index of the entered book title
        index = np.where(ratings_pivot_table.index == user_input)[0][0]

        # Find similar books and select the top 4
        similar_items = sorted(
            list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True
        )[1:7]

        data = []
        for i in similar_items:
            item = []
            # Get details of the similar books
            temp_df = books[books["Book-Title"] == ratings_pivot_table.index[i[0]]]
            item.extend(
                list(temp_df.drop_duplicates("Book-Title")["Book-Title"].values)
            )
            item.extend(
                list(temp_df.drop_duplicates("Book-Title")["Book-Author"].values)
            )
            item.extend(
                list(temp_df.drop_duplicates("Book-Title")["Image-URL-M"].values)
            )

            data.append(item)

    return render_template(
        "index.html",
        book_name=list(popular_df["Book-Title"].values),
        author=list(popular_df["Book-Author"].values),
        image=list(popular_df["Image-URL-M"].values),
        votes=list(popular_df["num_ratings"].values),
        rating=list(popular_df["avg_rating"].values),
        data=data,  # Pass the recommended books to the template
    )


if __name__ == "__main__":
    # Run the app
    app.run(host="0.0.0.0", port=5000, debug=True)
