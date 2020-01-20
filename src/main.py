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

def text_from_file(file_path):
    f = open(file_path, 'r')
    file_text = f.read()
    f.close()
    return file_text

def highlight(source_code):
    highlighter = Highlighter.Highlighter()
    return highlighter.highlight_python_file(source_code)

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
    print_syntax_tree(structure_visitor.syntax_tree)
    # print(wrapper.module)
    # traverse_cst_and_find_call(structure_visitor.syntax_tree.children[0].children[1].cst_node)

def print_syntax_tree(tree_node):
    tree_node.print()
    for child in tree_node.children:
        print_syntax_tree(child)

def traverse_cst_and_find_call(cst_node, call_nodes = []):
    print(type(cst_node))
    if(type(cst_node) == libcst._nodes.expression.Call):
        print(cst_node)
    for child in cst_node.children:
        traverse_cst_and_find_call(child)

def get_references(source_code, file_path):
    script = jedi.Script(source=source_code, path=file_path, line=3, column=8)
    # print(script.goto_definitions())
    # print(script.goto_definitions()[0], type(script.goto_definitions()[0]))
    # print(script.goto_definitions()[0].line, script.goto_definitions()[0].column)
    print(script.usages())

def get_html_table(html_code):
    # table = etree.HTML(html_code).find("body/table")
    # print(table)
    # print(etree.tostring(table))
    soup = BeautifulSoup(html_code, 'html.parser')
    res = soup.find('table')
    td_line_nos = res.find('td')
    td_code = td_line_nos.find_next_sibling()
    highlight_div = soup.find('div', {'class':'highlight'})
    preformated_text = highlight_div.find('pre')
    # td_code.
    # td_code = td_line_nos.find_add_next(td_line_nos)
    print(preformated_text)

def main():
    file_path = 'src/temp/temp2.py'
    source_code = text_from_file(file_path)
    html_code = highlight(source_code)
    get_html_table(html_code)
    # code_structure = get_code_structure(source_code) 
    # code_structure = get_better_code_structure(source_code) 
    # html_code = highlight(code_structure)
    # # # print(html_code)
    # generate_pdf(html_code, 'temp/gen2.pdf')
    # generate_syntax_tree(source_code)
    # get_references(source_code, file_path)




if __name__ == "__main__":
    main()