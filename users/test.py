from sqlalchemy import create_engine
DATABASE_URL = "postgresql+psycopg2://postgres:postgres@db:5432/microservices_db"
engine = create_engine(DATABASE_URL)
conn = engine.connect()
print(conn.execute("SELECT 1").fetchone())
conn.close()
