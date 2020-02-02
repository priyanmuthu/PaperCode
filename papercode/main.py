from CodeFile import CodeFile
from BaseDiv import EverythingBaseDiv
from SidebarDiv import SmallFunctionSidebarDiv
from CodePrinter import RegularCodePrinter
from SidebarCodePrinter import SidebarCodePrinter

def main():
    # file_path = 'papercode/temp/temp.py'
    # file_path = 'papercode/temp/temp2.py'
    file_path = 'papercode/temp/fpdf.py'
    # template_path = 'papercode/templates/template2.html'
    pdf_file_path = 'papercode/temp/pup.pdf'
    code_file = CodeFile(file_path)
    code_file.process()    
    base_div = EverythingBaseDiv(code_file)
    sidebar_div = SmallFunctionSidebarDiv(base_div, code_file, 3)
    code_printer = SidebarCodePrinter(pdf_file_path, code_file, base_div, sidebar_div)
    # print(code_printer.get_html())
    html_code = code_printer.print_code_file()
    print(html_code)


if __name__ == "__main__":
    main()