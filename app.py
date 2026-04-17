from flask import Flask, render_template, jsonify
import sqlite3

app = Flask(__name__)

# ─────────────────────────────────────────────
# Données fictives de test
# Règle : "lieu" doit être IDENTIQUE à la
# propriété "lieu" dans zones.geojson
# Niveaux PM2.5 (OMS 2021) :
#   ≤ 15  → Bon        (vert)
#   ≤ 25  → Modéré     (jaune)
#   ≤ 35  → Élevé      (orange)
#   ≤ 55  → Mauvais    (rouge)
#   > 55  → Dangereux  (violet)
# ─────────────────────────────────────────────
DONNEES_FICTIVES = [
    # (lieu,                        lat,     lon,    pm25, pm10)
    ("Centre-ville Natitingou",   10.304,  1.379,    35,   50),
    ("Marché Central",            10.285,  1.365,    20,   30),
    ("Quartier Administratif",    10.320,  1.395,    12,   18),
    ("Gare Routière",             10.298,  1.410,    48,   72),
    ("Hôpital de Zone",           10.310,  1.372,    58,   90),
    ("Quartier Kountori",         10.292,  1.400,    28,   42),
    ("Zone Artisanale",           10.278,  1.388,    42,   65),
    ("Lycée Mathieu Bouké",       10.315,  1.381,    14,   22),
]

def init_db():
    conn = sqlite3.connect("pollution.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS pollution (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    lieu      TEXT,
                    lat       REAL,
                    lon       REAL,
                    pm25      REAL,
                    pm10      REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )""")

    # Rechargement complet à chaque démarrage → idéal pour tester
    c.execute("DELETE FROM pollution")

    # executemany accepte directement la liste de tuples, pas besoin de list comprehension
    c.executemany(
        "INSERT INTO pollution (lieu, lat, lon, pm25, pm10) VALUES (?, ?, ?, ?, ?)",
        DONNEES_FICTIVES
    )

    conn.commit()
    conn.close()
    print(f"[DB] {len(DONNEES_FICTIVES)} zones chargées.")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/data")
def data():
    conn = sqlite3.connect("pollution.db")
    c = conn.cursor()
    c.execute("SELECT lat, lon, lieu, pm25, pm10 FROM pollution")
    rows = c.fetchall()
    conn.close()
    return jsonify([
        {"lat": r[0], "lon": r[1], "lieu": r[2], "pm25": r[3], "pm10": r[4]}
        for r in rows
    ])

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
