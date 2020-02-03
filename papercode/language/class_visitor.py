import libcst
from papercode.language.parser import Parser

class ClassVisitor(libcst.CSTTransformer):
    METADATA_DEPENDENCIES = (libcst.metadata.PositionProvider,)
    count = 0

    def __init__(self, module):
        self.module = module
        self.lparser = Parser()
        self.class_structure = []

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
        self.count += 1
        function_position = self.get_metadata(libcst.metadata.PositionProvider, original_node).start
        body_position = self.get_metadata(libcst.metadata.PositionProvider, original_node.body).start
        function_defition_length = body_position.line - function_position.line
        # print(original_node.name.value, '\t', function_defition_length, '\t', function_position.line)
        new_fstr = self.empty_function_body(self.module.code_for_node(original_node), function_defition_length)
        new_fdef = self.lparser.parse_module(new_fstr).body[0]
        return updated_node.with_changes(body = new_fdef.body)
        # return updated_node

    def empty_function_body(self, function_str, def_lines):
        all_lines = function_str.splitlines()
        init_position = 0
        while 'def' not in all_lines[init_position]:
            init_position += 1
        function_lines = all_lines[init_position:(init_position + def_lines)]
        function_lines.append('\tpass\n')
        new_fstr = "\n".join(function_lines)
        return new_fstr