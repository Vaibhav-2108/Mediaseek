import psycopg2

DB = dict(
    dbname="mmdb",
    user="postgres",
    password="vaibhav",
    host="127.0.0.1",
    port="5432"
)

def clear_all_rows():
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    print("🧹 Deleting all rows (but keeping table structure)...")

    # Use TRUNCATE to quickly clear all rows but keep schema intact
    cur.execute("""
        TRUNCATE TABLE embeddings, captions, images RESTART IDENTITY CASCADE;
    """)

    conn.commit()
    conn.close()
    print("✅ All rows deleted successfully, tables remain intact.")

if __name__ == "__main__":
    clear_all_rows()
