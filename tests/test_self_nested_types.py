import unittest
from hypothesis import given, strategies as st
from tests.utils import eval_uplc_value


class TestSelfInNestedTypes(unittest.TestCase):
    """Test cases for Self annotations in nested/recursive type structures"""

    @given(x=st.integers())
    def test_self_in_dict_key(self, x: int):
        """Test Self as Dict key type"""
        source_code = """
from typing import Self, Dict, List, Union
from pycardano import Datum as Anything, PlutusData
from dataclasses import dataclass

@dataclass
class A(PlutusData):
    value: int

    def get_from_dict(self, d: Dict[Self, int]) -> int:
        for k, v in d.items():
            if k.value == self.value:
                return v
        return -1

def validator(x: int) -> int:
    a1 = A(x)
    a2 = A(x + 1)
    return a1.get_from_dict({a1: 10, a2: 20})
"""
        ret = eval_uplc_value(source_code, x)
        self.assertEqual(ret, 10)

    @given(x=st.integers())
    def test_self_in_dict_value(self, x: int):
        """Test Self as Dict value type"""
        source_code = """
from typing import Self, Dict, List, Union
from pycardano import Datum as Anything, PlutusData
from dataclasses import dataclass

@dataclass
class A(PlutusData):
    value: int

    def get_self_from_dict(self, d: Dict[int, Self]) -> Self:
        return d.get(self.value, self)

def validator(x: int) -> int:
    a1 = A(x)
    a2 = A(x + 1)
    result = a1.get_self_from_dict({x: a2})
    return result.value
"""
        ret = eval_uplc_value(source_code, x)
        self.assertEqual(ret, x + 1)

    @given(x=st.integers())
    def test_self_in_list(self, x: int):
        """Test Self in List type"""
        source_code = """
from typing import Self, Dict, List, Union
from pycardano import Datum as Anything, PlutusData
from dataclasses import dataclass

@dataclass
class A(PlutusData):
    value: int

    def get_first_from_list(self, items: List[Self]) -> Self:
        if items:
            return items[0]
        return self

def validator(x: int) -> int:
    a1 = A(x)
    a2 = A(x + 1)
    result = a1.get_first_from_list([a2, a1])
    return result.value
"""
        ret = eval_uplc_value(source_code, x)
        self.assertEqual(ret, x + 1)

    @given(x=st.integers())
    def test_self_nested_in_union_and_dict(self, x: int):
        """Test Self in simpler nested types"""
        source_code = """
from typing import Self, Dict, List, Union
from pycardano import Datum as Anything, PlutusData
from dataclasses import dataclass

@dataclass
class A(PlutusData):
    value: int

    def process_simple(self, data: Union[Self, int]) -> int:
        if isinstance(data, A):
            return data.value
        else:
            return data

def validator(x: int) -> int:
    a1 = A(x)
    # Test with direct Self
    result1 = a1.process_simple(a1)
    # Test with int
    result2 = a1.process_simple(42)
    return result1 + result2
"""
        ret = eval_uplc_value(source_code, x)
        self.assertEqual(ret, x + 42)


if __name__ == "__main__":
    unittest.main()