from papercode.printer.code_file import CodeFile
from papercode.printer.base_div import EverythingBaseDiv, EmptyBaseDiv, BigFunctionBaseDiv
from papercode.printer.sidebar_div import SmallFunctionSidebarDiv, ReferencesSidebarDiv
from papercode.printer.code_printer import RegularCodePrinter
from papercode.printer.sidebar_code_printer import SidebarCodePrinter

def run():
    # file_path = 'papercode/temp/temp.py'
    file_path = 'papercode/temp/temp2.py'
    # file_path = 'papercode/temp/fpdf.py'
    # template_path = 'papercode/templates/template2.html'
    pdf_file_path = 'papercode/temp/pup.pdf'
    code_file = CodeFile(file_path)
    code_file.process()    
    base_div = EverythingBaseDiv(code_file)
    # sidebar_div = SmallFunctionSidebarDiv(base_div, code_file, 3)
    # base_div = BigFunctionBaseDiv(code_file)
    # sidebar_div = ReferencesSidebarDiv(base_div, code_file, 3)
    sidebar_div = None
    code_printer = SidebarCodePrinter(pdf_file_path, code_file, base_div, sidebar_div)
    # print(code_printer.get_html())
    html_code = code_printer.print_code_file()
    print(html_code)