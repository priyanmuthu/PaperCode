from papercode.language import parser, structure_visitor
from papercode.language.node import *
from papercode.common.utils import UtilMethods
import jedi

class CodeFile:
    def __init__(self, file_path: str, project_path: str = None):
        self.file_path = file_path
        self.project_path = project_path
        self.source_code = UtilMethods.text_from_file(file_path)
        self.all_lines = self.source_code.splitlines()
        self.jedi_script = jedi.Script(source=self.source_code, path=self.file_path)
        self.syntax_tree = None

    def process(self):
        self.generate_syntax_tree()
        self.post_process_syntax_tree() 

    def generate_syntax_tree(self):
        p = parser.Parser()
        wrapper = p.parse_module_with_metadata(self.source_code)
        svisitor = structure_visitor.StructureVisitor(wrapper)
        wrapper.visit(svisitor)
        self.syntax_tree = svisitor.syntax_tree
    
    def post_process_syntax_tree(self):
        if self.syntax_tree is None:
            return
        functions = []
        UtilMethods.flatten_syntax_tree(self.syntax_tree, [Node, ClassNode, CallNode], functions)
        function_line_dict = {f.start_pos.line : f for f in functions}
        # print(function_line_dict)
        for func in functions:
            if type(func) is not FunctionNode:
                continue
            # get all the calls and point it to the actual function
            calls = func.function_calls
            for fc in calls:
                # Get the function call location and find the function node
                func_defs = self.jedi_script.goto(fc.ref_pos.line, fc.ref_pos.column)
                if len(func_defs) == 0:
                    continue
                
                if func_defs[0].line not in function_line_dict:
                    continue
                qf = function_line_dict[func_defs[0].line]
                fc.function_node = qf
                fc.from_function_node = func
                qf.refs.append(fc)

    def generate_partitions(self):
        partitions = []
        flat_tree = []
        UtilMethods.flatten_syntax_tree(self.syntax_tree, [CallNode], flat_tree)
        
        if len(flat_tree) == 0:
            return None
        # Include everython before the first non-Node
        elif len(flat_tree) == 1:
            # Only Node is present - include all the html
            partitions.append(self.get_partition(1, len(self.all_lines)+1, Node))
        else:
            # Find the first Non-root node, and include everything before it
            first_non_root = flat_tree[1]
            start_line = 1
            end_line = first_non_root.start_pos.line
            partitions.append(self.get_partition(start_line, end_line-1, Node))

            tail_nodes = flat_tree[1:]
            # get HTML for all the other nodes.
            for tnode in tail_nodes:
                # for each node, if it gets borken within the page, then start from a new page
                if type(tnode) is ClassNode:
                    partitions.append(self.get_partition(tnode.start_pos.line, tnode.body_start_pos.line - 1, ClassNode))
                elif type(tnode) is FunctionNode:
                    partitions.append(self.get_partition(tnode.start_pos.line, tnode.end_pos.line, FunctionNode))
            
        return partitions

    def get_partition(self, start_line, end_line, partition_type):
        line_nos = [i for i in range(start_line, end_line+1)]
        source_code_lines = list(map(lambda x: self.all_lines[x-1], line_nos))
        return {
            'line_nos': line_nos, 
            'source_code_lines': source_code_lines, 
            'length': len(line_nos), 
            'partition_type': partition_type
            }
    def get_partition_from_node(self, cst_node):
        if type(cst_node) is Node:
            if len(cst_node.children) == 0:
                return self.get_partition(1, len(self.all_lines)+1, Node)
            return self.get_partition(1, cst_node.children[0].start_pos.line-1, Node)
        elif type(cst_node) is ClassNode:
            return self.get_partition(cst_node.start_pos.line, cst_node.body_start_pos.line - 1, ClassNode)
        elif type(cst_node) is FunctionNode:
            return self.get_partition(cst_node.start_pos.line, cst_node.end_pos.line, FunctionNode)