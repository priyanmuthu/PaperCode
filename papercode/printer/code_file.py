from papercode.language import parser, structure_visitor
from papercode.language.node import *
from papercode.common.utils import UtilMethods, Language, Position
from toposort import toposort_flatten
from os.path import abspath
import jedi
import json
import tempfile
import subprocess

class CodeFile:
    def __init__(self, file_path: str, project_path: str = None, lang: Language = Language.Python):
        self.file_path = file_path
        self.project_path = project_path
        self.source_code = UtilMethods.text_from_file(file_path)
        self.all_lines = self.source_code.splitlines()
        self.syntax_tree = None
        self.language = lang
    
    def process(self):
        pass
    
    def print_tree(self, node, tabspaces = ''):
        if type(node) == Node:
            print('', tabspaces ,'Node: ', node.start_pos.line)
        elif type(node) == ClassNode:
            print('', tabspaces ,'Class: ', node.name, ' @ ', node.start_pos.line)
        elif type(node) == InterfaceNode:
            print('', tabspaces ,'Interface: ', node.name, ' @ ', node.start_pos.line)
        elif type(node) == FunctionNode:
            print('', tabspaces ,'Function: ', node.name, ' @ ', node.start_pos.line)
        elif type(node) == CommentNode:
            print('', tabspaces ,'Comment @ ', node.start_pos, ' - ', node.end_pos)
        
        for child in node.children:
            self.print_tree(child, tabspaces + '\t')

    def get_partition(self, start_line, end_line, partition_type):
        line_nos = [i for i in range(start_line, end_line+1)]
        source_code_lines = list(map(lambda x: self.all_lines[x-1], line_nos))
        return {
            'line_nos': line_nos, 
            'source_code_lines': source_code_lines, 
            'length': len(line_nos), 
            'partition_type': partition_type
            }
    
    def get_hidden_comment_node(self, start_line, end_line, hide_string, partition_type):
        line_nos = [start_line]
        source_code_lines = [hide_string]
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

class PyCodeFile(CodeFile):
    def __init__(self, file_path: str, project_path: str = None):
        super().__init__(file_path, project_path, Language.Python)
        self.jedi_script = jedi.Script(source=self.source_code, path=self.file_path)

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

