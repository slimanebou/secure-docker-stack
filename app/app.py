import json
import os

import psycopg
import redis
from flask import Flask, jsonify

app = Flask(__name__)

# Configuration lue dans les variables d'environnement (fournies plus tard par Compose)
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),          # "db" = nom du service Compose
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("POSTGRES_DB", "appdb"),
    "user": os.getenv("POSTGRES_USER", "appuser"),
    "password": os.getenv("POSTGRES_PASSWORD", ""),
    "connect_timeout": 3,                         # n'attend pas indéfiniment
}

cache = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    decode_responses=True,                        # renvoie des str, pas des bytes
    socket_connect_timeout=2,
    socket_timeout=2,
)
CACHE_KEY = "clients"
CACHE_TTL = int(os.getenv("CACHE_TTL", "30"))     # durée de vie du cache en secondes


@app.get("/")
def index():
    return jsonify(message="Bienvenue sur secure-docker-stack")


@app.get("/health")
def health():
    # Vérifie seulement que l'application répond (liveness)
    return jsonify(status="ok"), 200


@app.get("/clients")
def clients():
    # 1. On cherche d'abord dans le cache
    try:
        cached = cache.get(CACHE_KEY)
        if cached:
            return jsonify(source="cache", clients=json.loads(cached))
    except redis.RedisError as e:
        app.logger.warning("Redis indisponible : %s", e)   # on continue sans cache

    # 2. Sinon on lit PostgreSQL
    try:
        with psycopg.connect(**DB_CONFIG) as conn:
            rows = conn.execute(
                "SELECT id, nom, email FROM clients ORDER BY id"
            ).fetchall()
    except psycopg.Error as e:
        app.logger.error("PostgreSQL indisponible : %s", e)
        return jsonify(error="base de données indisponible"), 503

    data = [{"id": r[0], "nom": r[1], "email": r[2]} for r in rows]

    # 3. On met le résultat en cache pour les prochains appels
    try:
        cache.setex(CACHE_KEY, CACHE_TTL, json.dumps(data))
    except redis.RedisError:
        pass

    return jsonify(source="database", clients=data)


if __name__ == "__main__":
    # Uniquement pour le test local (dans Docker, ce sera gunicorn)
    app.run(host="0.0.0.0", port=5000)