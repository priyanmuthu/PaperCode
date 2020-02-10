import { Node as tsNode, SyntaxKind } from "ts-morph";
import { fstat } from "fs";
const uuidv4 = require('uuid/v4');
import { Serializable, JsonProperty, serialize } from 'typescript-json-serializer';

@Serializable()
export class Position {
    @JsonProperty()
    line: number;

    @JsonProperty()
    column: number;

    constructor(line: number, column: number) {
        this.line = line;
        this.column = column;
    }

    public toJSON() {
        var jsonObj: any = {};
        jsonObj['line'] = this.line;
        jsonObj['column'] = this.column;
        return jsonObj;
    }
}

export enum NodeKind {
    Node = 0,
    Class,
    Interface,
    Function,
    Call
}

// Helperfunctions
function nodeArrayToUIDs(nodes: PaperNode[]): Array<string> {
    var uids: string[] = [];
    nodes.forEach(n => { uids.push(n.uid); });
    return uids;
}

function nodeToUID(node: PaperNode): string {
    return node.uid || '';
}

function deepSerialize(node: PaperNode) {
    switch (node.kind) {
        case NodeKind.Node:
            return serialize(node);
        case NodeKind.Interface:
            var iNode = node as InterfaceNode;
            return serialize(iNode);
        case NodeKind.Class:
            var cNode = node as ClassNode;
            return serialize(cNode);
        case NodeKind.Function:
            var fNode = node as FunctionNode;
            return serialize(fNode);
        case NodeKind.Call:
            var callNode = node as CallNode;
            return serialize(callNode);
    }
}

function deepSerializeArray(nodes: PaperNode[]) {
    var res_arr: any = [];
    nodes.forEach(n => { res_arr.push(deepSerialize(n)); });
    return res_arr;
}

@Serializable()
export class PaperNode {

    public compiler_node: tsNode;

    @JsonProperty()
    public kind: NodeKind;

    public parent?: PaperNode;

    @JsonProperty()
    public parentuid: string;

    @JsonProperty({ onSerialize: deepSerialize })
    public start_pos: Position;

    @JsonProperty({ onSerialize: deepSerialize })
    public end_pos: Position;

    @JsonProperty({ onSerialize: deepSerializeArray })
    public children: PaperNode[];

    @JsonProperty()
    public uid: string;

    constructor(compiler_node: tsNode, startPos: Position, endPos: Position, parent?: PaperNode) {
        this.kind = NodeKind.Node;
        this.compiler_node = compiler_node;
        this.parent = parent;
        this.parentuid = parent?.uid || '';
        this.start_pos = startPos;
        this.end_pos = endPos;
        this.children = [];
        this.uid = uuidv4();
    }

    public getChildren() {
        return this.children;
    }

    public addChildren(childNode: PaperNode) {
        this.children.push(childNode);
    }

    public ToString(tabspace: string = '') {
        return tabspace + `Other Node: ${SyntaxKind[this.compiler_node.getKind()]} @ (${this.start_pos.line}, ${this.start_pos.column}) - (${this.end_pos.line}, ${this.end_pos.column})`;
    }

    public toJSON() {
        var jsonObj: any = {}
        jsonObj['uid'] = this.uid;
        jsonObj['kind'] = this.kind;
        jsonObj['parentuid'] = this.parentuid;
        jsonObj['start_pos'] = this.start_pos.toJSON();
        jsonObj['end_pos'] = this.end_pos.toJSON();
        var children_arr: any[] = [];
        this.children.forEach(child => {
            children_arr.push(child.toJSON());
        });
        jsonObj['children'] = children_arr;

        return jsonObj;
    }
}

@Serializable('PaperNode')
export class InterfaceNode extends PaperNode {

    @JsonProperty()
    public name: string;

    constructor(compiler_node: tsNode, parent: PaperNode, name: string, startPos: Position, endPos: Position) {
        super(compiler_node, startPos, endPos, parent)
        this.kind = NodeKind.Interface;
        this.name = name;
    }

    public ToString(tabspace: string = '') {
        return tabspace + `Interface: ${this.name} @ (${this.start_pos.line}, ${this.start_pos.column}) - (${this.end_pos.line}, ${this.end_pos.column})`;
    }

    public toJSON() {
        var jsonObj = super.toJSON();
        jsonObj['name'] = this.name;
        return jsonObj;
    }
}

