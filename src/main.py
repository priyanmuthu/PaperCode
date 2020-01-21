from language import parser
from language import ClassVisitor
from language import StructureVisitor
from language import Highlighter
from language import Node
from lxml import etree
from bs4 import BeautifulSoup
import libcst
# from fpdf import FPDF, HTMLMixin
# from PyQt5.QtGui import QTextDocument, QPrinter, QApplication
# from weasyprint import HTML
import sys
import pdfkit
import jedi

class PaperOptions:
    def __init__(self, paper_size, max_lines):
        self.paper_size = paper_size
        self.max_lines = max_lines

print_paper = {
    'a4': PaperOptions('a4', '60')
}

def text_from_file(file_path):
    f = open(file_path, 'r')
    file_text = f.read()
    f.close()
    return file_text

def highlight(source_code):
    highlighter = Highlighter.Highlighter()
    return highlighter.highlight_python_file(source_code)


def generate_pdf(html_text, pdf_file_path):
    options = {
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
    }
    pdfkit.from_string(html_text, pdf_file_path, options=options)


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

def get_references(source_code, file_path):
    script = jedi.Script(source=source_code, path=file_path, line=3, column=8)
    # print(script.goto_definitions())
    # print(script.goto_definitions()[0], type(script.goto_definitions()[0]))
    # print(script.goto_definitions()[0].line, script.goto_definitions()[0].column)
    print(script.usages())

def get_pre_formated_text(html_code):
    soup = BeautifulSoup(html_code, 'html.parser')
    res = soup.find('table')
    td_line_nos = res.find('td')
    td_code = td_line_nos.find_next_sibling()
    code_preformated_text = td_code.find('pre')
    print(code_preformated_text)

def generate_proper_html(source_code, flat_tree, paper_options = print_paper['a4']):
    line_nos = []
    source_code_lines = []
    all_lines = source_code.splitlines()

    if len(flat_tree) == 0:
        return None
    # Include everython before the first non-Node
    elif len(flat_tree) == 1:
        # Only Node is present - include all the html
        return highlight(source_code)
    else:
        # Find the first Non-root node, and include everything before it
        first_non_root = flat_tree[1]
        start_line = 1
        end_line = first_non_root.start_pos.line
        for i in range (start_line, end_line):
            line_nos.append(i)
            source_code_lines.append(all_lines[i-1])
        
        tail_nodes = flat_tree[1:]
        # get HTML for all the other nodes.
        for node in tail_nodes:
            # for each node, if it gets borken within the page, then start from a new page
            pass

def main():
    file_path = 'src/temp/temp.py'
    source_code = text_from_file(file_path)
    html_code = highlight(source_code)
    # print(html_code)
    # get_html_table(html_code)
    # code_structure = get_code_structure(source_code) 
    # code_structure = get_better_code_structure(source_code) 
    # html_code = highlight(code_structure)
    # # # print(html_code)
    # generate_pdf(html_code, 'temp/gen2.pdf')
    syntax_tree = generate_syntax_tree(source_code)
    flat_tree = []
    flatten_syntax_tree(syntax_tree, [Node.CallNode], flat_tree)
    generate_proper_html(source_code, flat_tree)
    # print(syntax_tree.cst_node)
    # get_references(source_code, file_path)




if __name__ == "__main__":
    main()