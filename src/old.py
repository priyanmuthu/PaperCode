def get_code_structure(source_code):
    p = parser.Parser()
    wrapper = p.parse_module_with_metadata(source_code)
    visited_tree = wrapper.visit(ClassVisitor.ClassVisitor(wrapper.module))
    # print(wrapper.module)
    return visited_tree.code

def get_better_code_structure(source_code):
    p = parser.Parser()
    wrapper = p.parse_module_with_metadata(source_code)
    structure_visitor = StructureVisitor.StructureVisitor(wrapper.module)
    wrapper.visit(structure_visitor)
    class_structure_lines = structure_visitor.get_class_structure_lines()
    all_lines = source_code.splitlines()
    structure_lines = []
    for line in class_structure_lines:
        structure_lines.append(all_lines[line-1])
    
    structure_code = "\n\n".join(structure_lines)
    return structure_code

def get_references(source_code, file_path):
    script = jedi.Script(source=source_code, path=file_path, line=3, column=8)
    # print(script.goto_definitions())
    # print(script.goto_definitions()[0], type(script.goto_definitions()[0]))
    # print(script.goto_definitions()[0].line, script.goto_definitions()[0].column)
    print(script.usages())

def traverse_cst_and_find_call(cst_node, call_nodes = []):
    print(type(cst_node))
    if(type(cst_node) == libcst._nodes.expression.Call):
        print(cst_node)
    for child in cst_node.children:
        traverse_cst_and_find_call(child)