from ast import *
from typing import Optional

from ..util import CompilingNodeTransformer

"""
Checks that there was an import of dataclass if there are any class definitions
"""


class RewriteImportTyping(CompilingNodeTransformer):
    step = "Checking import and usage of typing"

    imports_typing = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.imports_Self = False

    def _recursively_set_self_id(self, node, class_name):
        """Recursively find and set idSelf attribute for all Name nodes with id='Self'"""
        if isinstance(node, Name) and node.id == "Self":
            node.idSelf = class_name
        elif isinstance(node, Subscript):
            # Handle subscripts like Dict[Self, int], Union[Self, int], etc.
            self._recursively_set_self_id(node.value, class_name)
            self._recursively_set_self_id(node.slice, class_name)
        elif isinstance(node, Tuple):
            # Handle tuple slices like in Dict[Self, int] -> Tuple(elts=[Name(Self), Name(int)])
            for elt in node.elts:
                self._recursively_set_self_id(elt, class_name)
        elif isinstance(node, List):
            # Handle list of elements
            for elt in node.elts:
                self._recursively_set_self_id(elt, class_name)
        # Note: We don't need to handle other node types as they don't contain type annotations

    def visit_ImportFrom(self, node: ImportFrom) -> Optional[ImportFrom]:
        if node.module != "typing":
            return node
        
        # Check if this is a Self-only import
        if len(node.names) == 1 and node.names[0].name == "Self":
            self.imports_Self = True
            return None
        
        # Check if this contains Self among other imports
        has_self = any(alias.name == "Self" for alias in node.names)
        if has_self:
            self.imports_Self = True
            # Remove Self from the import list and continue processing
            node.names = [alias for alias in node.names if alias.name != "Self"]
            if not node.names:  # If only Self was imported
                return None
        
        # Validate the remaining imports are the expected Dict, List, Union
        # Allow 3 for just Dict, List, Union or 4 if Self was included
        expected_len = 3
        assert (
            len(node.names) == expected_len
        ), f"The program must contain one 'from typing import Dict, List, Union', got {len(node.names)} imports: {[alias.name for alias in node.names]}"
        for i, n in enumerate(["Dict", "List", "Union"]):
            assert (
                node.names[i].name == n
            ), f"The program must contain one 'from typing import Dict, List, Union', got {node.names[i].name} at position {i}"
            assert (
                node.names[i].asname == None
            ), "The program must contain one 'from typing import Dict, List, Union'"
        self.imports_typing = True
        return None

    def visit_ClassDef(self, node: ClassDef) -> ClassDef:
        assert (
            self.imports_typing
        ), "typing must be imported in order to use datum classes"
        if self.imports_Self:
            for i, attribute in enumerate(node.body):
                if isinstance(attribute, FunctionDef):
                    # Handle all argument annotations recursively
                    for j, arg in enumerate(attribute.args.args):
                        if arg.annotation is not None:
                            self._recursively_set_self_id(arg.annotation, node.name)

                    # Handle return type annotation recursively
                    if attribute.returns is not None:
                        self._recursively_set_self_id(attribute.returns, node.name)

        return node
