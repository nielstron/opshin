from opshin.prelude import *
from typing import Self

@dataclass
class A(PlutusData):
    x: int

    def foo(self, other: Self) -> Self:
        return other

def validator(a: int) -> bool:
    return True