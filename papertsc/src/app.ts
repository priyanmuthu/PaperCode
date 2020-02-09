// import { getAST } from './APISample_linter'
import {getAST} from './visitor'
import path from 'path'
// getAST('./src/APISample_linter.ts')
// getAST('./test/test1.ts')
// console.log(process.cwd())
var projectPath = path.resolve('temp/project1/**/*.ts');
var pytutorPath = path.resolve('temp/project1/pytutor.ts');
getAST(projectPath, pytutorPath)