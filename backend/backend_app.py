from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


def generate_new_id():
    """Generate a new unique ID based on the current max ID in POSTS."""
    return max(post["id"] for post in POSTS) + 1 if POSTS else 1


@app.route('/api/posts', methods=['GET'])
def get_posts():
    return jsonify(POSTS)


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    """Search for posts by title or content using query parameters."""
    title_query = request.args.get('title', '').lower()
    content_query = request.args.get('content', '').lower()

    # Filter posts by title and/or content based on the search terms
    filtered_posts = [
        post for post in POSTS
        if (title_query in post["title"].lower() if title_query else True) and
           (content_query in post["content"].lower() if content_query else True)
    ]

    # Get sorting parameters
    sort = request.args.get('sort')
    direction = request.args.get('direction')

    # Sorting logic
    if sort in ["title", "content"]:
        reverse = direction == "desc"
        filtered_posts.sort(key=lambda x: x[sort].lower(), reverse=reverse)

    # Return the filtered list of posts (empty list if no matches)
    return jsonify(filtered_posts), 200


@app.route('/api/posts', methods=['POST'])
def add_post():
    # Get JSON data from the request
    data = request.get_json()

    # Check if 'title' and 'content' are present in the request
    if not data or "title" not in data or "content" not in data:
        missing_fields = []
        if "title" not in data:
            missing_fields.append("title")
        if "content" not in data:
            missing_fields.append("content")
        return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

    # Generate a new ID for the post
    new_id = generate_new_id()

    # Create the new post
    new_post = {
        "id": new_id,
        "title": data["title"],
        "content": data["content"]
    }

    # Add the new post to the POSTS list
    POSTS.append(new_post)

    # Return the new post with a 201 status code
    return jsonify(new_post), 201


@app.route('/api/posts/<int:id>', methods=['DELETE'])
def delete_post(id):
    global POSTS
    # Find the post by ID
    post = next((post for post in POSTS if post["id"] == id), None)

    # If post not found, return a 404 error
    if post is None:
        return jsonify({"error": f"Post with id {id} not found."}), 404

    # Remove the post from the list
    POSTS = [post for post in POSTS if post["id"] != id]

    # Return a success message
    return jsonify({"message": f"Post with id {id} has been deleted successfully."}), 200


@app.route('/api/posts/<int:id>', methods=['PUT'])
def update_post(id):
    data = request.get_json()
    post = next((post for post in POSTS if post["id"] == id), None)

    # Check if the post exists
    if post is None:
        return jsonify({"error": f"Post with id {id} not found."}), 404

    # Update the post's title and/or content, keeping existing values if not provided
    post["title"] = data.get("title", post["title"])
    post["content"] = data.get("content", post["content"])

    # Return the updated post
    return jsonify(post), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
