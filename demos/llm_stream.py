"""Simulate an LLM streaming a JSON order and validate it while it arrives.

Usage: python llm_stream.py

Pydantic 2 (2.10 or newer) can validate incomplete JSON with
experimental_allow_partial=True. Parsing and validation run in its Rust core.
Partial validation works with TypedDict (not BaseModel), so the order is a TypedDict.
No model is called: the chunks below stand in for the tokens a model sends.
"""
import time
from typing import List, Literal, Optional

from pydantic import Field, TypeAdapter
from typing_extensions import Annotated, NotRequired, TypedDict


class LineItem(TypedDict):
    sku: str
    quantity: Annotated[int, Field(gt=0)]


class Order(TypedDict):
    customer: str
    priority: NotRequired[Literal["low", "normal", "high"]]
    items: NotRequired[List[LineItem]]
    notes: NotRequired[Optional[str]]


RESPONSE = (
    '{"customer": "ACME Ltda.", "priority": "high", '
    '"items": [{"sku": "SKU-1001", "quantity": 12}, '
    '{"sku": "SKU-4120", "quantity": 3}], '
    '"notes": "Deliver before Friday"}'
)

CHUNK_SIZE = 12          # characters per simulated token batch
DELAY_SECONDS = 0.3      # pause between chunks, so the audience can follow

adapter = TypeAdapter(Order)
received = ""

for start in range(0, len(RESPONSE), CHUNK_SIZE):
    received += RESPONSE[start:start + CHUNK_SIZE]
    try:
        partial = adapter.validate_json(received, experimental_allow_partial=True)
        print(f"{len(received):>3} chars | {partial}")
    except Exception:
        print(f"{len(received):>3} chars | waiting for 'customer'...")
    time.sleep(DELAY_SECONDS)

order = adapter.validate_json(received)   # the complete response, fully validated
print()
print("complete:", order)
