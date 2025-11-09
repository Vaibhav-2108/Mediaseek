import psycopg2

# 🔧 Database connection (no environment variables)
DB_NAME = "mmdb"
DB_USER = "postgres"
DB_PASS = "vaibhav"       # <-- change if your PostgreSQL password is different
DB_HOST = "localhost"
DB_PORT = "5432"

def setup():
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASS,
        host=DB_HOST, port=DB_PORT
    )
    cur = conn.cursor()
    with open("schema.sql", "r") as f:
        cur.execute(f.read())
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Database schema and functions created successfully!")

if __name__ == "__main__":
    setup()