class TsCodeFile(CodeFile):
    def __init__(self, file_path: str, project_path: str = None):
        super().__init__(file_path, project_path, Language.Typescript)
        self.node_dict = {}
        self.ref_dict = {}
        self.call_func = {}
        self.tsc_path = abspath('../PaperCode/papertsc/dist/app.js')
        self.class_nodes = []

    def process(self):
        self.generate_syntax_tree()
        self.post_process_syntax_tree() 

    def get_ts_parsed_json(self):
        temp_filename = tempfile.mktemp()
        command = ['node', self.tsc_path, '-p', self.project_path, '-f', self.file_path, '-o', temp_filename]
        process = subprocess.Popen(command, stdout=subprocess.PIPE)
        process.wait()
        # print(process.returncode)
        if process.returncode != 0:
            print(process.returncode)
            print('-------------------\n\n\n\n')
            raise Exception('Cannot parse typescript file')
        return UtilMethods.text_from_file(temp_filename)

    def generate_syntax_tree(self):
        
        json_text = self.get_ts_parsed_json()
        json_obj = json.loads(json_text)
        root_node = self.create_node(json_obj)
        # print(self.create_node(json_obj))
        # self.print_tree(root_node)
        self.syntax_tree = root_node
        
    def create_node(self, json_obj):
        start_pos = self.getPositionFromJson(json_obj['start_pos'])
        end_pos = self.getPositionFromJson(json_obj['end_pos'])
        if json_obj['kind'] == 0: # Node
            node =  Node(None, start_pos, end_pos)
        elif json_obj['kind'] == 1: # Class Node
            name = json_obj['name']
            body_start_pos = self.getPositionFromJson(json_obj['body_start_pos'])
            body_end_pos = self.getPositionFromJson(json_obj['body_end_pos'])
            node = ClassNode(None, self.node_dict[json_obj['parentuid']], name, start_pos, end_pos, body_start_pos, body_end_pos)
            self.class_nodes.append(node)
        elif json_obj['kind'] == 2: # Interface Node
            name = json_obj['name']
            node = InterfaceNode(None, self.node_dict[json_obj['parentuid']], name, start_pos, end_pos, start_pos, end_pos)
        elif json_obj['kind'] == 3: # Function Node
            name = json_obj['name']
            body_start_pos = self.getPositionFromJson(json_obj['body_start_pos'])
            body_end_pos = self.getPositionFromJson(json_obj['body_end_pos'])
            node = FunctionNode(None, self.node_dict[json_obj['parentuid']], name, start_pos, end_pos, body_start_pos, body_end_pos)
        elif json_obj['kind'] == 4: # Call Node
            node = CallNode(None, self.node_dict[json_obj['parentuid']], None, start_pos, end_pos, start_pos)
            # add func stuff
            self.call_func[node] = json_obj['func']
        elif json_obj['kind'] == 5: # Comment Node
            node = CommentNode(None, self.node_dict[json_obj['parentuid']], start_pos, end_pos)
        
        # adding the node to uid dict
        self.node_dict[json_obj['uid']] = node

        #Extra processing for functions
        if json_obj['kind'] == 3: # Function Node
            # processing function calls
            for fc in json_obj['function_calls']:
                node.function_calls.append(self.create_node(fc))
            # add references for post processing
            self.ref_dict[node] = json_obj['refs']

        for child in json_obj['children']:
            node.children.append(self.create_node(child))
        return node

    def getPositionFromJson(self, json_pos):
        pos = Position(json_pos['line'], json_pos['column'])
        return pos

    def post_process_syntax_tree(self):
        # Post processing for TS

        # Functions in call expressions
        for call in self.call_func:
            call.function_node = self.node_dict[self.call_func[call]]
            call.from_function_node = call.parent_node

        # Function references
        for func in self.ref_dict:
            for ref in self.ref_dict[func]:
                func.refs.append(self.node_dict[ref])
        
        # Squashing comments:
        self.squash_comments(self.syntax_tree)

        # Topological sort
        # For each class, perform the topological sort
        for cNode in self.class_nodes:
            self.topo_sort(cNode)
    

    def topo_sort(self, cnode: ClassNode):
        # Sort all the functions into topological order
        functions = []
        topo_dict= {}

        for child in cnode.children:
            if type(child) == FunctionNode:
                functions.append(child)
        
        # Setting the defalt topo order:
        cnode.topo_order = functions

        for func in functions:
            calls = set()
            for fcall in func.function_calls:
                if func != fcall.function_node and fcall.function_node in functions:
                    calls.add(fcall.function_node)
            topo_dict[func] = calls
        
        try:
            cnode.topo_order = toposort_flatten(topo_dict, sort=False)
        except:
            pass      

    
    def squash_comments(self, node: Node):
        if type(node) == CommentNode:
            return
        combine_stack = []
        comment_stack = []
        for child in node.children:
            if type(child) != CommentNode:
                if len(comment_stack) > 1:
                    combine_stack.append(comment_stack)
                comment_stack = []
                continue

            if len(comment_stack) == 0:
                comment_stack.append(child)
            else:
                if comment_stack[-1].end_pos.line + 1 == child.start_pos.line:
                    comment_stack.append(child)
                else:
                    # Combine and nuke the stack
                    if len(comment_stack) > 1:
                        combine_stack.append(comment_stack)
                    comment_stack = []
                    comment_stack.append(child)
        
        if(len(comment_stack) > 1):
            combine_stack.append(comment_stack)

        # actually combining
        for comb_stc in combine_stack:
            self.combine_comments(node, comb_stc)
        
        for ch in node.children:
            self.squash_comments(ch)

    def combine_comments(self, node, comment_stack):
        multi_comment = CommentNode(comment_stack[0], node, comment_stack[0].start_pos, comment_stack[-1].end_pos)
        multi_comment.is_single = True
        child_idx = node.children.index(comment_stack[0])
        node.children[child_idx] = multi_comment
        for cs in comment_stack[1:]:
            node.children.remove(cs)

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