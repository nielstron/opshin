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

    def visit_ImportFrom(self, node: ImportFrom) -> Optional[ImportFrom]:
        if node.module != "typing":
            return node
        if len(node.names) == 1 and node.names[0].name == "Self":
            self.imports_Self = True
            return None
        assert (
            len(node.names) == 3
        ), "The program must contain one 'from typing import Dict, List, Union'"
        for i, n in enumerate(["Dict", "List", "Union"]):
            assert (
                node.names[i].name == n
            ), "The program must contain one 'from typing import Dict, List, Union'"
            assert (
                node.names[i].asname == None
            ), "The program must contain one 'from typing import Dict, List, Union'"
        self.imports_typing = True
        return None

    def _process_annotation_for_self(self, annotation, class_name):
        """Recursively process annotations to replace Self with the class name"""
        if isinstance(annotation, Name) and annotation.id == "Self":
            annotation.idSelf = class_name
        elif isinstance(annotation, Subscript):
            # Process the slice elements recursively
            if isinstance(annotation.slice, Tuple):
                for elt in annotation.slice.elts:
                    self._process_annotation_for_self(elt, class_name)
            else:
                self._process_annotation_for_self(annotation.slice, class_name)

    def visit_ClassDef(self, node: ClassDef) -> ClassDef:
        assert (
            self.imports_typing
        ), "typing must be imported in order to use datum classes"
        if self.imports_Self:
            for i, attribute in enumerate(node.body):
                if isinstance(attribute, FunctionDef):
                    for j, arg in enumerate(attribute.args.args):
                        self._process_annotation_for_self(arg.annotation, node.name)

                    self._process_annotation_for_self(attribute.returns, node.name)

        return node
