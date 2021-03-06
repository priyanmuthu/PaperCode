from papercode.common.utils import UtilMethods, print_paper, Paper
from bs4 import BeautifulSoup
from papercode.printer.code_file import CodeFile
from papercode.printer.code_printer import CodePrinter
from papercode.printer.base_div import BaseDiv
from papercode.printer.sidebar_div import SidebarDiv
from papercode.printer.configurable_base_div import ConfigurableBaseDiv

class ConfigurableCodePrinter(CodePrinter):
    def __init__(self, pdf_file_path: str, code_file: CodeFile, base_div: ConfigurableBaseDiv, sidebar_div: SidebarDiv):
        super().__init__(pdf_file_path, code_file)
        self.paper = print_paper['A4P']
        self.size_limit = 3
        self.base_div = base_div
        self.sidebar_div = sidebar_div

    
    def get_html(self):
        # todo: paper options
        # start with the syntax tree
        template_text = UtilMethods.text_from_file(self.paper.template_path)
        soup = BeautifulSoup(template_text, 'html.parser')
        self.base_div.generate_html(soup, self.paper)
        self.base_div.get_auxiliary_pages(soup)
        self.base_div.get_diff_auxiliary_pages(soup)

        return str(soup)

    def print_code_file(self):
        html_code = self.get_html()
        UtilMethods.get_pdf_sync(html_code, self.pdf_file_path)
        return html_code
