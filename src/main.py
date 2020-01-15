from language import parser
from language import ClassVisitor
from language import Highlighter
from fpdf import FPDF, HTMLMixin

class MyFPDF(FPDF, HTMLMixin):
    pass

def highlight():
    highlighter = Highlighter.Highlighter()
    html_out = highlighter.highlight_file('temp/fb_driver.py')
    

def gen_pdf():
    f = open("temp/high.html", 'r')
    html_out = f.read()
    f.close()
    pdf = MyFPDF()
    #First page
    pdf.add_page()
    pdf.write_html(html_out)
    pdf.output('temp/html.pdf', 'F')

def parsing():
    p = parser.Parser()
    # print(p.parse_expression("1+2"))
    f = open("temp/fpdf.py", 'r')
    file_str = f.read()
    f.close()
    wrapper = p.parse_module_with_metadata(file_str)
    visited_tree = wrapper.visit(ClassVisitor.ClassVisitor(wrapper.module))
    # print(wrapper.module.code)
    print(visited_tree.code)

def main():
    parsing()
    # highlight()
    # gen_pdf()

if __name__ == "__main__":
    main()