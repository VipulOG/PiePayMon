from dataclasses import dataclass


@dataclass
class Offer:
    id: str
    pay: float
    earn: float
