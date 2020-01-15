from language import parser
from language import ClassVisitor
from language import StructureVisitor
from language import Highlighter
# from fpdf import FPDF, HTMLMixin
# from PyQt5.QtGui import QTextDocument, QPrinter, QApplication
# from weasyprint import HTML
import sys
import pdfkit

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
    # print(wrapper.module.code)
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
    # app = QApplication(sys.argv)
    # doc = QTextDocument()
    # doc.setHtml(html_text)

    # printer = QPrinter()
    # printer.setOutputFileName(pdf_file_path)
    # printer.setOutputFormat(QPrinter.PdfFormat)
    # printer.setPageSize(QPrinter.A4);
    # printer.setPageMargins (15,15,15,15,QPrinter.Millimeter);
    # doc.print_(printer)
    # html = HTML('temp/high.html')
    # html.write_pdf(pdf_file_path)
    options = {
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
    }
    pdfkit.from_string(html_text, pdf_file_path, options=options)

def main():
    source_code = text_from_file('temp/fpdf.py')
    code_structure = get_code_structure(source_code) 
    html_code = highlight(code_structure)
    # print(html_code)
    generate_pdf(html_code, 'temp/gen.pdf')


if __name__ == "__main__":
    main()