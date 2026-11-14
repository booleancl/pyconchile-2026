"""Validate simulated LLM responses with Pydantic V1 or V2, using the same model.

Usage:
    python llm_parser.py v1 responses.jsonl
    python llm_parser.py v2 responses.jsonl

v1 uses Pydantic 1 when it is installed (pip install "pydantic<2"). Inside a
Pydantic 2 environment it falls back to the V1 code bundled as pydantic.v1.
Only validation is timed; reading the file is not.
"""
import sys
import time
from datetime import datetime
from typing import List, Literal, Optional

engine = sys.argv[1]
path = sys.argv[2]

if engine == "v1":
    import pydantic

    if pydantic.VERSION.startswith("1."):
        from pydantic import BaseModel, Field, ValidationError
        label = f"Pydantic {pydantic.VERSION} (compiled: {pydantic.compiled})"
    else:
        from pydantic.v1 import BaseModel, Field, ValidationError
        import pydantic.v1
        label = f"Pydantic {pydantic.v1.VERSION} via pydantic.v1 (compiled: {pydantic.v1.compiled})"
else:
    import pydantic
    from pydantic import BaseModel, Field, ValidationError
    label = f"Pydantic {pydantic.VERSION} (Rust core)"


# The same model for both versions.
class LineItem(BaseModel):
    sku: str
    description: str
    quantity: int = Field(gt=0)
    unit_price: float = Field(ge=0)


class Order(BaseModel):
    order_id: str
    customer: str
    currency: Literal["CLP", "USD"]
    priority: Literal["low", "normal", "high"]
    created_at: datetime
    items: List[LineItem]
    notes: Optional[str] = None


def parse(text: str) -> Order:
    if engine == "v1":
        return Order.parse_raw(text)            # V1: json.loads + validation in Python
    return Order.model_validate_json(text)      # V2: parse + validate in Rust, one call


with open(path) as f:
    responses = f.read().splitlines()

valid, invalid = 0, 0
first_error = None

start = time.perf_counter()
for text in responses:
    try:
        parse(text)
        valid += 1
    except ValidationError as error:
        invalid += 1
        if first_error is None:
            first_error = error
elapsed = time.perf_counter() - start

print(label)
print(f"responses: {len(responses):,}   valid: {valid:,}   invalid: {invalid:,}")
print(f"time: {elapsed:.2f} s   ({elapsed / len(responses) * 1e6:.1f} µs per response)")
if first_error is not None:
    print("first error:")
    print(first_error)
