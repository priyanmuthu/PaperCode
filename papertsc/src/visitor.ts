import { Project, StructureKind } from "ts-morph";
import { readFileSync } from "fs";
import * as ts from "ts-morph";
import path from 'path'
import { visitNodes } from "typescript";

export function delint(sourceFile: ts.SourceFile) {
    delintNode(sourceFile);

    function delintNode(node: ts.Node) {
        /*
          InterfaceDeclaration
          ClassDeclaration
          FunctionDeclaration
          CallExpression
         */
        // switch-case for generating report
        switch (node.getKind()) {
            case ts.SyntaxKind.SourceFile:
                // report(node, '' + ts.SyntaxKind[node.getKind()]);
                break;
            case ts.SyntaxKind.InterfaceDeclaration:
                // report(node, '' + ts.SyntaxKind[node.getKind()]);
                var interface_node = node as ts.InterfaceDeclaration;
                // interface_node.name
                break;
            case ts.SyntaxKind.ClassDeclaration:
                // report(node, '' + ts.SyntaxKind[node.getKind()]);
                break;
            case ts.SyntaxKind.FunctionDeclaration:
                // report(node, '' + ts.SyntaxKind[node.getKind()]);
                break;
            case ts.SyntaxKind.CallExpression:
                report(node, '' + ts.SyntaxKind[node.getKind()]);
                var call_identifier = node.getFirstChildByKind(ts.ts.SyntaxKind.Identifier);
                var definitions = call_identifier?.getDefinitions() || [];
                if(definitions.length > 0){
                    var def = definitions[0]
                    console.log(def.getDeclarationNode()?.getStartLineNumber())
                }
                console.log('-------------------------------------------------------------------------------------')

                //   var callExpr = node as ts.CallExpression;
                break;
            default:
                //   report(node, '' + ts.SyntaxKind[node.getKind()]);
                break;
        }
        // report(node, '' + ts.SyntaxKind[node.getKind()]);
        // Switch-case for visiting child nodes.
        switch (node.getKind()) {
            case ts.SyntaxKind.FunctionDeclaration:
                node.forEachChild(delintNode);
                break;
            default:
                node.forEachChild(delintNode);
                break;
        }
    }

    function report(node: ts.Node, message: string) {
        const { line, character } = sourceFile.compilerNode.getLineAndCharacterOfPosition(node.getStart());
        console.log(`${sourceFile.compilerNode.fileName} (${line + 1},${character + 1}): ${message}`);
    }
}

export function getAST() {
    // initialize
    var projectPath = path.resolve('temp/project1/**/*.ts');
    var pytutorPath = path.resolve('temp/project1/pytutor.ts');
    const project = new Project({
        // Optionally specify compiler options, tsconfig.json, in-memory file system, and more here.
        // If you initialize with a tsconfig.json, then it will automatically populate the project
        // with the associated source files.
        // Read more: https://ts-morph.com/setup/
    });

    // add source files
    project.addSourceFilesAtPaths(projectPath);
    var pytutorSourceFile = project.getSourceFile(pytutorPath)!;
    // console.log(pytutorSourceFile)
    // console.log(pytutorSourceFile?.getFullText())
    // console.log(__dirname)
    // console.log(readFileSync(pytutorPath))
    // console.log(pytutorPath)
    // console.log(projectPath)
    delint(pytutorSourceFile);
}