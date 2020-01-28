from language import parser
from language import StructureVisitor
from language import Highlighter
from language import Node
from bs4 import BeautifulSoup
import jedi

class PaperOptions:
    def __init__(self, paper_size, max_lines):
        self.paper_size = paper_size
        self.max_lines = max_lines

print_paper = {
    'A4': PaperOptions('A4', 96)
}

def text_from_file(file_path):
    f = open(file_path, 'r')
    file_text = f.read()
    f.close()
    return file_text

def post_process_syntax_tree(source_code: str, file_path: str, syntax_tree: Node.Node):
    functions = []
    flatten_syntax_tree(syntax_tree, [Node.Node, Node.ClassNode, Node.CallNode], functions)
    script = jedi.Script(source=source_code, path=file_path)
    function_line_dict = {f.start_pos.line : f for f in functions}
    # print(function_line_dict)
    for func in functions:
        if type(func) is not Node.FunctionNode:
            continue
        # get all the calls and point it to the actual function
        calls = func.function_calls
        for fc in calls:
            # Get the function call location and find the function node
            func_defs = script.goto(fc.ref_pos.line, fc.ref_pos.column)
            if len(func_defs) == 0:
                continue
            
            if func_defs[0].line not in function_line_dict:
                continue
            qf = function_line_dict[func_defs[0].line]
            fc.function_node = qf
            qf.refs.append(fc)

def generate_syntax_tree(source_code, file_path):
    p = parser.Parser()
    wrapper = p.parse_module_with_metadata(source_code)
    structure_visitor = StructureVisitor.StructureVisitor(wrapper)
    wrapper.visit(structure_visitor)
    post_process_syntax_tree(source_code, file_path, structure_visitor.syntax_tree)
    return structure_visitor.syntax_tree

def flatten_syntax_tree(tree_node, filter_types = [], flat_tree = []):
    if(type(tree_node) not in filter_types):
        flat_tree.append(tree_node)
    
    for child in tree_node.children:
        flatten_syntax_tree(child, filter_types, flat_tree)


def print_syntax_tree(tree_node):
    tree_node.print()
    for child in tree_node.children:
        print_syntax_tree(child)

def isBlank (myString):
    return not (myString and myString.strip())

def generate_partitions(source_code, flat_tree, paper_options = print_paper['A4']):
    partitions = []
    all_lines = source_code.splitlines()
    
    if len(flat_tree) == 0:
        return None
    # Include everython before the first non-Node
    elif len(flat_tree) == 1:
        # Only Node is present - include all the html
        partitions.append(get_partition(all_lines, 1, len(all_lines)+1))
    else:
        # Find the first Non-root node, and include everything before it
        first_non_root = flat_tree[1]
        start_line = 1
        end_line = first_non_root.start_pos.line
        partitions.append(get_partition(all_lines, start_line, end_line-1))

        tail_nodes = flat_tree[1:]
        # get HTML for all the other nodes.
        for tnode in tail_nodes:
            # for each node, if it gets borken within the page, then start from a new page
            if type(tnode) is Node.ClassNode:
                partitions.append(get_partition(all_lines, tnode.start_pos.line, tnode.body_start_pos.line - 1))
            elif type(tnode) is Node.FunctionNode:
                partitions.append(get_partition(all_lines, tnode.start_pos.line, tnode.end_pos.line))
        
    return partitions

def get_partition(all_lines, start_line, end_line):
    line_nos = [i for i in range(start_line, end_line+1)]
    source_code_lines = list(map(lambda x: all_lines[x-1], line_nos))
    return {'line_nos': line_nos, 'source_code_lines': source_code_lines, 'length': len(line_nos)}