# test.py
from opshin.prelude import *
from typing import Self

@dataclass
class A(PlutusData):

    def foo(self, x: Dict[Self, int]) -> int:
        for y in x.values():
            return y
        return 0

def validator(a: int) -> bool:
    return A().foo({A(): a}) == 1