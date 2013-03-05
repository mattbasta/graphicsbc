var gbc = (function() {

    'use strict';

    var operations = {};

    var return_true = function() {return true;};
    var return_false = function() {return false;};

    function _in(haystack, needle) {
        if (typeof haystack === "string") {
            return haystack.indexOf(needle) > -1;
        }
        for (var k in haystack)
            if (haystack[k] === needle)
                return true;
        return false;
    }

    function expect_continuation(self, len) {
        return function(closure) {
            return function() {
                if (!this.body)
                    throw new Error("Tuple not passed to prefix statement");
                if (!(this.body instanceof Continuation))
                    throw new Error("Expected tuple, got non-tuple");

                if (len) {
                    if (typeof len !== "object")
                        len = [len];
                    var length = this.body.value.length;
                    if (!_in(len, length))
                        throw new Error("Tuple of invalid length (" + len + " got " + length + ")");
                }

                return closure.apply(this, arguments);
            };
        };
    }

    function literal(value) {
        var out;
        if (_in(value, "."))
            out = parseFloat(value);
        else
            out = parseInt(value, 10);
        out = new Number(out);
        out.run = function() {return this;};
        out.compile = out.toString;
        console.log(value, out);
        return out;
    }

    function Operation() {
        this.toString = function() {
            return "<Operation>";
        };
    }
    function Statement() {
        this.has_return_value = return_false;
        this.toString = function() {
            return "<" + this.name + ">";
        };
    }
    Statement.prototype = new Operation;

    function Expression() {
        this.has_return_value = return_true;
        this.value = null;
    }
    Expression.prototype = new Operation;

    function PrefixOperation() {
        this.name = "Unknown";
        this.body = null;
        this.push = function(node) {this.body = node;};
    }
    PrefixOperation.prototype = new Statement;

    function PrefixStatement() {
        PrefixOperation.apply(this, arguments);
        this.toString = function() {
            return "Statement(" + this.name + ")>" + this.body;
        };
    }
    PrefixStatement.prototype = new PrefixOperation;

    function PrefixExpression() {
        PrefixOperation.apply(this, arguments);
        this.toString = function() {
            return "Expression(" + this.name + ")>" + this.body;
        };
    }
    PrefixExpression.prototype = new PrefixOperation;

    (operations["n"] = function() {
        this.name = "Negate";
        this.run = function(context) {
            return this.body.run(context) * -1;
        };
        this.compile = function() {
            return '(-1 * ' + this.body.compile() + ')';
        };
    }).prototype = new PrefixExpression;

    (operations["N"] = function() {
        this.name = "Not";
        this.run = function(context) {
            return !this.body.run(context);
        };
        this.compile = function() {
            return '(!' + this.body.compile() + ')';
        };
    }).prototype = new PrefixExpression;

    (operations["&"] = function() {
        this.name = "And";
        this.run = expect_continuation(this, 2)(function(context) {
            var left = this.body.value[0];
            var right = this.body.value[1];
            return left.run(context) == 0 ? 0 : right.run(context);
        });
        this.compile = function() {
            return '(' + this.body.value[0].compile() + ' && ' + this.body.value[1].compile() + ')';
        };
    }).prototype = new PrefixExpression;

    (operations["|"] = function() {
        this.name = "Or";
        this.run = expect_continuation(this, 2)(function(context) {
            var left = this.body.value[0].run(context);
            var right = this.body.value[1];
            return left != 0 ? left : right.run(context);
        });
        this.compile = function() {
            return '(' + this.body.value[0].compile() + ' || ' + this.body.value[1].compile() + ')';
        };
    }).prototype = new PrefixExpression;

    (operations["I"] = function() {
        this.name = "Iff";
        this.run = expect_continuation(this, 3)(function(context) {
            var condition = this.body.value[0];
            var left = this.body.value[1];
            var right = this.body.value[2];
            return condition.run(context) ? left.run(context) : right.run(context);
        });
        this.compile = function() {
            return '(' + this.body.value[0].compile() + ' ? ' + this.body.value[1].compile() + ' : ' + this.body.value[2].compile() + ')';
        };
    }).prototype = new PrefixExpression;

    (operations["X"] = function() {
        this.name = "XOR";
        this.run = expect_continuation(this, 2)(function(context) {
            var left = this.body.value[0].run(context);
            var right = this.body.value[1].run(context);
            return !!(left) !== !!(right);
        });
        this.compile = function() {
            return '(!!' + this.body.value[0].compile() + ' !== !!' + this.body.value[1].compile() + ')';
        };
    }).prototype = new PrefixExpression;

    var SinOperation = operations["s"] = function() {
        PrefixExpression.apply(this, arguments);
        this.name = "Sin";
        this.run = function(context) {
            return Math.sin(this.body.run(context));
        };
        this.compile = function() {
            return 'Math.sin(' + this.body.compile() + ')';
        };
    };
    SinOperation.prototype = new PrefixExpression;

    var CosOperation = operations["o"] = function() {
        PrefixExpression.apply(this, arguments);
        this.name = "Cos";
        this.run = function(context) {
            return Math.cos(this.body.run(context));
        };
        this.compile = function() {
            return 'Math.cos(' + this.body.compile() + ')';
        };
    };
    CosOperation.prototype = new PrefixExpression;

    var TanOperation = operations["T"] = function() {
        PrefixExpression.apply(this, arguments);
        this.name = "Tan";
        this.run = function(context) {
            return Math.tan(this.body.run(context));
        };
        this.compile = function() {
            return 'Math.tan(' + this.body.compile() + ')';
        };
    };
    TanOperation.prototype = new PrefixExpression;

    var SecOperation = operations["E"] = function() {
        PrefixExpression.apply(this, arguments);
        this.name = "Sec";
        this.run = function(context) {
            return 1 / Math.cos(this.body.run(context));
        };
        this.compile = function() {
            return '(1 / Math.cos(' + this.body.compile() + '))';
        };
    };
    SecOperation.prototype = new PrefixExpression;

    var CscOperation = operations["O"] = function() {
        PrefixExpression.apply(this, arguments);
        this.name = "Csc";
        this.run = function(context) {
            return 1 / Math.sin(this.body.run(context));
        };
        this.compile = function() {
            return '(1 / Math.sin(' + this.body.compile() + '))';
        };
    };
    CscOperation.prototype = new PrefixExpression;

    var CotOperation = operations["Y"] = function() {
        PrefixExpression.apply(this, arguments);
        this.name = "Cot";
        this.run = function(context) {
            return 1 / Math.tan(this.body.run(context));
        };
        this.compile = function() {
            return '(1 / Math.tan(' + this.body.compile() + '))';
        };
    };
    CotOperation.prototype = new PrefixExpression;

    (operations["!"] = function() {
        PrefixExpression.apply(this, arguments);
        this.name = "Inv";
        this.run = function(context) {
            if (this.body instanceof SinOperation)
                return Math.asin(this.body.body.run(context));
            else if (this.body instanceof CosOperation)
                return Math.acos(this.body.body.run(context));
            else if (this.body instanceof TanOperation)
                return Math.atan(this.body.body.run(context));
            else if (this.body instanceof SecOperation)
                return Math.acos(1 / this.body.body.run(context));
            else if (this.body instanceof CscOperation)
                return Math.asin(1 / this.body.body.run(context));
            else if (this.body instanceof CotOperation)
                return Math.atan(1 / this.body.body.run(context));
            else
                throw new Error("Unsupported inversion operation.");
        };
        this.compile = function(context) {
            if (this.body instanceof SinOperation)
                return 'Math.asin(' + this.body.body.compile() + ')';
            else if (this.body instanceof CosOperation)
                return 'Math.acos(' + this.body.body.compile() + ')';
            else if (this.body instanceof TanOperation)
                return 'Math.atan(' + this.body.body.compile() + ')';
            else if (this.body instanceof SecOperation)
                return 'Math.acos(1 / ' + this.body.body.compile() + ')';
            else if (this.body instanceof CscOperation)
                return 'Math.asin(1 / ' + this.body.body.compile() + ')';
            else if (this.body instanceof CotOperation)
                return 'Math.atan(1 / ' + this.body.body.compile() + ')';
            else
                throw new Error("Unsupported inversion operation.");
        };
    }).prototype = new PrefixExpression;

    (operations["_"] = function() {
        this.name = "Floor";
        this.run = function(context) {
            return this.body.run(context) | 0;
        };
        this.compile = function() {
            return 'Math.floor(' + this.body.compile() + ')';
        };
    }).prototype = new PrefixExpression;

    (operations["`"] = function() {
        this.name = "Ceil";
        this.run = function(context) {
            return this.body.run(context) | 0 + 1;
        };
        this.compile = function() {
            return 'Math.ceil(' + this.body.compile() + ')';
        };
    }).prototype = new PrefixExpression;

    (operations["\""] = function() {
        this.name = "Square";
        this.run = function(context) {
            return Math.pow(this.body.run(context), 2);
        };
        this.compile = function() {
            return 'Math.pow(' + this.body.compile() + ', 2)';
        };
    }).prototype = new PrefixExpression;

    (operations["\\"] = function() {
        this.name = "SqRt";
        this.run = function(context) {
            return Math.sqrt(this.body.run(context));
        };
        this.compile = function() {
            return 'Math.sqrt(' + this.body.compile() + ')';
        };
    }).prototype = new PrefixExpression;

    (operations["a"] = function() {
        this.name = "Assignment";
        this.run = function(context) {
            var out = this.body.run(context);
            if (out instanceof Array) {
                context.vars[out[0]] = out[1];
                return out[1];
            }

            if (out in context.vars) {
                return context.vars[out];
            }
            return 0;
        };
        this.compile = function() {
            if (this.body instanceof Continuation) {
                return '(context[' + this.body.value[0].compile() + '] = ' + this.body.value[1].compile() + ')';
            } else {
                return 'context[' + this.body.compile() + ']';
            }
        };
    }).prototype = new PrefixExpression;

    (operations["q"] = function() {
        this.name = "Call";
        this.run = function(context) {
            var out = this.body.run(context);
            var func = out, args = [];
            if (out instanceof Array) {
                func = out[0];
                args = out.slice(1);
            }

            if (!(func in context.funcs))
                throw new Error("Function " + func + " not yet defined.");

            var i;
            for (i = 0; i < args.length; i++)
                context.vars[-(i + 1)] = args[i];

            out = 0;
            var _func = context.funcs[func];
            for (i = 0; i < _func.body.length; i++)
                out = _func.body[i].run(context);
            
            if (!out)
                out = 0;

            return out;
        };
        this.compile = function() {
            var out = '(function() {';
            out += 'var func = ' + this.body.value[0].compile() + ';';
            out += 'if (!(func in functions)) {';
            out += 'throw new Error("Function " + func + " not yet defined");';
            out += '}';
            out += 'for (var i = 0; i < arguments.length; i++) {';
            out += 'context[~i] = arguments[i];';
            out += '}';
            out += 'functions[func]();';
            out += '})(';
            out += this.body.value.slice(1).map(function(n) {return n.compile();}).join(', ');
            out += ')';
            return out;
            if (this.body.value[1]) {
                return '(context[' + this.body.value[0].compile() + '] = ' + this.body.value[1].compile() + ')';
            } else {
                return 'context[' + this.body.value[0].compile() + ']';
            }
        };
    }).prototype = new PrefixExpression;

    function BlockOperation() {
        this.body = null;
        this.name = "";
        this.push = function(operation) {this.body.push(operation);};
        this.run = function(context) {
            for (var i in this.body)
                this.body[i].run(context);
        };
        this.compile = function() {
            return this.body.map(function(n) {return n.compile() + ';';}).join('\n');
        };
        this.toString = function() {
            var output = [];
            for (var k in this.body)
                output.push(this.body[k].toString());
            return "block(" + this.name + "){" + output.join(", ") + "}";
        };
    }
    BlockOperation.prototype = new Operation;

    function BlockExpression() {
        this.name = "..";
        this.body = null;
        this.push = function(node) {this.body = node;};
        this.run = function(context) {
            if (this.body)
                return this.body.run(context);
            return 0;
        };
        this.compile = function() {
            if (this.body)
                return this.body.compile();
            return '0';
        };
        this.toString = function() {
            return "block(" + this.name + ")<<{" + this.body.toString() + "}";
        };
    }
    BlockExpression.prototype = new Expression;

    function FirstExprBlockOperation() {
        this.first = null;
        this.push = function(operation) {
            if (!this.first)
                this.first = operation;
            else
                this.body.push(operation);
        };
        this.toString = function() {
            var output = [];
            for (var k in this.body)
                output.push(this.body[k].toString());
            return "block(" + this.name + ")<" + this.first + ">{" + output.join(",") + "}";
        };
    }
    FirstExprBlockOperation.prototype = new BlockOperation;

    (operations["L"] = function() {
        this.body = [];
        this.name = "Loop";
        this.run = function(context) {
            var count = this.first.run(context);
            if (count < 0)
                throw new Error("Cannot loop less than 0 times.");
            for (var i = 0; i < count; i++)
                for (var j in this.body)
                    this.body[j].run(context);
        };
        this.compile = function() {
            return '(function() {' +
                   'for(var i = 0; i < ' + this.first.compile() + '; i++) {' +
                   this.body.map(function(n) {return n.compile();}).join(';\n') + ';\n' +
                   '}' +
                   '})()';
        };
    }).prototype = new FirstExprBlockOperation;

    (operations["i"] = function() {
        this.body = [];
        this.name = "Conditional";
        this.run = function(context) {
            if (this.first.run(context))
                for (var j in this.body)
                    this.body[j].run(context);
        };
        this.compile = function() {
            return 'if(' + this.first.compile() + ') {' +
                   this.body.map(function(n) {return n.compile();}).join(';\n') + ';\n' +
                   '}';
        };
    }).prototype = new FirstExprBlockOperation;

    function ExecutableOperation() {
        this.body = [];
        this.name = "Executable Block";
        this.execute = function(context) {
            for (var i in this.body)
                this.body[i].run(context);
        };
    }
    ExecutableOperation.prototype = new BlockOperation;

    (operations["{"] = function() {
        this.body = [];
        ExecutableOperation.apply(this, arguments);
        this.name = "Function";
        this.run = function(context) {
            context.funcs[this.first.run(context)] = this;
        };
        this.compile = function() {
            var id = this.first.compile();
            var out = '(id = ' + id + ', functions[id] = function() {';
            out += this.body.map(function(n) {return n.compile()}).join(';\n') + ';\n';
            out += '}, id)';
            return out;
        };
    }).prototype = new FirstExprBlockOperation;

    (operations["T"] = function() {
        this.body = [];
        this.name = "Any";
        this.run = function(context) {
            for (var i in this.body) {
                var out = this.body[i].run(context);
                if (out)
                    return out;
            }
            return 0;
        };
        this.compile = function() {
            return '(' + this.body.map(function(n) {return n.compile()}).join(' || ') + ')';
        };
    }).prototype = new BlockOperation;

    (operations["A"] = function() {
        this.body = [];
        this.name = "All";
        this.run = function(context) {
            for (var i = 0; i < this.body.length; i++)
                if (!this.body[i].run(context))
                    return 0;
            return 1;
        };
        this.compile = function() {
            return '(' + this.body.map(function(n) {return n.compile()}).join(' && ') + ')';
        };
    }).prototype = new BlockOperation;

    (operations["U"] = function() {
        this.body = [];
        this.name = "Sum";
        this.run = function(context) {
            var out = 0;
            for (var i in this.body) {
                var item = this.body[i].run(context);
                if (item instanceof Number)
                    out += item;
            }
            return out;
        };
        this.compile = function() {
            return '[' + this.body.map(function(n) {return n.compile()}).join(', ') + '].reduce(function(p, c) {return p + c;}, 0)';
        };
    }).prototype = new BlockOperation;

    (operations[";"] = function() {
        this.name = "Break";
        this.run = function() {
            throw new Error("FIXME: Not implemented");
        };
        this.compile = function() {
            return 'break';
        };
    }).prototype = new Statement;

    (operations["#"] = function() {
        this.name = "ClearMat";
        this.run = function(context) {
            context.canvas.clear_transforms();
        };
        this.compile = function() {
            return 'canvas.clear()';
        };
    }).prototype = new Statement;

    (operations["<"] = function() {
        this.name = "PopMat";
        this.run = function(context) {
            context.canvas.pop();
        };
        this.compile = function() {
            return 'canvas.pop()';
        };
    }).prototype = new Statement;

    (operations["d"] = function() {
        this.name = "Dot";
        this.run = function(context) {
            context.canvas.dot();
        };
        this.compile = function() {
            return 'canvas.dot()';
        };
    }).prototype = new Statement;

    (operations["P"] = function() {
        this.name = "Line";
        this.run = function(context) {
            context.canvas.line();
        };
        this.compile = function() {
            return 'canvas.line()';
        };
    }).prototype = new Statement;

    (operations["C"] = function() {
        this.name = "RGBA";
        this.run = expect_continuation(this, [3, 4])(function(context) {
            var body = this.body.run(context);
            if (body.length === 3)
                body.push(1);
            body[0] = body[0]|0;
            body[1] = body[1]|0;
            body[2] = body[2]|0;
            context.canvas.set_color(body);
        });
        this.compile = function() {
            if (this.body.value.length === 3)
                return 'canvas.set_color([' + this.body.value[0].compile() + '|0, ' + this.body.value[1].compile() + '|0, ' + this.body.value[2].compile() + '|0, 1])';
            else
                return 'canvas.set_color([' + this.body.value[0].compile() + '|0, ' + this.body.value[1].compile() + '|0, ' + this.body.value[2].compile() + '|0, ' + this.body.value[3].compile() + '])';
        };
    }).prototype = new PrefixStatement;

    (operations["H"] = function() {
        this.name = "HSLA";
        this.run = expect_continuation(this, [3, 4])(function(context) {
            var body = this.body.run(context);
            if (body.length === 3)
                body.push(1);
            body[0] = body[0] | 0;
            body[1] = (body[1] / 255 * 100 | 0) + '%';
            body[2] = (body[2] / 255 * 100 | 0) + '%';
            context.canvas.set_hsl(body);
        });
        this.compile = function() {
            if (this.body.value.length === 3)
                return 'canvas.set_hsl([' + this.body.value[0].compile() + '|0, (' + this.body.value[1].compile() + '/ 255 * 100 | 0) + "%", (' + this.body.value[2].compile() + '/ 255 * 100 | 0) + "%", 1])';
            else
                return 'canvas.set_hsl([' + this.body.value[0].compile() + '|0, (' + this.body.value[1].compile() + '/ 255 * 100 | 0) + "%", (' + this.body.value[2].compile() + '/ 255 * 100 | 0) + "%", ' + this.body.value[3].compile() + '])';
        };
    }).prototype = new PrefixStatement;

    (operations["p"] = function() {
        this.name = "Cursor";
        this.run = expect_continuation(this, 2)(function(context) {
            context.canvas.set_cursor(this.body.run(context));
        });
        this.compile = function() {
            return 'canvas.set_cursor([' + this.body.value[0].compile() + ', ' + this.body.value[1].compile() + '])';
        };
    }).prototype = new PrefixStatement;

    (operations["t"] = function() {
        this.name = "Translate";
        this.run = expect_continuation(this, 2)(function(context) {
            context.canvas.translate(this.body.run(context));
        });
        this.compile = function() {
            return 'canvas.translate([' + this.body.value[0].compile() + ', ' + this.body.value[1].compile() + '])';
        };
    }).prototype = new PrefixStatement;

    (operations["r"] = function() {
        this.name = "Rotate";
        this.run = function(context) {
            context.canvas.rotate(this.body.run(context));
        };
        this.compile = function() {
            return 'canvas.rotate(' + this.body.compile() + ')';
        };
    }).prototype = new PrefixStatement;

    (operations["S"] = function() {
        this.name = "Scale";
        this.run = expect_continuation(this, 2)(function(context) {
            context.canvas.scale(this.body.run(context));
        });
        this.compile = function() {
            return 'canvas.scale([' + this.body.value[0].compile() + ', ' + this.body.value[1].compile() + '])';
        };
    }).prototype = new PrefixStatement;


    function InfixOperation(left) {
        this.left = left;
        this.right = null;
        this.name = "?";
        this.push = function(operation) {this.right = operation;};
        this.run = function(context) {
            var left = this.left.run(context);
            var right = this.right.run(context);
            return this._run(left, right);
        };
        this.toString = function() {
            return this.left.toString() + this.name + (this.right ? this.right.toString() : "null");
        };
        this.compile = function() {
            return '(' + this.left.compile() + ' ' + this.name + ' ' + this.right.compile() + ')';
        };
    }
    InfixOperation.prototype = new Expression;

    (operations["+"] = function() {
        InfixOperation.apply(this, arguments);
        this.name = "+";
        this._run = function(l, r) {return l + r;};
    }).prototype = new InfixOperation;

    (operations["-"] = function() {
        InfixOperation.apply(this, arguments);
        this.name = "-";
        this._run = function(l, r) {return l - r;};
    }).prototype = new InfixOperation;

    (operations["*"] = function() {
        InfixOperation.apply(this, arguments);
        this.name = "*";
        this._run = function(l, r) {return l * r;};
    }).prototype = new InfixOperation;

    (operations["/"] = function() {
        InfixOperation.apply(this, arguments);
        this.name = "/";
        this._run = function(l, r) {return l / r;};
    }).prototype = new InfixOperation;

    (operations["%"] = function() {
        InfixOperation.apply(this, arguments);
        this.name = "%";
        this._run = function(l, r) {return l % r;};
    }).prototype = new InfixOperation;

    (operations["^"] = function() {
        InfixOperation.apply(this, arguments);
        this.name = "^";
        this._run = function(l, r) {return Math.pow(l, r);};
        this.compile = function() {
            return 'Math.pow(' + this.left.compile() + ', ' + this.right.compile() + ')';
        };
    }).prototype = new InfixOperation;

    (operations[">"] = function() {
        InfixOperation.apply(this, arguments);
        this.name = ">";
        this._run = function(l, r) {return l > r;};
    }).prototype = new InfixOperation;

    (operations["g"] = function() {
        InfixOperation.apply(this, arguments);
        this.name = "g";
        this._run = function(l, r) {return l >= r;};
        this.compile = function() {
            return '(' + this.left.compile() + ' >= ' + this.right.compile() + ')';
        };
    }).prototype = new InfixOperation;

    (operations["="] = function() {
        InfixOperation.apply(this, arguments);
        this.name = "=";
        this._run = function(l, r) {return l == r;};
        this.compile = function() {
            return '(' + this.left.compile() + ' == ' + this.right.compile() + ')';
        };
    }).prototype = new InfixOperation;

    (operations["x"] = function() {
        InfixOperation.apply(this, arguments);
        this.name = "x";
        this._run = function(l, r) {return l != r;};
        this.compile = function() {
            return '(' + this.left.compile() + ' != ' + this.right.compile() + ')';
        };
    }).prototype = new InfixOperation;


    var Continuation = function(left) {
        if (left instanceof Continuation)
            this.value = left.value;
        else
            this.value = [left];

        this.name = "Continuation";
        this.push = function(operation) {
            if (operation instanceof Continuation) {
                this.value = operation.value;
                return;
            }
            this.value.push(operation);
        };
        this.run = function(context) {
            var output = [];
            for (var k in this.value)
                output.push(this.value[k].run(context));
            return output;
        };
        this.toString = function() {
            var output = [];
            for (var k in this.value)
                output.push(this.value[k].toString());
            return "[" + output.join(",") + "]";
        };
    };
    Continuation.prototype = new InfixOperation;

    function Body() {
        this.body = [];
        this.name = "program";
    }
    Body.prototype = new BlockOperation;


    function parse(data) {
        var NUMBERS = ".0123456789";
        var BLOCK_END = ")";
        var BLOCK_STATEMENTS = "Li@{";
        var BLOCK_EXPRESSIONS = "(TAU";
        var SINGLE_OPERATIONS = "#<dP;";
        var PREFIX_STATEMENTS = "CHptrS";
        var PREFIX_EXPRESSIONS = "nN&|IXsoTEOY_`\"!\\aq";
        var INFIX_EXPRESSIONS = "+-*/^%M>g=x";
        var CONTINUATION = ",";
        var WHITESPACE = " \n\r\t";

        var STATEMENTS = SINGLE_OPERATIONS + PREFIX_STATEMENTS;

        var buffer = "";
        var blocks = [new Body()];
        var expressions = [];
        var position = 0;

        function push_block(block) {
            console.log("Push block", block.toString());
            blocks.push(block);
        }

        function pop_block() {
            var block = blocks.pop();
            console.log("Pop block", block.toString());
            if (expressions.length)
                block.push(collapse_expressions());
            
            blocks[blocks.length - 1].push(block);
            return block;
        }

        function push_to_block(node) {
            if (expressions.length)
                push_to_block(collapse_expressions());
            var block = blocks[blocks.length - 1];
            block.push(node);
            console.log("Push", node.toString(), "to block", block.toString());
        }

        function push_to_tip(node) {
            if (expressions.length) {
                var e = expressions[expressions.length - 1];
                if (e instanceof Number)
                    throw new Error("Cannot push expression to literal");
                if (node instanceof Number &&
                    (e instanceof Continuation ||
                     e instanceof InfixOperation)) {
                    e.push(node);
                    console.log("Pushed", node.toString(), "to back of", e.toString());
                    return;
                }
            }
            console.log("Pushed to tip", node.toString());
            expressions.push(node);
        }

        function collapse_expressions(offset) {
            var e = null;
            offset = offset || 0;
            while (expressions.length > offset) {
                e = expressions.pop();
                console.log("Collapsing", e.toString())
                if (expressions.length)
                    expressions[expressions.length - 1].push(e);
            }
            return e;
        }

        for (var i = 0; i < data.length; i++) {
            var e;
            var char_ = data[i];
            position += 1;
            if (!_in(NUMBERS, char_) && buffer.length) {
                push_to_tip(literal(buffer));
                buffer = "";
            } else if (_in(NUMBERS, char_)) {
                if (char_ === "." && _in(buffer, "."))
                    throw new Error("Invalid numeric literal");
                buffer += char_;
                continue;
            }

            if (char_ === CONTINUATION) {
                if (!expressions.length)
                    throw new Error("Continuation inside block");
                e = expressions.pop();
                if (!(e instanceof Number ||
                      e instanceof Expression ||
                      e instanceof PrefixExpression))
                    throw new Error("Continuation against non-expressive value (" + e + ")");
                push_to_tip(new Continuation(e));
                continue;
            }

            if (char_ === BLOCK_END) {
                var found = false;
                var j;
                for (j = expressions.length - 1; j >= 0; j--) {
                    var val = expressions[j];
                    if (!(val instanceof BlockExpression))
                        continue;
                    push_to_tip(collapse_expressions(j));
                    found = true;
                    break;
                }
                if (found)
                    continue;

                var blocks_left = false;
                for (j = 0; j < blocks.length; j++) {
                    if (blocks[j] instanceof BlockOperation) {
                        blocks_left = true;
                        break;
                    }
                }
                if (!blocks_left)
                    throw new Error("End of block detected outside of block");

                if (expressions.length)
                    push_to_block(collapse_expressions());

                var p = pop_block();
                while (!(p instanceof BlockOperation))
                    p = pop_block();
                continue;
            }

            if (_in(WHITESPACE, char_)) {
                if (expressions.length) {
                    e = expressions.pop();
                    if (e instanceof Continuation) {
                        expressions[expressions.length - 1].push(e);
                        e = expressions.pop();
                    }

                    if (expressions.length) {
                        var last_exp = expressions[expressions.length - 1];
                        last_exp.push(e);
                        var next_last = expressions[expressions.length - 2];
                        if (next_last instanceof Continuation) {
                            next_last.push(expressions.pop());
                        }
                    } else
                        push_to_block(e);
                }
                continue;
            }


            if (_in(STATEMENTS, char_)) {
                if (expressions.length)
                    push_to_block(collapse_expressions());
                push_to_tip(new operations[char_]());
            } else if (_in(PREFIX_EXPRESSIONS, char_)) {
                push_to_tip(new operations[char_]());
            } else if (_in(INFIX_EXPRESSIONS, char_)) {
                if (!expressions.length)
                    throw new Error("Infix operation in invalid location");
                e = expressions.pop();
                if (e instanceof Continuation) {
                    var last = e.value.pop();
                    expressions.push(e);
                    push_to_tip(new operations[char_](last));
                } else
                    push_to_tip(new operations[char_](e));
            } else if (_in(BLOCK_STATEMENTS, char_)) {
                if (expressions.length)
                    push_to_block(collapse_expressions());
                push_block(new operations[char_]());
            } else if (_in(BLOCK_EXPRESSIONS, char_)) {
                push_to_tip(new operations[char_]());
            }
        }

        if (expressions.length)
            throw new Error("Expressions remaining on the stack at termination.");

        var body = blocks.pop();
        if (blocks.length)
            throw new Error("Unclosed blocks detected at termination.");

        return body;
    }

    function TranslateTransform(xy) {
        this.x = xy[0];
        this.y = xy[1];
        this.get = function(xy) {
            return [this.x + xy[0], this.y + xy[1]];
        };
        this.get_ip = function(xy) {
            xy[0] += this.x;
            xy[1] += this.y;
        };
    }

    function RotateTransform(theta) {
        this.theta = theta;
        this.get = function(xy) {
            return [xy[0] * Math.cos(this.theta) - xy[1] * Math.sin(this.theta),
                    xy[1] * Math.cos(this.theta) + xy[0] * Math.sin(this.theta)];
        };
        this.get_ip = function(xy) {
            var x = xy[0];
            var y = xy[1];
            xy[0] = x * Math.cos(this.theta) - y * Math.sin(this.theta);
            xy[1] = y * Math.cos(this.theta) + x * Math.sin(this.theta);
        };
    }

    function ScaleTransform(xy) {
        this.x = xy[0];
        this.y = xy[1];
        this.get = function(xy) {
            return [this.x * xy[0], this.y * xy[1]];
        };
        this.get_ip = function(xy) {
            xy[0] *= this.x;
            xy[1] *= this.y;
        };
    }

    function CanvasWrap(canvas) {
        this.canvas = canvas.getContext("2d");
        this.cursor = [0, 0];
        this.last_point = [0, 0];
        this.transforms = [];
        this.scratch = [];

        this.canvas.strokeStyle = "black";
        this.canvas.clearRect(0, 0, canvas.width, canvas.height);
    }
    CanvasWrap.prototype = {
        canvas: null,
        cursor: null,
        last_point: null,
        transforms: null,
        scratch: null,
        color: "#000",
        clear_transforms: function() {
            console.log("Clearing transforms");
            this.transforms = [];
        },
        pop: function() {
            console.log("pop");
            this.transforms.pop();
        },
        set_color: function(rgba) {
            console.log(
                "set color",
                this.canvas.strokeStyle =
                    this.color = "rgba(" + rgba.join(",") + ")");
        },
        set_hsl: function(hsla) {
            console.log("set hsl",
                this.canvas.strokeStyle =
                    this.color = "hsla(" + hsla.join(",") + ")");
        },
        set_cursor: function(xy) {
            console.log("set cursor", xy[0]|0, xy[1]|0);
            this.cursor = xy;
            this.set_cursor = true;
        },
        translate: function(xy) {
            //console.log("translate", xy[0]|0, xy[1]|0);
            var last = this.transforms[this.transforms.length - 1];
            if (last instanceof TranslateTransform) {
                last.x += xy[0];
                last.y += xy[1];
            } else
                this.transforms.push(new TranslateTransform(xy));
        },
        rotate: function(deg) {
            //console.log("rotate", deg + 0);
            var last = this.transforms[this.transforms.length - 1];
            if (last instanceof RotateTransform)
                last.theta += deg;
            else
                this.transforms.push(new RotateTransform(deg));
        },
        scale: function(xy) {
            //console.log("scale", xy[0] + 0, xy[1] + 0);
            var last = this.transforms[this.transforms.length - 1];
            if (last instanceof ScaleTransform) {
                last.x *= xy[0];
                last.y *= xy[1];
            } else
                this.transforms.push(new ScaleTransform(xy));
        },
        get_cursor_null: function() {
            this.scratch[0] = 0;
            this.scratch[1] = 0;
            for (var i = 0; i < this.transforms.length; i++)
                this.transforms[i].get_ip(this.scratch);
            this.scratch[0] += this.cursor[0];
            this.scratch[1] += this.cursor[1];
        },
        dot: function() {
            console.log("dot");
            this.get_cursor_null();
            //this.canvas.fillRect(this.scratch[0], this.scratch[1], 1, 1);
            this.canvas.moveTo(this.scratch[0] | 0, this.scratch[0] | 0);
            this.canvas.lineTo(this.scratch[0] | 0, this.scratch[1] | 0);
            this.canvas.beginPath();
            this.last_point[0] = this.scratch[0];
            this.last_point[1] = this.scratch[1];
        },
        line: function() {
            //console.log("line");
            this.get_cursor_null();
            //this.canvas.moveTo(this.last_point[0] | 0, this.last_point[1] | 0);
            this.canvas.lineTo(this.scratch[0] | 0, this.scratch[1] | 0);
            this.canvas.stroke();
            this.last_point[0] = this.scratch[0];
            this.last_point[1] = this.scratch[1];
        }
    };

    function Context(canvas) {
        this.canvas = new CanvasWrap(canvas);
        this.vars = {};
        this.funcs = {};
    }
    Context.prototype = {
        vars: null,
        funcs: null,
        counter: 0,
        next_id: function() {
            var c = this.counter;
            this.counter++;
            while (c in this.vars || c in this.funcs) {
                c = this.counter;
                this.counter++;
            }
            return c;
        }
    };
    
    function run(canvas, data) {
        var tree = parse(data);
        var context = new Context(canvas);
        var output = tree.run(context);

    }

    function compile(canvas, data) {
        var tree = parse(data);
        var out = 'return function(canvas) {\n';
        out += 'var id;\n';
        out += 'var context = {};\n';
        out += tree.compile();

        out += '}';
        console.log(out);
        var compiled = new Function(out);
        compiled()(new CanvasWrap(canvas));
        return compiled;
    }

    return {
        run: run,
        compile: compile
    };
})();
