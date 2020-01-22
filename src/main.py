from language import parser
from language import ClassVisitor
from language import StructureVisitor
from language import Highlighter
from language import Node
from lxml import etree
from bs4 import BeautifulSoup
from pyppeteer import launch
from PyPDF2 import PdfFileWriter, PdfFileReader
import math
import asyncio
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
    'A4': PaperOptions('A4', 96)
}

def text_from_file(file_path):
    f = open(file_path, 'r')
    file_text = f.read()
    f.close()
    return file_text

def highlight(source_code):
    highlighter = Highlighter.Highlighter()
    return highlighter.highlight_python_file(source_code)

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
    pages = []
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
    

async def get_pdf(html_code, pdf_file_path):
    browser = await launch()
    page = await browser.newPage()
    await page.setContent(html_code)
    await page.pdf({
        'path': pdf_file_path,
        'format': 'A4',
        'printBackground': True,
        'margin': { 'top': "1cm", 'bottom': "1cm", 'left': "1cm", 'right': "1cm" }
    })
    await browser.close()

def generate_pdf_two_page_layout(pdf_file_path, out_path):
    input1 = PdfFileReader(open(pdf_file_path, "rb"))
    output = PdfFileWriter()
    for iter in range (0, input1.getNumPages()-1, 2):
        lhs = input1.getPage(iter)
        rhs = input1.getPage(iter+1)
        lhs.mergeTranslatedPage(rhs, lhs.mediaBox.getUpperRight_x(),0, True)
        output.addPage(lhs)
        sys.stdout.flush()

    # print("writing " + sys.argv[2])
    outputStream = open(out_path, "wb")
    output.write(outputStream)

def main():
    file_path = 'src/temp/fpdf.py'
    template_path = 'src/template.html'
    pdf_file_path = 'src/temp/pup.pdf'
    source_code = text_from_file(file_path)
    syntax_tree = generate_syntax_tree(source_code)
    flat_tree = []
    flatten_syntax_tree(syntax_tree, [Node.CallNode], flat_tree)
    partitions = generate_partitions(source_code, flat_tree)
    final_code = get_html_from_partitions(template_path, source_code, partitions, print_paper['A4'])
    asyncio.get_event_loop().run_until_complete(get_pdf(final_code, pdf_file_path))
    generate_pdf_two_page_layout(pdf_file_path, 'src/temp/pup2.pdf')
    # print(final_code)




if __name__ == "__main__":
    main()