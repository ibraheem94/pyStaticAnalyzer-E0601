from pyStaticAnalyzer.checker import add_method, Checker
from pyStaticAnalyzer.kernel import FileKernel
import ast
import re


def dfs_check_var_assign(k, cur, used):
    if cur not in used:
        if cur.endswith(".py"):
            messages = []
            cur_ast = k.get_file_ast(cur)
            rhs = {}
            id = 0
            nodes = ast.walk(cur_ast)
            nod = list(nodes)
            for i, node in enumerate(nod):
                if isinstance(node, ast.Assign):
                    name = node.targets[0]
                    value = node.value
                    if isinstance(name, ast.Name) and isinstance(value, (ast.Constant, ast.Num)) and isinstance(nod[i - 1], ast.Global):
                        rhs[id] = [str(name.id), 1, 'Const', str(node.lineno)]
                        id = id + 1
                    elif isinstance(name, ast.Name) and isinstance(value, (ast.Constant, ast.Num)) and not isinstance(nod[i - 1], ast.Global):
                        rhs[id] = [str(name.id), 0, 'Const', str(node.lineno)]
                        id = id + 1
                    elif isinstance(name, ast.Name) and isinstance(value, ast.BinOp) and isinstance(nod[i - 1], ast.Global) and isinstance(value.left, ast.Name) and (str(name.id) == str(value.left.id)):
                        rhs[id] = [str(name.id), 1, 'Binop', str(node.lineno)]
                        id = id + 1
                    elif isinstance(name, ast.Name) and isinstance(value, ast.BinOp) and isinstance(nod[i - 1], ast.Global) and isinstance( value.right, ast.Name) and (str(name.id) == str(value.right.id)):
                        rhs[id] = [str(name.id), 1, 'Const', str(node.lineno)]
                        id = id + 1
                    elif isinstance(name, ast.Name) and isinstance(value, ast.BinOp) and not isinstance(nod[i - 1], ast.Global) and isinstance(value.left, ast.Name) and (str(name.id) == str(value.left.id)):
                        rhs[id] = [str(name.id), 0, 'Binop', str(node.lineno)]
                        id = id + 1
                    elif isinstance(name, ast.Name) and isinstance(value, ast.BinOp) and not isinstance(nod[i - 1],ast.Global) and isinstance(value.right, ast.Name) and (str(name.id) == str(value.right.id)):
                        rhs[id] = [str(name.id), 0, 'Binop', str(node.lineno)]
                        id = id + 1
                    elif isinstance(name, ast.Name) and isinstance(value, ast.UnaryOp) and isinstance(nod[i - 1], ast.Global):
                        rhs[id] = [str(name.id), 1, 'Const', str(node.lineno)]
                        id = id + 1
                    elif isinstance(name, ast.Name) and isinstance(value, ast.UnaryOp) and not isinstance(nod[i - 1], ast.Global):
                        rhs[id] = [str(name.id), 0, 'Binop', str(node.lineno)]
                        id = id + 1
                elif isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                    childern = []
                    for  childs in ast.iter_child_nodes(node):
                        # print(child)
                        childern.append(childs)
                    for t, child in enumerate(childern):
                        if isinstance(child, ast.Expr) and isinstance(childern[t - 1],ast.Global):
                            val= child.value
                            if isinstance(val, ast.Call):
                                # argname=val.args.name
                                for i in range(0 , len(val.args)):
                                    if isinstance(val.args[i], ast.Name):
                                        rhs[id] = [str(name.id), 1, 'Const', str(child.lineno)]
                                        id = id + 1
                            # print(child)

                        elif isinstance(child, ast.Expr) and not isinstance(childern[t - 1],ast.Global):
                            val= child.value
                            if isinstance(val, ast.Call):
                                # argname=val.args.name
                                for i in range(0 , len(val.args)):
                                    if isinstance(val.args[i], ast.Name):
                                        rhs[id] = [str(val.args[i].id), 0, 'Binop', str(child.lineno)]
                                        id = id + 1
                        elif isinstance(child, ast.If) and not isinstance(childern[t - 1],ast.Global):
                            # print(childern[t - 1])
                            val= child.test
                            if isinstance(val, ast.Compare):
                                # argname=val.args.name
                                if isinstance(val.left, ast.Name):
                                    rhs[id] = [str(val.left.id), 0, 'Binop', str(child.lineno)]
                                    id = id + 1
                                if isinstance (val.comparators, ast.Name):
                                    rhs[id] = [str(val.left.id), 0, 'Binop', str(child.lineno)]
                                    id = id + 1
                        elif isinstance(child, ast.If) and  isinstance(childern[t - 1],ast.Global):
                            # print(childern[t - 1])
                            val= child.test
                            if isinstance(val, ast.Compare):
                                # argname=val.args.name
                                if isinstance(val.left, ast.Name):
                                    rhs[id] = [str(val.left.id), 1, 'Const', str(child.lineno)]
                                    id = id + 1
                                if isinstance (val.comparators, ast.Name):
                                    rhs[id] = [str(val.left.id), 1, 'Const', str(child.lineno)]
                                    id = id + 1
            # print(rhs)
            for j in range(1, len(rhs.keys())):
                for d in reversed(range(0, j)):
                    if (rhs[d][0] == rhs[j][0] and rhs[j][2] == "Binop" and rhs[d][1] == 1):
                        break
                    elif (rhs[d][0] == rhs[j][0] and rhs[j][2] == "Binop" and rhs[d][1] == 0):
                        messages.append(
                            "line " + rhs[j][3] + ": E0601 Using variable \"" + str(rhs[d][0]) + "\" before assignment")
            if messages:
                print(cur)
                for message in messages:
                    print(message)
                print()
        used.add(cur)
        for child in k.get_structure[cur]:
            dfs_check_var_assign(k, child, used)


# pylint C0102
@add_method(Checker)
def check_var_assign(k):
    used = set()
    dfs_check_var_assign(k,  k.get_path, used)


if __name__ == "__main__":
    k = FileKernel('first.py')
    c = Checker()
    checks = c.get_all_checks()
    print(checks)
    c.run_check('check_var_assign', k)