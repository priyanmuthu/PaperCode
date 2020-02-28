from papercode.printer.code_file import CodeFile, PyCodeFile, TsCodeFile
from papercode.printer.base_div import EverythingBaseDiv, EmptyBaseDiv, BigFunctionBaseDiv
from papercode.printer.configurable_base_div import ConfigurableBaseDiv
from papercode.printer.sidebar_div import SmallFunctionSidebarDiv, ReferencesSidebarDiv
from papercode.printer.code_printer import RegularCodePrinter
from papercode.printer.sidebar_code_printer import SidebarCodePrinter
from papercode.printer.configurable_code_printer import ConfigurableCodePrinter
from papercode.common.utils import UtilMethods, Language
from os.path import abspath
import difflib

def run():
    # runpy()
    runts()
    # file_compare_test()
    # pdf_test()

def pdf_test():
    pdf_file_path = abspath('papercode/temp/pup2.pdf')
    raw = parser.from_file(pdf_file_path)
    print(raw['content'])

def file_compare_test():
    # https://stackoverflow.com/questions/9505822/getting-line-numbers-that-were-changed
    # + for add - for delete maybe use ? ??
    file_path_1 = abspath('../PaperCode/papertsc/test/project1/pytutor.ts')
    file_path_2 = abspath('../PaperCode/papertsc/test/pytutor.ts')

    f1 = open(file_path_1, 'r')
    f1_lines = f1.readlines()
    f1.close()

    f2 = open(file_path_2, 'r')
    f2_lines = f2.readlines()
    f2.close()

    diff = difflib.ndiff(f1_lines, f2_lines)
    for line in diff:
        print(line)

def runts():
    file_path = abspath('../PaperCode/papertsc/test/project1/pytutor.ts')
    project_path = abspath('../PaperCode/papertsc/test/project1/**/*.ts')
    pdf_file_path = abspath('papercode/temp/pup2.pdf')
    html_path = abspath('papercode/temp/high3.html')
    code_file = TsCodeFile(file_path, project_path)
    code_file.process()
    # code_file.print_tree(code_file.syntax_tree)
    # return
    base_div = ConfigurableBaseDiv(code_file)
    sidebar_div = None
    # sidebar_div = ReferencesSidebarDiv(base_div, code_file, 3)
    code_printer = ConfigurableCodePrinter(pdf_file_path, code_file, base_div, sidebar_div)
    html_code = code_printer.print_code_file()
    # html_code = code_printer.get_html()
    # print(html_code)
    UtilMethods.write_text_to_file(html_path, html_code)

def runpy():
    # file_path = 'papercode/temp/temp.py'
    # file_path = 'papercode/temp/temp2.py'
    html_path = 'papercode/temp/high.html'
    file_path = 'papercode/temp/fpdf.py'
    # file_path = 'D:/PV/Research/PaperCode/papertsc/temp/project1/pytutor.ts'
    # template_path = 'papercode/templates/template2.html'
    pdf_file_path = 'papercode/temp/pup.pdf'
    code_file = PyCodeFile(file_path)
    code_file.process()
    # code_file.print_tree(code_file.syntax_tree)
    base_div = ConfigurableBaseDiv(code_file)
    # base_div = EverythingBaseDiv(code_file)
    # sidebar_div = SmallFunctionSidebarDiv(base_div, code_file, 3)
    # base_div = BigFunctionBaseDiv(code_file)
    # sidebar_div = ReferencesSidebarDiv(base_div, code_file, 3)
    sidebar_div = None
    # code_printer = SidebarCodePrinter(pdf_file_path, code_file, base_div, sidebar_div)
    code_printer = ConfigurableCodePrinter(pdf_file_path, code_file, base_div, sidebar_div)
    # print(code_printer.get_html())
    html_code = code_printer.print_code_file()
    # print(html_code)
    UtilMethods.write_text_to_file(html_path, html_code)