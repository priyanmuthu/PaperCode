import { readFileSync } from "fs";
import * as ts from "typescript";

export function delint(sourceFile: ts.SourceFile, program: ts.Program) {
  delintNode(sourceFile);

  function delintNode(node: ts.Node) {
    /*
      InterfaceDeclaration
      ClassDeclaration
      FunctionDeclaration
      CallExpression
     */
    var typeChecker = program.getTypeChecker();
    // switch-case for generating report
    switch(node.kind){
      case ts.SyntaxKind.SourceFile:
        // report(node, '' + ts.SyntaxKind[node.kind]);
        break;
      case ts.SyntaxKind.InterfaceDeclaration:
        // report(node, '' + ts.SyntaxKind[node.kind]);
        var interface_node = node as ts.InterfaceDeclaration;
        // interface_node.name
        break;
      case ts.SyntaxKind.ClassDeclaration:
        // report(node, '' + ts.SyntaxKind[node.kind]);
        break;
      case ts.SyntaxKind.FunctionDeclaration:
        // report(node, '' + ts.SyntaxKind[node.kind]);
        break;
      case ts.SyntaxKind.CallExpression:
        report(node, '' + ts.SyntaxKind[node.kind]);
        var callExpr = node as ts.CallExpression;
        try{
          var signature = typeChecker.getResolvedSignature(callExpr)
          console.log(signature?.declaration)
        }
        catch(error){
          console.log(error)
        }
        console.log('------------------------------------------------------------')
        break;
      default:
        // report(node, '' + ts.SyntaxKind[node.kind]);
        break;
    }
    // report(node, '' + ts.SyntaxKind[node.kind]);
    // Switch-case for visiting child nodes.
    switch(node.kind){
      case ts.SyntaxKind.FunctionDeclaration:
        ts.forEachChild(node, delintNode);
        break;
      default:
        ts.forEachChild(node, delintNode);
        break;
    }
  }

  function report(node: ts.Node, message: string) {
    const { line, character } = sourceFile.getLineAndCharacterOfPosition(node.getStart());
    console.log(`${sourceFile.fileName} (${line + 1},${character + 1}): ${message}`);
  }
}

export function getAST(filePath: string){
  var options = {
    target: ts.ScriptTarget.ES5,
    module: ts.ModuleKind.CommonJS
  }
  // Parsing a file
  const sourceFile = ts.createSourceFile(
      filePath,
      readFileSync(filePath).toString(),
      ts.ScriptTarget.ES2015,
      /*setParentNodes */ true
    );
  
  var files = [filePath]
  var programOptions = {rootNames: files, options: options}
  var program = ts.createProgram(programOptions)
  // var typeChecker = program.getTypeChecker()
  // typeChecker.getResolvedSignature
  // ts.getPreEmitDiagnostics(program)
  // delint it
  delint(sourceFile, program);
}