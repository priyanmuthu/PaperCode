import * as ts from "ts-morph";
import * as pn from './papernode'
import { serialize } from 'typescript-json-serializer';

export function postProcess(rootNode: pn.PaperNode) {
    var functionNodes: pn.PaperNode[] = [];
    getAllNodesOfKind(rootNode, pn.NodeKind.Function, functionNodes);
    var sourceFilePath = rootNode.compiler_node.getSourceFile().getFilePath();
    // console.log(sourceFilePath);

    let function_dict = new Map<number, pn.FunctionNode>();
    functionNodes.forEach(fn => {
        function_dict.set(fn.start_pos.line, fn as pn.FunctionNode);
    });

    // Getting all the call expressions
    functionNodes.forEach(fn => {
        var funcNode = fn as pn.FunctionNode;
        funcNode.function_calls.forEach(fc => {
            // Find the actual definition of the call expression
            // console.log(`0: callexpr @ ${fc.start_pos.line}`);
            var fc_id = fc.compiler_node.getFirstDescendantByKind(ts.SyntaxKind.Identifier);
            if (fc_id === undefined) { return; }
            var defs = fc_id.getDefinitionNodes();
            if (defs.length === 0) { return; }
            var def = defs[0];
            var def_start_line = def.getStartLineNumber();
            // console.log(`1: def @ ${def_start_line}`);
            // console.log(`1: callexpr @ ${fc.start_pos.line} has definition at ${def.getStartLineNumber()} @ file: ${def.getSourceFile().getFilePath()}`);
            if (def.getSourceFile().getFilePath() !== sourceFilePath || !function_dict.has(def_start_line)) { return; }
            var df_func = function_dict.get(def_start_line)!;
            fc.func = df_func;
            df_func.addReference(fc);
            // console.log(`2: callexpr @ ${fc.start_pos.line} has definition at ${def.getStartLineNumber()} @ file: ${def.getSourceFile().getFilePath()};  Function: ${function_dict.get(def.getStartLineNumber())?.name}`);
        });
    });

    // Trying out serialization
    // var json = serialize(rootNode);
}

function getAllNodesOfKind(node: pn.PaperNode, kind: pn.NodeKind, nodeList: pn.PaperNode[]) {
    if (node.kind === kind) {
        nodeList.push(node);
    }

    node.getChildren().forEach(child => {
        getAllNodesOfKind(child, kind, nodeList);
    });
}