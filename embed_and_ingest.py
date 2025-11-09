import os
import psycopg2
from sentence_transformers import SentenceTransformer
from PIL import Image
from tqdm import tqdm

# ==========================================================
# DATABASE CONFIGURATION
# ==========================================================
DB = dict(
    dbname="mmdb",
    user="postgres",
    password="vaibhav",  # change if needed
    host="127.0.0.1",
    port="5432"
)

# ==========================================================
# PATHS
# ==========================================================
IMAGES_DIR = r"C:\Users\asus\Desktop\DBMS Project PSQL\flickr8k\Images"
CAPTIONS_FILE = r"C:\Users\asus\Desktop\DBMS Project PSQL\flickr8k\captions.txt"

# ==========================================================
# MODEL LOADING
# ==========================================================
print("🚀 Loading CLIP model (ViT-B/32)…")
model = SentenceTransformer("clip-ViT-B-32")
print("✅ CLIP model loaded successfully.\n")

# ==========================================================
# HELPERS
# ==========================================================
def db_connect():
    return psycopg2.connect(**DB)

def embed_image(path):
    """Generate CLIP embedding for image"""
    try:
        image = Image.open(path).convert("RGB")
        emb = model.encode(image, normalize_embeddings=True)
        return emb.tolist()
    except Exception as e:
        print(f"⚠️ Skipping {path}: {e}")
        return None

def embed_text(text):
    """Generate CLIP embedding for text"""
    emb = model.encode(text, normalize_embeddings=True)
    return emb.tolist()

# ==========================================================
# MAIN INGESTION FUNCTION
# ==========================================================
def ingest_dataset():
    conn = db_connect()
    cur = conn.cursor()

    captions_map = {}
    with open(CAPTIONS_FILE, "r", encoding="utf-8") as f:
        next(f)  # skip header
        for line in f:
            parts = line.strip().split(",", 1)
            if len(parts) == 2:
                img, caption = parts
                captions_map.setdefault(img, []).append(caption)

    print(f"📁 Found {len(captions_map)} image entries.\n")

    for img_name, caps in tqdm(captions_map.items(), desc="Embedding & inserting"):
        img_path = os.path.join(IMAGES_DIR, img_name)
        if not os.path.exists(img_path):
            continue

        # 🔹 1. Embed image
        img_vec = embed_image(img_path)
        if img_vec is None:
            continue

        # 🔹 2. Insert image using your SQL function
        cur.execute("SELECT insert_image_with_embedding(%s, %s, %s);", (img_path, None, img_vec))
        image_id = cur.fetchone()[0]

        # 🔹 3. Embed and insert captions
        for cap in caps:
            cap_vec = embed_text(cap)
            cur.execute("SELECT insert_caption_with_embedding(%s, %s, %s);", (image_id, cap, cap_vec))

    conn.commit()
    conn.close()
    print("\n✅ All embeddings successfully stored in your PostgreSQL schema!")

# ==========================================================
if __name__ == "__main__":
    ingest_dataset()
