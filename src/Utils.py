from language import parser
from language import StructureVisitor
from language import Highlighter
from language import Node
from bs4 import BeautifulSoup

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

def generate_syntax_tree(source_code):
    p = parser.Parser()
    wrapper = p.parse_module_with_metadata(source_code)
    structure_visitor = StructureVisitor.StructureVisitor(wrapper)
    wrapper.visit(structure_visitor)
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