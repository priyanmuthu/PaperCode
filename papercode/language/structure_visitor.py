import libcst
from papercode.language.parser import Parser
from papercode.language.node import *

class StructureVisitor(libcst.CSTTransformer):
    METADATA_DEPENDENCIES = (libcst.metadata.PositionProvider, libcst.metadata.QualifiedNameProvider,)
    count = 0

    def __init__(self, wrapper, all_lines):
        self.wrapper = wrapper
        self.module = self.wrapper.module
        self.lparser = Parser()
        self.all_lines = all_lines
        

    def visit_Module(self, node: libcst.Module):
        module_start_position = self.get_metadata(libcst.metadata.PositionProvider, node).start
        module_end_position = self.get_metadata(libcst.metadata.PositionProvider, node).end
        self.syntax_tree = Node(self.module, module_start_position, module_end_position, None)
        self.current_parent_node = self.syntax_tree
        self.prev_comment = None

    def visit_ClassDef(self, node: libcst.ClassDef):
        class_start_position = self.get_metadata(libcst.metadata.PositionProvider, node).start
        class_end_position = self.get_metadata(libcst.metadata.PositionProvider, node).end
        body_start_postition = self.get_metadata(libcst.metadata.PositionProvider, node.body).start
        body_end_postition = self.get_metadata(libcst.metadata.PositionProvider, node.body).end
        class_node = ClassNode(
            node, 
            self.current_parent_node, 
            node.name.value, 
            class_start_position, 
            class_end_position, 
            body_start_postition, 
            body_end_postition)
        self.current_parent_node.children.append(class_node)
        self.current_parent_node = class_node
        return True
    
    def leave_ClassDef(self, original_node: libcst.ClassDef, updated_node: libcst.ClassDef) -> libcst.ClassDef:
        self.current_parent_node = self.current_parent_node.parent_node
        return original_node
    
    
    def visit_FunctionDef(self, node: libcst.FunctionDef):
        function_start_position = self.get_metadata(libcst.metadata.PositionProvider, node).start
        function_end_position = self.get_metadata(libcst.metadata.PositionProvider, node).end
        body_start_postition = self.get_metadata(libcst.metadata.PositionProvider, node.body).start
        body_end_postition = self.get_metadata(libcst.metadata.PositionProvider, node.body).end
        func_node = FunctionNode(
            node, 
            self.current_parent_node, 
            node.name.value, 
            function_start_position, 
            function_end_position, 
            body_start_postition, 
            body_end_postition)
        self.current_parent_node.children.append(func_node)
        self.current_parent_node = func_node
        return True

    def leave_FunctionDef(self, original_node: libcst.FunctionDef, updated_node: libcst.FunctionDef) -> libcst.FunctionDef:
        self.current_parent_node = self.current_parent_node.parent_node
        return original_node

    def visit_Call(self, node):
        # Not supported, if it is directly in the module
        if type(self.current_parent_node) is Node:
            return False
        call_start_position = self.get_metadata(libcst.metadata.PositionProvider, node).start
        call_end_position = self.get_metadata(libcst.metadata.PositionProvider, node).end
        # Get more info about the function
        func_cst = node.func
        if type(func_cst) is libcst._nodes.expression.Attribute:
            # Get the location of the attribute
            ref_start_position = self.get_metadata(libcst.metadata.PositionProvider, func_cst.attr).start
        else:
            ref_start_position = self.get_metadata(libcst.metadata.PositionProvider, func_cst).start

        call_node = CallNode(node, self.current_parent_node, node.func, call_start_position, call_end_position, ref_start_position)
        if type(self.current_parent_node) is FunctionNode:
            self.current_parent_node.function_calls.append(call_node)
        else:
            self.current_parent_node.children.append(call_node)
        return False
    
    def visit_Comment(self, node):
        comment_start_position = self.get_metadata(libcst.metadata.PositionProvider, node).start
        comment_end_position = self.get_metadata(libcst.metadata.PositionProvider, node).end
        comment_line = self.all_lines[comment_start_position.line - 1].strip()
        if comment_start_position.line == comment_end_position.line and comment_line[0] != '#':
            return True
        
        # Check if the previous comment is a line before this
        if not (self.prev_comment is None) and self.prev_comment.end_pos.line == (comment_start_position.line - 1):
            # append to the prev comment
            self.prev_comment.end_pos = comment_end_position
            return True
        
        comment_node = CommentNode(
            node, 
            self.current_parent_node, 
            comment_start_position, 
            comment_end_position)
        self.current_parent_node.children.append(comment_node)
        self.prev_comment = comment_node
        return True