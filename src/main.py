from Utils import *
from CodeFile import CodeFile
from CodePrinter import RegularCodePrinter
from SidebarCodePrinter import SidebarCodePrinter

def main():
    # file_path = 'src/temp/temp.py'
    # file_path = 'src/temp/temp2.py'
    file_path = 'src/temp/fpdf.py'
    template_path = 'src/templates/template2.html'
    pdf_file_path = 'src/temp/pup.pdf'
    code_file = CodeFile(file_path)
    code_file.process()    
    code_printer = SidebarCodePrinter(pdf_file_path, code_file)
    html_code = code_printer.print_code_file()
    print(html_code)


if __name__ == "__main__":
    main()