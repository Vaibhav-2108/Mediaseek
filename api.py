import os
import psycopg2
from flask import Flask, request, jsonify, render_template, send_from_directory
from PIL import Image
from sentence_transformers import SentenceTransformer

# ==========================================================
# CONFIGURATION
# ==========================================================
app = Flask(__name__)

DB = dict(
    dbname="mmdb",
    user="postgres",
    password="vaibhav",
    host="127.0.0.1",
    port="5432"
)

IMAGE_FOLDER = r"C:\Users\asus\Desktop\DBMS Project PSQL\flickr8k\Images"

# ==========================================================
# MODEL LOADING
# ==========================================================
print("🚀 Loading CLIP model (ViT-B/32)…")
model = SentenceTransformer("clip-ViT-B-32")
print("✅ CLIP model loaded.\n")

# ==========================================================
# HELPERS
# ==========================================================
def db_connect():
    return psycopg2.connect(**DB)

def embed_image(file_stream):
    """Embed an uploaded image with CLIP"""
    image = Image.open(file_stream).convert("RGB")
    return model.encode(image, normalize_embeddings=True).tolist()

def embed_text(text):
    """Embed text query with CLIP"""
    return model.encode(text, normalize_embeddings=True).tolist()

# ==========================================================
# ROUTES
# ==========================================================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/images/<path:filename>")
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

# ==========================================================
# TEXT → IMAGE SEARCH
# ==========================================================
@app.route("/search/text_to_image", methods=["POST"])
def text_to_image():
    query = request.form.get("query", "").strip()
    if not query:
        return jsonify({"error": "Empty query"}), 400

    qvec = embed_text(query)
    qnorm = 1.0  # CLIP embeddings are normalized
    conn = db_connect()
    cur = conn.cursor()

    cur.execute("SELECT * FROM search_similar_images(%s, %s, %s);", (qvec, qnorm, 20))
    rows = cur.fetchall()
    conn.close()

    results = []
    for r in rows:
        img_name = os.path.basename(r[1])
        img_url = f"/images/{img_name}"
        score = float(r[2]) if r[2] is not None else 0.0
        results.append({"image_path": img_url, "score": round(score, 4)})

    return jsonify(results)

# ==========================================================
# IMAGE → IMAGE SEARCH
# ==========================================================
@app.route("/search/image_to_image", methods=["POST"])
def image_to_image():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    qvec = embed_image(file.stream)
    qnorm = 1.0
    conn = db_connect()
    cur = conn.cursor()

    cur.execute("SELECT * FROM search_similar_images(%s, %s, %s);", (qvec, qnorm, 20))
    rows = cur.fetchall()
    conn.close()

    results = []
    for r in rows:
        img_name = os.path.basename(r[1])
        img_url = f"/images/{img_name}"
        score = float(r[2]) if r[2] is not None else 0.0
        results.append({"image_path": img_url, "score": round(score, 4)})

    return jsonify(results)

# ==========================================================
# IMAGE → TEXT SEARCH
# ==========================================================
@app.route("/search/image_to_text", methods=["POST"])
def image_to_text():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    qvec = embed_image(file.stream)
    qnorm = 1.0
    conn = db_connect()
    cur = conn.cursor()

    cur.execute("SELECT * FROM search_similar_captions(%s, %s, %s);", (qvec, qnorm, 20))
    rows = cur.fetchall()
    conn.close()

    results = []
    for r in rows:
        img_name = os.path.basename(r[3])
        img_url = f"/images/{img_name}"
        score = float(r[4]) if r[4] is not None else 0.0
        results.append({
            "caption": r[1],
            "image_path": img_url,
            "score": round(score, 4)
        })

    return jsonify(results)

# ==========================================================
# MAIN
# ==========================================================
if __name__ == "__main__":
    print(f"🌐 Flask app running — serving images from:\n{IMAGE_FOLDER}\n")
    app.run(debug=True)
