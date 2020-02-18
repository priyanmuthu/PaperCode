from papercode.printer.code_file import CodeFile, PyCodeFile, TsCodeFile
from papercode.printer.base_div import EverythingBaseDiv, EmptyBaseDiv, BigFunctionBaseDiv
from papercode.printer.configurable_base_div import ConfigurableBaseDiv
from papercode.printer.sidebar_div import SmallFunctionSidebarDiv, ReferencesSidebarDiv
from papercode.printer.code_printer import RegularCodePrinter
from papercode.printer.sidebar_code_printer import SidebarCodePrinter
from papercode.printer.configurable_code_printer import ConfigurableCodePrinter
from papercode.common.utils import UtilMethods, Language
from os.path import abspath

def run():
    # runpy()
    runts()

def runts():
    file_path = abspath('../PaperCode/papertsc/test/project1/pytutor.ts')
    project_path = abspath('../PaperCode/papertsc/test/project1/**/*.ts')
    pdf_file_path = abspath('papercode/temp/pup.pdf')
    html_path = abspath('papercode/temp/high3.html')
    code_file = TsCodeFile(file_path, project_path)
    code_file.process()
    # code_file.print_tree(code_file.syntax_tree)
    # return
    base_div = ConfigurableBaseDiv(code_file)
    # sidebar_div = None
    sidebar_div = ReferencesSidebarDiv(base_div, code_file, 3)
    code_printer = ConfigurableCodePrinter(pdf_file_path, code_file, base_div, sidebar_div)
    html_code = code_printer.print_code_file()
    # html_code = code_printer.get_html()
    # print(html_code)
    html_file = open(html_path, 'w')
    html_file.write(html_code)
    html_file.close()

def runpy():
    # file_path = 'papercode/temp/temp.py'
    file_path = 'papercode/temp/temp2.py'
    # file_path = 'papercode/temp/fpdf.py'
    # file_path = 'D:/PV/Research/PaperCode/papertsc/temp/project1/pytutor.ts'
    # template_path = 'papercode/templates/template2.html'
    pdf_file_path = 'papercode/temp/pup.pdf'
    code_file = PyCodeFile(file_path)
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