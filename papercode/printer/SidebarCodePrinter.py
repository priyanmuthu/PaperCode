from papercode.common.Utils import UtilMethods
from bs4 import BeautifulSoup
from papercode.printer.CodeFile import CodeFile
from papercode.printer.CodePrinter import CodePrinter
from papercode.printer.BaseDiv import BaseDiv
from papercode.printer.SidebarDiv import SidebarDiv
from papercode.language import Node

class SidebarCodePrinter(CodePrinter):
    def __init__(self, pdf_file_path: str, code_file: CodeFile, base_div: BaseDiv, sidebar_div: SidebarDiv):
        super().__init__(pdf_file_path, code_file)
        self.html_template_path = 'papercode/templates/sidebar.html'
        self.size_limit = 3
        self.base_div = base_div
        self.sidebar_div = sidebar_div
    
    def get_html(self):
        # todo: paper options
        # start with the syntax tree
        template_text = UtilMethods.text_from_file(self.html_template_path)
        soup = BeautifulSoup(template_text, 'html.parser')
        self.base_div.generate_html(soup)
        self.sidebar_div.generate_html(soup)
        return str(soup)

    def print_code_file(self):
        html_code = self.get_html()
        UtilMethods.get_pdf_sync(html_code, self.pdf_file_path)
        return html_code
