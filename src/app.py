import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path
import matplotlib.pyplot as plt


# Load environment variables

load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# 1) Connect to the database with SQLAlchemy

# Load environment variables

def connect():
    global engine
    try:
        connection_string = (
            f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
        print("Starting the connection...")
        engine = create_engine(connection_string, isolation_level="AUTOCOMMIT")
        conn = engine.connect()
        print("Connected successfully!")
        conn.close()
        return engine
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

engine = connect()

if engine is None:
    exit()

#Funcion para ejecutar archivos SQL

def run_sql_file(engine, sql_path):
    sql_text = Path(sql_path).read_text(encoding="utf-8")
    statements = sql_text.strip().split(";")  # dividir por ;
    with engine.connect() as conn:
        for stmt in statements:
            if stmt.strip():  # evitar líneas vacías
                conn.execute(text(stmt))
    print(f"✅ Ejecutado: {sql_path}")

# Limpiar tablas 
run_sql_file(engine, "src/sql/drop.sql")

# Crear tablas
run_sql_file(engine, "src/sql/create.sql")

# Insertar datos
run_sql_file(engine, "src/sql/insert.sql")

# Leer con Pandas una tabla existente
with engine.connect() as conn:
    df = pd.read_sql("SELECT * FROM books", conn)
print("📄 DataFrame (books):")
print(df.head())

#Ver otras tablas con PAndas autores
with engine.connect() as conn:
    df_authors = pd.read_sql("SELECT * FROM authors", conn)
print(df_authors.head())

#consulta para seleccionar titulo libro, nombre y apellido del autor
#nombre de la editorial haciendo un join para unir las tablas
#con los datos

query = """
SELECT b.title, a.first_name, a.last_name, p.name AS publisher
FROM books b
JOIN book_authors ba ON b.book_id = ba.book_id
JOIN authors a ON ba.author_id = a.author_id
JOIN publishers p ON b.publisher_id = p.publisher_id;
"""
with engine.connect() as conn:
    df_join = pd.read_sql(query, conn)
print(df_join.head())

#Graficando y guardando en el archivo grafico_editoriales.png

df_counts = df_join.groupby("publisher").size().reset_index(name="total_books")

df_counts.plot(kind="bar", x="publisher", y="total_books", legend=False)

plt.title("Número de libros por editorial")
plt.xlabel("Editorial")
plt.ylabel("Cantidad de libros")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()

# Guardar gráfico como imagen
plt.savefig("grafico_editoriales.png")
print("Gráfico guardado como grafico_editoriales.png")








