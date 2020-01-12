from language import parser
from language import ClassVisitor
from language import Highlighter

def highlight():
    highlighter = Highlighter.Highlighter()
    print(highlighter.highlight_file('temp/fb_driver.py'))

def parsing():
    p = parser.Parser()
    # print(p.parse_expression("1+2"))
    f = open("temp/fb_driver.py", 'r')
    file_str = f.read()
    f.close()
    wrapper = p.parse_module_with_metadata(file_str)
    visited_tree = wrapper.visit(ClassVisitor.ClassVisitor(wrapper.module))
    # print(wrapper.module.code)
    print(visited_tree.code)

def main():
    parsing()
    # highlight()

if __name__ == "__main__":
    main()