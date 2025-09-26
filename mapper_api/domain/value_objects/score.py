"""Domain value object score."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Score:
    value: float

    def __post_init__(self) -> None:
        if not (0.0 <= self.value <= 1.0):
            raise ValueError("score must be between 0 and 1 inclusive")

    # def __float__(self) -> float:  # convenience
    #     return float(self.value)
