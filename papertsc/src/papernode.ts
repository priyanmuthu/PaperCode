import { Node as tsNode } from "ts-morph";

export class Position {
    line: number;
    column: number;

    constructor(line: number, column: number) {
        this.line = line;
        this.column = column;
    }
}

export enum NodeKind {
    Node = 0,
    Class,
    Interface,
    Function,
    Call
}

export class PaperNode {

    public compiler_node: tsNode;
    public kind: NodeKind;
    public parent?: PaperNode;
    public start_pos: Position;
    public end_pos: Position;
    public children: PaperNode[];

    constructor(compiler_node: tsNode, startPos: Position, endPos: Position, parent?: PaperNode) {
        this.kind = NodeKind.Node;
        this.compiler_node = compiler_node;
        this.parent = parent;
        this.start_pos = startPos;
        this.end_pos = endPos;
        this.children = [];
    }

    public getChildren() {
        return this.children;
    }

    public addChildren(childNode: PaperNode) {
        this.children.push(childNode);
    }
}

export class InterfaceNode extends PaperNode {

    public name: string;

    constructor(compiler_node: tsNode, parent: PaperNode, name: string, startPos: Position, endPos: Position) {
        super(compiler_node, startPos, endPos, parent)
        this.kind = NodeKind.Interface;
        this.name = name;
    }
}

export class ClassNode extends PaperNode {

    public name: string;
    public body_start_pos: Position;
    public body_end_position: Position;

    constructor(compiler_node: tsNode, parent: PaperNode, name: string, startPos: Position, endPos: Position, body_start_pos: Position, body_end_position: Position) {
        super(compiler_node, startPos, endPos, parent)
        this.kind = NodeKind.Class;
        this.name = name;
        this.body_start_pos = body_start_pos;
        this.body_end_position = body_end_position;
    }
}

export class FunctionNode extends PaperNode {

    public name: string;
    public body_start_pos: Position;
    public body_end_position: Position;
    public size: number;
    public function_calls: CallNode[]
    public refs: PaperNode[]

    constructor(compiler_node: tsNode, parent: PaperNode, name: string, startPos: Position, endPos: Position, body_start_pos: Position, body_end_position: Position) {
        super(compiler_node, startPos, endPos, parent)
        this.kind = NodeKind.Function;
        this.name = name;
        this.body_start_pos = body_start_pos;
        this.body_end_position = body_end_position;
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
}

export class CallNode extends PaperNode {

    public func?: FunctionNode;

    constructor(compiler_node: tsNode, parent: PaperNode, startPos: Position, endPos: Position) {
        super(compiler_node, startPos, endPos, parent)
        this.kind = NodeKind.Call;
    }
}