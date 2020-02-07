import { readFileSync } from "fs";
import * as ts from "typescript";

export function delint(sourceFile: ts.SourceFile) {
  delintNode(sourceFile);

  function delintNode(node: ts.Node) {
    // switch (node.kind) {
    //   case ts.SyntaxKind.FunctionDeclaration:
    //     // If parent node is a function, skip it!
    //     report(node, '' + node.kind + ' at line ' + sourceFile.getLineAndCharacterOfPosition(node.getStart()).line)
    //     break;
    //   case ts.SyntaxKind.ForStatement:
    //   case ts.SyntaxKind.ForInStatement:
    //   case ts.SyntaxKind.WhileStatement:
    //   case ts.SyntaxKind.DoStatement:
    //     if ((node as ts.IterationStatement).statement.kind !== ts.SyntaxKind.Block) {
    //       report(
    //         node,
    //         'A looping statement\'s contents should be wrapped in a block body.'
    //       );
    //     }
    //     break;

    //   case ts.SyntaxKind.IfStatement:
    //     const ifStatement = node as ts.IfStatement;
    //     if (ifStatement.thenStatement.kind !== ts.SyntaxKind.Block) {
    //       report(ifStatement.thenStatement, 'An if statement\'s contents should be wrapped in a block body.');
    //     }
    //     if (
    //       ifStatement.elseStatement &&
    //       ifStatement.elseStatement.kind !== ts.SyntaxKind.Block &&
    //       ifStatement.elseStatement.kind !== ts.SyntaxKind.IfStatement
    //     ) {
    //       report(
    //         ifStatement.elseStatement,
    //         'An else statement\'s contents should be wrapped in a block body.'
    //       );
    //     }
    //     break;

    //   case ts.SyntaxKind.BinaryExpression:
    //     const op = (node as ts.BinaryExpression).operatorToken.kind;
    //     if (op === ts.SyntaxKind.EqualsEqualsToken || op === ts.SyntaxKind.ExclamationEqualsToken) {
    //       report(node, 'Use \'===\' and \'!==\'.');
    //     }
    //     break;
    // }
    
    // switch-case for generating report
    // switch(node.kind){
    //   case ts.SyntaxKind.SourceFile:
    //     report(node, '' + ts.SyntaxKind[node.kind] + ' at line ' + sourceFile.getLineAndCharacterOfPosition(node.getStart()).line)
    //     break;
    //   default:
    //     report(node, '' + ts.SyntaxKind[node.kind] + ' at line ' + sourceFile.getLineAndCharacterOfPosition(node.getStart()).line)
    //     break;
    // }
    report(node, '' + ts.SyntaxKind[node.kind])
    if(ts.isFunctionDeclaration(node)){
      var func_node = node as ts.FunctionDeclaration
    }
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
    // Parsing a file
    const sourceFile = ts.createSourceFile(
        filePath,
        readFileSync(filePath).toString(),
        ts.ScriptTarget.ES2015,
        /*setParentNodes */ true
      );
    
      // delint it
      delint(sourceFile);
}