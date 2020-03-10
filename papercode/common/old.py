from language import parser
from language import ClassVisitor
from language import StructureVisitor
from language import Highlighter
from language import Node
from lxml import etree
from bs4 import BeautifulSoup
from pyppeteer import launch
import asyncio
import libcst
# from fpdf import FPDF, HTMLMixin
# from PyQt5.QtGui import QTextDocument, QPrinter, QApplication
# from weasyprint import HTML
import sys
import pdfkit
import jedi

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

class PaperOptions:
    def __init__(self, paper_size, max_lines):
        self.paper_size = paper_size
        self.max_lines = max_lines

print_paper = {
    'a4': PaperOptions('a4', '100')
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

def get_pre_formated_text(partition):
    partition_code = '\n'.join(partition['source_code_lines'])
    partition_html = highlight(partition_code)
    soup = BeautifulSoup(partition_html, 'html.parser')
    res = soup.find('table')
    td_line_nos = res.find('td')
    td_code = td_line_nos.find_next_sibling()
    code_preformated_text = td_code.find('pre')
    #generating line_preformated_text
    line_soup = soup.new_tag('pre')
    line_soup.string = '' + '\n'.join(str(lno) for lno in partition['line_nos'])
    return line_soup, code_preformated_text

def generate_partitions(source_code, flat_tree, paper_options = print_paper['a4']):
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

def get_html_from_partitions(html_template_path, source_code, partitions):
    template_text = text_from_file(html_template_path)
    soup = BeautifulSoup(template_text, 'html.parser')
    line_no_div = soup.find('div', {'class': 'linenodiv'})
    highlight_div = soup.find('div', {'class': 'highlight'})
    line_nos = []
    code_lines = []
    for p in partitions:
        # print(p)
        _, code_p = get_pre_formated_text(p)
        pcode = str(code_p).splitlines()[:p['length']]
        pcode = '\n'.join(pcode)
        pcode = pcode.replace('<pre>', '', 1).replace('</pre>', '', 1)
        line_nos.append('\n'.join(str(lno) for lno in p['line_nos']))
        code_lines.append(pcode)

    # preformatted_line = soup.new_tag('pre')
    # preformatted_line.string = '\n'.join(line_nos)
    # preformatted_code = soup.new_tag('pre')
    # preformatted_code.append(BeautifulSoup('\n'.join(code_lines), 'html.parser'))
    # print(code_lines[2])
    # print('xxxxxxx')
    # print(line_nos[2])
    # print('xxxxxxx')
    # print(partitions[2]['source_code_lines'])
    preformatted_line = '<pre>' + '\n'.join(line_nos) + '</pre>'
    preformatted_code = '<pre>' + '\n'.join(code_lines) + '</pre>'
    line_no_div.append(BeautifulSoup(preformatted_line, 'html.parser'))
    highlight_div.append(BeautifulSoup(preformatted_code, 'html.parser'))
    return soup
    # line_p, code_p = get_pre_formated_text(partitions[0])
    # print(line_p)
    # print(code_p)

    # pass

async def get_pdf(html_code):
    browser = await launch()
    page = await browser.newPage()
    await page.setContent(html_code)
    await page.pdf({
        'path': 'papercode/temp/pup.pdf',
        'format': 'A4',
        'printBackground': True,
        'margin': { 'top': "1cm", 'bottom': "1cm", 'left': "1cm", 'right': "1cm" }
    })
    await browser.close()

# def main():
#     file_path = 'papercode/temp/fpdf.py'
#     template_path = 'papercode/template.html'
#     source_code = text_from_file(file_path)
#     # html_code = highlight(source_code)
#     syntax_tree = generate_syntax_tree(source_code)
#     flat_tree = []
#     flatten_syntax_tree(syntax_tree, [Node.CallNode], flat_tree)
#     partitions = generate_partitions(source_code, flat_tree)
#     final = get_html_from_partitions(template_path, source_code, partitions)
#     final_code = str(final)
#     asyncio.get_event_loop().run_until_complete(get_pdf(final_code))
#     # generate_pdf(final_code, 'papercode/temp/gen2.pdf')
#     print(final_code)
#     # print(html_code)
#     # get_html_table(html_code)
#     # code_structure = get_code_structure(source_code) 
#     # code_structure = get_better_code_structure(source_code) 
#     # html_code = highlight(code_structure)
#     # # # print(html_code)
#     # print(syntax_tree.cst_node)
#     # get_references(source_code, file_path)

def generate_html_from_template(html_template_path, line_nos, code_lines):
    template_text = text_from_file(html_template_path)
    soup = BeautifulSoup(template_text, 'html.parser')
    line_no_div = soup.find('div', {'class': 'linenodiv'})
    highlight_div = soup.find('div', {'class': 'highlight'})
    preformatted_line = '<pre>' + '\n'.join(line_nos) + '</pre>'
    preformatted_code = '<pre>' + '\n'.join(code_lines) + '</pre>'
    line_no_div.append(BeautifulSoup(preformatted_line, 'html.parser'))
    highlight_div.append(BeautifulSoup(preformatted_code, 'html.parser'))
    return str(soup)

def get_html_from_partitions(html_template_path, source_code, partitions, paper_options):
    line_nos = []
    code_lines = []
    line_count = 0
    for p in partitions:
        if (line_count + p['length']) >= paper_options.max_lines and (paper_options.max_lines - line_count) < paper_options.max_lines/2:
            remaining_lines = paper_options.max_lines - line_count
            empty_str = '\n'.join('' for i in range(remaining_lines)) + '<p style="page-break-before: always"></p>'
            line_nos.append(empty_str)
            code_lines.append(empty_str)
            line_count = 0
        _, code_p = get_pre_formated_text(p)
        pcode = str(code_p).splitlines()[:p['length']]
        pcode = '\n'.join(pcode)
        pcode = pcode.replace('<pre>', '', 1).replace('</pre>', '', 1)
        line_str = '\n'.join(str(lno) for lno in p['line_nos'])
        line_nos.append(line_str)
        code_lines.append(pcode)
        line_count += p['length']
    return generate_html_from_template(html_template_path, line_nos, code_lines)

    def get_references(source_code, file_path):
        script = jedi.Script(source=source_code, path=file_path, line=47, column=9)
        # print(script.goto_definitions()[0].line)
        # print(script.goto_definitions()[0], type(script.goto_definitions()[0]))
        # print(script.goto_definitions()[0].line, script.goto_definitions()[0].column)
        uses = script.usages()
        for u in uses:
            print(u, u.line, u.column)


# <tr style="position:relative;">
#   <td style="position:relative;"></td>
#   <td style="position:relative;"></td>
#   <td></td>
#   <td style="position:relative;">
#     <img style="width: 100px; height: 100px; position:absolute; left:-200px; top: 10px;" src="data:image/png;base64,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">
#   </td style="position:relative;">
# </tr>