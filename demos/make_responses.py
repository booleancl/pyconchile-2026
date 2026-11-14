"""Generate simulated LLM responses: JSON orders extracted from customer emails.

Usage: python make_responses.py 100000 > responses.jsonl

About 5% of the responses are broken on purpose, the way real model output
sometimes is: a missing field, a wrong value, or JSON cut off mid-stream.
The seed is fixed, so every run produces the same file.
"""
import json
import random
import sys

random.seed(42)

# Fictional customers only: never use real clients or prospects in demo data.
CUSTOMERS = ["ACME Ltda.", "Demo Corp", "Ejemplo SpA", "Prueba Ltda.", "Muestra S.A."]
PRODUCTS = [
    ("SKU-1001", "USB-C cable"),
    ("SKU-2040", "Laptop stand"),
    ("SKU-3300", "Wireless mouse"),
    ("SKU-4120", "27-inch monitor"),
    ("SKU-5005", "Mechanical keyboard"),
]


def make_order(i: int) -> dict:
    items = []
    for _ in range(random.randint(1, 5)):
        sku, description = random.choice(PRODUCTS)
        items.append({
            "sku": sku,
            "description": description,
            "quantity": random.randint(1, 20),
            "unit_price": round(random.uniform(5, 500), 2),
        })
    return {
        "order_id": f"ORD-{i:07d}",
        "customer": random.choice(CUSTOMERS),
        "currency": random.choice(["CLP", "USD"]),
        "priority": random.choice(["low", "normal", "high"]),
        "created_at": f"2026-10-{random.randint(1, 28):02d}T{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:00",
        "items": items,
        "notes": random.choice([None, "Deliver before Friday", "Call before delivery"]),
    }


def break_it(order: dict) -> str:
    kind = random.choice(["missing_field", "bad_quantity", "bad_currency", "truncated"])
    if kind == "missing_field":
        del order["customer"]
    elif kind == "bad_quantity":
        order["items"][0]["quantity"] = 0
    elif kind == "bad_currency":
        order["currency"] = "pesos"
    text = json.dumps(order)
    if kind == "truncated":
        text = text[: len(text) // 2]
    return text


def main() -> None:
    n = int(sys.argv[1])
    for i in range(n):
        order = make_order(i)
        if random.random() < 0.05:
            print(break_it(order))
        else:
            print(json.dumps(order))


if __name__ == "__main__":
    main()
