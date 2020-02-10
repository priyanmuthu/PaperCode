import * as ts from "ts-morph";
import * as pn from './papernode'

export function postProcess(rootNode: pn.PaperNode) {
    var functionNodes: pn.PaperNode[] = [];
    getAllNodesOfKind(rootNode, pn.NodeKind.Function, functionNodes);

    let function_dict = new Map<number, pn.FunctionNode>();
    functionNodes.forEach(fn => {
        function_dict.set(fn.start_pos.line, fn as pn.FunctionNode);
    });

    // Getting all the call expressions
    functionNodes.forEach(fn => {
        var funcNode = fn as pn.FunctionNode;
        funcNode.function_calls.forEach(fc => {
            // Find the actual definition of the call expression
            var fc_id = fc.compiler_node.getFirstChildByKind(ts.SyntaxKind.Identifier);
            if (fc_id === undefined) { return; }
            var defs = fc_id.getDefinitionNodes();
            if (defs.length === 0) { return; }
            var def = defs[0];
            console.log(`callexpr @ ${fc.start_pos.line} has definition at ${def.getStartLineNumber()} @ file: ${def.getSourceFile().getFilePath()}`);
        });
    });
}

function getAllNodesOfKind(node: pn.PaperNode, kind: pn.NodeKind, nodeList: pn.PaperNode[]) {
    if (node.kind === kind) {
        nodeList.push(node);
    }

    node.getChildren().forEach(child => {
        getAllNodesOfKind(child, kind, nodeList);
    });
}