@Serializable('PaperNode')
export class ClassNode extends PaperNode {

    @JsonProperty()
    public name: string;

    @JsonProperty({ onSerialize: deepSerialize })
    public body_start_pos: Position;

    @JsonProperty({ onSerialize: deepSerialize })
    public body_end_pos: Position;

    constructor(compiler_node: tsNode, parent: PaperNode, name: string, startPos: Position, endPos: Position, body_start_pos: Position, body_end_pos: Position) {
        super(compiler_node, startPos, endPos, parent)
        this.kind = NodeKind.Class;
        this.name = name;
        this.body_start_pos = body_start_pos;
        this.body_end_pos = body_end_pos;
    }

    public ToString(tabspace: string = '') {
        return tabspace + `Class: ${this.name} @ (${this.start_pos.line}, ${this.start_pos.column}) - (${this.end_pos.line}, ${this.end_pos.column})`;
    }

    public toJSON() {
        var jsonObj = super.toJSON();
        jsonObj['name'] = this.name;
        jsonObj['bosy_start_pos'] = this.body_start_pos.toJSON();
        jsonObj['body_end_pos'] = this.body_end_pos.toJSON();
        return jsonObj;
    }
}


@Serializable('PaperNode')
export class CallNode extends PaperNode {

    @JsonProperty({ onSerialize: deepSerialize })
    public func?: PaperNode;

    constructor(compiler_node: tsNode, parent: PaperNode, startPos: Position, endPos: Position) {
        super(compiler_node, startPos, endPos, parent)
        this.kind = NodeKind.Call;
    }

    public ToString(tabspace: string = '') {
        return tabspace + `Call Expression @ (${this.start_pos.line}, ${this.start_pos.column}) - (${this.end_pos.line}, ${this.end_pos.column})`;
    }

    public toJSON() {
        var jsonObj = super.toJSON();
        jsonObj['func'] = this.func?.uid || '';
        return jsonObj;
    }
}

@Serializable('PaperNode')
export class FunctionNode extends PaperNode {

    @JsonProperty()
    public name: string;

    @JsonProperty({ onSerialize: deepSerialize })
    public body_start_pos: Position;

    @JsonProperty({ onSerialize: deepSerialize })
    public body_end_pos: Position;

    public size: number;

    @JsonProperty({ onSerialize: deepSerializeArray })
    public function_calls: CallNode[];

    @JsonProperty({ onSerialize: nodeArrayToUIDs })
    public refs: CallNode[];

    constructor(compiler_node: tsNode, parent: PaperNode, name: string, startPos: Position, endPos: Position, body_start_pos: Position, body_end_pos: Position) {
        super(compiler_node, startPos, endPos, parent)
        this.kind = NodeKind.Function;
        this.name = name;
        this.body_start_pos = body_start_pos;
        this.body_end_pos = body_end_pos;
        this.size = this.end_pos.line - this.start_pos.line + 1;
        this.function_calls = []
        this.refs = []
    }

    public addFunctionCall(fCall: CallNode) {
        this.function_calls.push(fCall);
    }

    public addFunctionCallArray(fCalls: CallNode[]) {
        this.function_calls.push(...fCalls);
    }

    public addReference(ref: CallNode) {
        this.refs.push(ref);
    }

    public ToString(tabspace: string = '') {
        var fString = [`Function: ${this.name} @ (${this.start_pos.line}, ${this.start_pos.column}) - (${this.end_pos.line}, ${this.end_pos.column})`];
        this.function_calls.forEach(fc => {
            fString.push(tabspace + '\t' + fc.ToString())
        });
        return tabspace + fString.join('\n');
    }

    public toJSON() {
        var jsonObj = super.toJSON();
        jsonObj['name'] = this.name;
        jsonObj['bosy_start_pos'] = this.body_start_pos.toJSON();
        jsonObj['body_end_pos'] = this.body_end_pos.toJSON();
        var func_calls: any[] = [];
        this.function_calls.forEach(fc => {
            if (fc.func === undefined || fc.func === null) { return; }
            func_calls.push(fc.toJSON());
        });
        jsonObj['function_calls'] = func_calls;
        var refs_arr: string[] = [];
        this.refs.forEach(r => {
            refs_arr.push(r.uid);
        });
        jsonObj['refs'] = refs_arr;
        return jsonObj;
    }
}