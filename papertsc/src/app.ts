// import { getAST } from './APISample_linter'
import { getAST } from './visitor'
import path from 'path'
import { postProcess } from './postprocess'
import { readFileSync, writeFileSync } from "fs";
const prism = require('prismjs')
const commander = require('commander');

function run() {
    commander
        .option('-p, --project <type>', 'project path')
        .option('-f, --file <type>', 'tsc file path')
        .option('-o, --out <type>', 'output file path');

    commander.parse(process.argv);

    if (!commander.project || !commander.file || !commander.out) {
        console.log('Not all the arguments are parsed.');
        return
    }

    // node dist/app.js -p test/project1/**/*.ts -f test/project1/pytutor.ts -o test/pyt.json
    // var projectPath = path.resolve('test/project1/**/*.ts');
    // var pytutorPath = path.resolve('test/project1/pytutor.ts');
    // var json_path = path.resolve('test/pyt.json');

    var projectPath = path.resolve(commander.project);
    var pytutorPath = path.resolve(commander.file);
    var json_path = path.resolve(commander.out);

    var ast_root = getAST(projectPath, pytutorPath)
    postProcess(ast_root);
    var root_json = ast_root.toJSON();
    writeFileSync(json_path, JSON.stringify(root_json));
    // var code = readFileSync(pytutorPath).toString();
    // console.log(prism.highlight(code, prism.languages.typescript, 'typescript'));

    // console.log(JSON.stringify(ast_root));
}

run()