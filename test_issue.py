# test.py
from opshin.prelude import *
from typing import Self

@dataclass
class A(PlutusData):

    def foo(x: Dict[Self, int]) -> Union[Self, int]:
        for y in x.values():
            return y
        return 0

def validator(a: int) -> bool:
    return foo({A(): a}) == 1