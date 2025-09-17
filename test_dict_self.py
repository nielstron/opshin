from dataclasses import dataclass
from typing import Dict, List, Union, Self
from pycardano import Datum as Anything, PlutusData

@dataclass
class A(PlutusData):
    x: int

    def foo(self, other: Dict[Self, int]) -> Union[Self, int]:
        for y in other.values():
            return y
        return self

def validator(a: int) -> bool:
    return isinstance(A(1).foo({A(2): a}), A)