import libcst as cst

class Parser:
    def __init__(self):
        pass
    def parse_expression(self, exp_str):
        return cst.parse_expression(exp_str)
    def parse_statement(self, stat_str):
        return cst.parse_statement(stat_str)
    def parse_module(self, module_str):
        return cst.parse_module(module_str)