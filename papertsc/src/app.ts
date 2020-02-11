// import { getAST } from './APISample_linter'
import {getAST} from './visitor'
import path from 'path'
import {postProcess} from './postprocess'
import { readFileSync, writeFileSync } from "fs";
const prism = require('prismjs')

var projectPath = path.resolve('temp/project1/**/*.ts');
var pytutorPath = path.resolve('temp/project1/pytutor.ts');
var json_path = 'D:/PV/Research/PaperCode/papertsc/temp/pyt.json';
var ast_root = getAST(projectPath, pytutorPath)
postProcess(ast_root);
var root_json = ast_root.toJSON();
writeFileSync(json_path, JSON.stringify(root_json));
// var code = readFileSync(pytutorPath).toString();
// console.log(prism.highlight(code, prism.languages.typescript, 'typescript'));

// console.log(JSON.stringify(ast_root));