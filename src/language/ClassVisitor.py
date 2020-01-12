import libcst
from .parser import Parser

class ClassVisitor(libcst.CSTTransformer):
    METADATA_DEPENDENCIES = (libcst.metadata.PositionProvider,)
    count = 0

    def __init__(self, module):
        self.module = module
        self.lparser = Parser()

    # def visit_ClassDef(self, node: libcst.ClassDef):
    #     pos = self.get_metadata(libcst.metadata.PositionProvider, node).start
    #     # print('class: ', node.name.value, ' at ', pos.line)
    #     return True
    
    # def visit_FunctionDef(self, node: libcst.FunctionDef):
    #     # print('Func: ', node.name.value)
    #     return False
    
    # def leave_ClassDef(self, original_node: libcst.ClassDef, updated_node: libcst.ClassDef) -> libcst.ClassDef:
    #     # print('Leaving class: ', node.name.value)
    #     print(self.module.code_for_node(updated_node))
    #     return updated_node
    
    def leave_FunctionDef(self, original_node: libcst.FunctionDef, updated_node: libcst.FunctionDef) -> libcst.FunctionDef:
        # print('Leaving Func: ', node.name.value)
        # return libcst.FunctionDef(updated_node.name.value.upper(), updated_node.params, updated_node.body)
        # print(self.module.code_for_node(original_node))
        new_fstr = self.empty_function_body(self.module.code_for_node(original_node))
        new_fdef = self.lparser.parse_module(new_fstr).body[0]
        # print(new_fdef)
        return updated_node.with_changes(body = new_fdef.body)

    def empty_function_body(self, function_str):
        def_line = 0
        all_lines = function_str.splitlines()
        while 'def' not in all_lines[def_line]:
            def_line += 1
        new_fstr = all_lines[def_line]
        new_fstr += '\n\tpass\n'
        # print(new_fstr)
        return new_fstr
