"""Local teaching application. No authentication: never expose it publicly."""

import argparse
import re
import sqlite3
import uuid
from pathlib import Path

from flask import Flask, g, jsonify, request, send_file
from werkzeug.exceptions import BadRequest, UnsupportedMediaType

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    sku TEXT PRIMARY KEY, name TEXT NOT NULL,
    stock INTEGER NOT NULL CHECK(stock >= 0)
);
CREATE TABLE IF NOT EXISTS reservations (
    id TEXT PRIMARY KEY,
    sku TEXT NOT NULL REFERENCES products(sku),
    quantity INTEGER NOT NULL CHECK(quantity BETWEEN 1 AND 100),
    email TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('active', 'cancelled')),
    idempotency_key TEXT NOT NULL UNIQUE
);
"""


def create_app(database):
    app = Flask(__name__)
    app.config.update(DATABASE=str(database), MAX_CONTENT_LENGTH=16_384)
    with sqlite3.connect(database) as connection:
        connection.executescript(SCHEMA)
        connection.executemany(
            "INSERT OR IGNORE INTO products VALUES (?, ?, ?)",
            [("TEA-001", "Чай жасминовый", 10), ("CUP-001", "Чашка керамическая", 3)],
        )

    def db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"], timeout=5)
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
        return g.db

    @app.teardown_appcontext
    def close_db(_error):
        connection = g.pop("db", None)
        if connection is not None:
            connection.close()

    def error(code, status):
        return jsonify(error=code), status

    def reservation(row):
        return {key: row[key] for key in ("id", "sku", "quantity", "email", "status")}

    @app.get("/")
    def index():
        return send_file(Path(__file__).with_name("index.html"))

    @app.get("/api/health")
    def health():
        return jsonify(status="ok")

    @app.get("/api/products")
    def products():
        rows = db().execute("SELECT sku, name, stock FROM products ORDER BY sku").fetchall()
        return jsonify([dict(row) for row in rows])

    @app.get("/api/reservations/<reservation_id>")
    def get_reservation(reservation_id):
        row = db().execute("SELECT * FROM reservations WHERE id = ?", (reservation_id,)).fetchone()
        return (jsonify(reservation(row)), 200) if row else error("reservation_not_found", 404)

    @app.post("/api/reservations")
    def create_reservation():
        try:
            body = request.get_json()
        except UnsupportedMediaType:
            return error("json_required", 415)
        except BadRequest:
            return error("malformed_json", 400)
        if not isinstance(body, dict):
            return error("invalid_payload", 422)
        sku, quantity, email = (body.get(key) for key in ("sku", "quantity", "email"))
        if not isinstance(sku, str) or not sku.strip():
            return error("invalid_sku", 422)
        if type(quantity) is not int or not 1 <= quantity <= 100:
            return error("invalid_quantity", 422)
        if not isinstance(email, str) or len(email) > 254 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            return error("invalid_email", 422)
        key = request.headers.get("Idempotency-Key", "").strip()
        if not key or len(key) > 80:
            return error("invalid_idempotency_key", 422)
        # A write lock makes the stock check and reservation one atomic operation.
        connection = db()
        with connection:
            connection.execute("BEGIN IMMEDIATE")
            previous = connection.execute(
                "SELECT * FROM reservations WHERE idempotency_key = ?", (key,)
            ).fetchone()
            if previous:
                if (previous["sku"], previous["quantity"], previous["email"]) != (sku, quantity, email):
                    return error("idempotency_conflict", 409)
                return jsonify(reservation(previous)), 200
            product = connection.execute("SELECT stock FROM products WHERE sku = ?", (sku,)).fetchone()
            if product is None:
                return error("product_not_found", 404)
            if product["stock"] < quantity:
                return error("insufficient_stock", 409)
            identifier = str(uuid.uuid4())
            connection.execute("UPDATE products SET stock = stock - ? WHERE sku = ?", (quantity, sku))
            connection.execute(
                "INSERT INTO reservations VALUES (?, ?, ?, ?, 'active', ?)",
                (identifier, sku, quantity, email, key),
            )
            row = connection.execute("SELECT * FROM reservations WHERE id = ?", (identifier,)).fetchone()
        return jsonify(reservation(row)), 201

    @app.delete("/api/reservations/<reservation_id>")
    def cancel_reservation(reservation_id):
        connection = db()
        with connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("SELECT * FROM reservations WHERE id = ?", (reservation_id,)).fetchone()
            if row is None:
                return error("reservation_not_found", 404)
            if row["status"] == "active":
                connection.execute("UPDATE products SET stock = stock + ? WHERE sku = ?", (row["quantity"], row["sku"]))
                connection.execute("UPDATE reservations SET status = 'cancelled' WHERE id = ?", (reservation_id,))
            row = connection.execute("SELECT * FROM reservations WHERE id = ?", (reservation_id,)).fetchone()
        return jsonify(reservation(row)), 200

    return app


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Local QA teaching lab")
    parser.add_argument("--database", default="lab.sqlite3")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    create_app(args.database).run(host="127.0.0.1", port=args.port, debug=False)
