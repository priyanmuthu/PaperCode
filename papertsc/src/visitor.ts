import { Project, StructureKind } from "ts-morph";
import { readFileSync } from "fs";
import * as ts from "ts-morph";
import path from 'path'
import { visitNodes } from "typescript";
import * as pn from './papernode'

export function delint(sourceFile: ts.SourceFile) {
    var rootNode = new pn.PaperNode(sourceFile, getStartPosition(sourceFile), getEndPosition(sourceFile));
    var currentParent = rootNode;
    var tabSpaces: string[] = [];
    sourceFile.forEachChild(delintNode)
    // sourceFile.getChildren()[0].getChildren().forEach(child => {
    //     console.log(ts.SyntaxKind[child.getKind()]);
    // });
    // delintNode(sourceFile.getChildren()[0]);
    // delintNode(sourceFile);
    return rootNode;

    function delintNode(node: ts.Node) {

        // var pos = getStartPosition(node);
        // console.log(`${tabSpaces.join('')} node: ${ts.SyntaxKind[node.getKind()]} at (${pos.line}, ${pos.column}) \t children count: ${node.getChildCount()}`);
        switch (node.getKind()) {
            case ts.SyntaxKind.InterfaceDeclaration:
                if (currentParent.kind !== pn.NodeKind.Node) {
                    break;
                }
                var interface_node = node as ts.InterfaceDeclaration;
                console.log(`For the Class: ${interface_node.getName()} @ (${interface_node.getStartLineNumber()}, ${interface_node.getEndLineNumber()})`)
                var iNode = new pn.InterfaceNode(node,
                    currentParent,
                    interface_node.getName(),
                    getStartPosition(interface_node),
                    getEndPosition(interface_node));
                currentParent.addChildren(iNode);
                // Don't need to traverse the sub-trees for interface.
                break;

            case ts.SyntaxKind.ClassDeclaration:
                if (currentParent.kind !== pn.NodeKind.Node) {
                    break;
                }
                var class_node = node as ts.ClassDeclaration;
                console.log(`For the Class: ${class_node.getName()} @ (${class_node.getStartLineNumber()}, ${class_node.getEndLineNumber()})`)
                var cNode = new pn.ClassNode(node,
                    currentParent,
                    class_node.getName() || '',
                    getStartPosition(class_node),
                    getEndPosition(class_node),
                    getStartPosition(class_node),
                    getEndPosition(class_node));
                currentParent.addChildren(cNode);

                // We need to venture into classes
                var temp_parent = currentParent;    // Changing the parent to the current node
                currentParent = cNode;
                node.getChildren().forEach(child => {
                    delintNode(child);
                });
                currentParent = temp_parent;    // Changing back the parent
                break;
            
            case ts.SyntaxKind.MethodDeclaration:
                // Do something here
                // If parent is a function, skip it
                if (currentParent.kind === pn.NodeKind.Function) {
                    break;
                }
                var method_node = node as ts.MethodDeclaration;
                console.log(`For the Method: ${method_node.getName()} @ (${method_node.getStartLineNumber()}, ${method_node.getEndLineNumber()})`)
                var fNode = new pn.FunctionNode(node,
                    currentParent,
                    method_node.getName() || '',
                    getStartPosition(node),
                    getEndPosition(node),
                    getStartPosition(node),
                    getEndPosition(node));

                currentParent.addChildren(fNode);

                // We need to venture into Functions
                var temp_parent = currentParent;    // Changing the parent to the current node
                currentParent = fNode;
                node.getChildren().forEach(child => {
                    delintNode(child);
                });
                currentParent = temp_parent;    // Changing back the parent
                break;
                
            case ts.SyntaxKind.FunctionDeclaration:
                // Do something here
                // If parent is a function, skip it
                if (currentParent.kind === pn.NodeKind.Function) {
                    break;
                }
                var function_node = node as ts.FunctionDeclaration;
                console.log(`For the function: ${function_node.getName()} @ (${function_node.getStartLineNumber()}, ${function_node.getEndLineNumber()})`)
                var fNode = new pn.FunctionNode(node,
                    currentParent,
                    function_node.getName() || '',
                    getStartPosition(node),
                    getEndPosition(node),
                    getStartPosition(node),
                    getEndPosition(node));

                currentParent.addChildren(fNode);

                // We need to venture into Functions
                var temp_parent = currentParent;    // Changing the parent to the current node
                currentParent = fNode;
                node.getChildren().forEach(child => {
                    delintNode(child);
                });
                currentParent = temp_parent;    // Changing back the parent
                break;

            case ts.SyntaxKind.CallExpression:
                if (currentParent.kind !== pn.NodeKind.Function) {
                    break;
                }
                var call_expression = node as ts.CallExpression;
                console.log(`For the call_expression: @ (${call_expression.getStartLineNumber()}, ${call_expression.getEndLineNumber()})`)
                var fParentNode = currentParent as pn.FunctionNode;
                fParentNode.addFunctionCall(
                    new pn.CallNode(
                        call_expression, 
                        fParentNode, 
                        getStartPosition(call_expression), 
                        getEndPosition(call_expression))
                    );

                // Todo: Maybe traverse inside
                break;

            default:
                // Just add it as a regular papernode
                // console.log(`Other Node: ${ts.SyntaxKind[node.getKind()]} @ (${node.getStartLineNumber()}, ${node.getEndLineNumber()})`)
                node.getChildren().forEach(child => {
                    delintNode(child);
                });
                break;
        }
    }

    function report(node: ts.Node, message: string) {
        const { line, character } = sourceFile.compilerNode.getLineAndCharacterOfPosition(node.getStart());
        console.log(`${sourceFile.compilerNode.fileName} (${line + 1},${character + 1}): ${message}`);
    }

    function getStartPosition(node: ts.Node): pn.Position {
        var lineChar = sourceFile.compilerNode.getLineAndCharacterOfPosition(node.getStart());
        return new pn.Position(lineChar.line, lineChar.character);
    }

    function getEndPosition(node: ts.Node): pn.Position {
        var lineChar = sourceFile.compilerNode.getLineAndCharacterOfPosition(node.getStart());
        return new pn.Position(lineChar.line, lineChar.character);
    }
}

export function getAST(sourceFilesPath: string, tsFilePath: string) {
    // initialize
    const project = new Project({
        // Optionally specify compiler options, tsconfig.json, in-memory file system, and more here.
        // If you initialize with a tsconfig.json, then it will automatically populate the project
        // with the associated source files.
        // Read more: https://ts-morph.com/setup/
    });

    // add source files
    project.addSourceFilesAtPaths(sourceFilesPath);
    var pytutorSourceFile = project.getSourceFile(tsFilePath)!;

    delint(pytutorSourceFile);
}