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