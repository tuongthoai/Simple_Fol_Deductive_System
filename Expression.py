from defaultDict import defaultkeydict
import itertools


class Expression:
    """An Expression has its operator and arguments
    Examples: 2 + 3 then op (operator)   is '+' and args is (2, 3)
              plusOne(x): op= plusOne args is (x)
    """

    def __init__(self, op, *args):
        self.op = str(op)
        self.args = args

    # Operator overloads
    def __and__(self, rhs):
        return Expression('&', self, rhs)

    def __or__(self, rhs):
        if isinstance(rhs, Expression):
            return Expression('|', self, rhs)
        else:
            return UnaryExpression(rhs, self)

    def __invert__(self):
        return Expression('~', self)

    # Reverse operator overloads

    def __rand__(self, lhs):
        return Expression('&', lhs, self)

    def __ror__(self, lhs):
        return Expression('|', lhs, self)

    def __call__(self, *args):
        """Call: if 'f' is a Symbol, then f(0) == Expression('f', 0)."""
        if self.args:
            raise ValueError('Cannot convert into Expression')
        else:
            return Expression(self.op, *args)

    # Equality and repr
    def __eq__(self, other):
        """two Expression is equal if it has the same op and args"""
        return isinstance(other, Expression) and self.op == other.op and self.args == other.args

    def __lt__(self, other):
        return isinstance(other, Expression) and str(self) < str(other)

    def __hash__(self):
        return hash(self.op) ^ hash(self.args)

    def __repr__(self):
        op = self.op
        args = [str(arg) for arg in self.args]
        if op.isidentifier():  # f(x) or f(x, y)
            return '{}({})'.format(op, ', '.join(args)) if args else op
        elif len(args) == 1:  # -x or -(x + 1)
            return op + args[0]
        else:  # (x - y)
            opp = (' ' + op + ' ')
            return '(' + opp.join(args) + ')'


class UnaryExpression:
    """If a single Symbol comes with a opertor"""

    def __init__(self, op, lhs):
        self.op, self.lhs = op, lhs

    def __or__(self, rhs):
        return Expression(self.op, self.lhs, rhs)

    def __repr__(self):
        return "UnaryExpression('{}', {})".format(self.op, self.lhs)


def Symbol(name):
    """A Symbol is just an Expression with no args."""
    return Expression(name)


def toExpression(x):
    """
    :param x: a string of expresion
    :return: an Expression eval by python interpreter using eval and proper Expression implementation.
    """

    res = eval(handling_sentences(x), defaultkeydict(Symbol)) if isinstance(x, str) else x
    return res


def handling_sentences(x):
    x = x.replace("not", "~").replace(" ", "").replace("),", ")&").replace(");", ")|").replace(".", "").replace('\n',
                                                                                                                '')
    x = x.replace("not", "~")
    if ':-' in x:
        lhs, rhs = x.split(':-')
        x = rhs + "|'==>'|" + lhs
    return x


def subst(s, x):
    """Substitute the substitution s into the expression x.
        S is dict contain mapping value of each variable to its value then assign it into the expression x
    """
    if isinstance(x, list):
        return [subst(s, xi) for xi in x]
    elif isinstance(x, tuple):
        return tuple([subst(s, xi) for xi in x])
    elif not isinstance(x, Expression):
        return x
    elif is_var_symbol(x.op):
        return s.get(x, x)
    else:
        return Expression(x.op, *[subst(s, arg) for arg in x.args])


def unify(x, y, s=None):
    if s is None:
        s = {}
    extended_theta = extend(s, x, y)
    s = extended_theta.copy()
    while True:
        trans_cnt = 0
        for x, y in extended_theta.items():
            if x == y:
                # if x = y this mapping is deleted (rule b)
                del s[x]
            elif not is_variable(x) and is_variable(y):
                # if x is not a variable and y is a variable, rewrite it as y = x in s (rule a)
                if s.get(y, None) is None:
                    s[y] = x
                    del s[x]
                else:
                    # if a mapping already exist for variable y then apply
                    # variable elimination (there is a chance to apply rule d)
                    s[x] = vars_elimination(y, s)
            elif not is_variable(x) and not is_variable(y):
                # in which case x and y are not variables, if the two root function symbols
                # are different, stop with failure, else apply term reduction (rule c)
                if x.op is y.op and len(x.args) == len(y.args):
                    term_reduction(x, y, s)
                    del s[x]
                else:
                    return None
            elif isinstance(y, Expression):
                # in which case x is a variable and y is a function or a variable (e.g. F(z) or y),
                # if y is a function, we must check if x occurs in y, then stop with failure, else
                # try to apply variable elimination to y (rule d)
                if occur_check(x, y, s):
                    return None
                s[x] = vars_elimination(y, s)
                if y == s.get(x):
                    trans_cnt += 1
            else:
                trans_cnt += 1
        if trans_cnt == len(extended_theta):
            # if no transformation has been applied, stop with success
            return s
        extended_theta = s.copy()


def is_definite_clause(s):
    """
    check if s in in form A & B & ... & C ==> D,
    or ~A | ~B | ... | ~C | D
    """
    if is_symbol(s.op):
        return True
    elif s.op == '==>':
        antecedent, consequent = s.args
        return is_symbol(consequent.op) and all(is_symbol(arg.op) for arg in conjuncts(antecedent))
    else:
        return False


def standardize_variables(sentence, dic=None):
    """Replace all the variables in sentence with new variables."""
    if dic is None:
        dic = {}
    if not isinstance(sentence, Expression):
        return sentence
    elif is_var_symbol(sentence.op):
        if sentence in dic:
            return dic[sentence]
        else:
            v = Expression('X_{}'.format(next(standardize_variables.counter)))
            dic[sentence] = v
            return v
    else:
        return Expression(sentence.op, *[standardize_variables(a, dic) for a in sentence.args])


standardize_variables.counter = itertools.count()


def is_variable(x):
    """
    Checking if a Expression is a variable or not (Expression has no args and op is uppercase first letter)
    """
    return isinstance(x, Expression) and not x.args and x.op[0].isupper()


def is_var_symbol(s):
    """
    check if a string is a Variable or not (uppercase first letter)
    """
    return is_symbol(s) and s[0].isupper()


def is_symbol(s):
    return isinstance(s, str) and s[:1].isalpha()


def dissociate(op, args):
    """
    :param op: Opertator
    :param args: argument
    :return: arguments that op between
    """
    result = []

    def collect(subargs):
        for arg in subargs:
            if arg.op == op:
                collect(arg.args)
            else:
                result.append(arg)

    collect(args)
    return result


def conjuncts(s):
    return dissociate('&', [s])


def extend(s, var, val):
    """Copy dict s and extend it by setting var to val; return copy."""
    return {**s, var: val}


def vars_elimination(x, s):
    """Apply variable elimination to x: if x is a variable and occurs in s, return
    the term mapped by x, else if x is a function recursively applies variable
    elimination to each term of the function."""
    if not isinstance(x, Expression):
        return x
    if is_variable(x):
        return s.get(x, x)
    return Expression(x.op, *[vars_elimination(arg, s) for arg in x.args])


def occur_check(var, x, s):
    """Return true if variable var occurs anywhere in x
    (or in subst(s, x), if s has a binding for x)."""
    if var == x:
        return True
    elif is_variable(x) and x in s:
        return occur_check(var, s[x], s)
    elif isinstance(x, Expression):
        return (occur_check(var, x.op, s) or
                occur_check(var, x.args, s))
    elif isinstance(x, (list, tuple)):
        return first(e for e in x if occur_check(var, e, s))
    else:
        return False


def term_reduction(x, y, s):
    """Apply term reduction to x and y if both are functions and the two root function
    symbols are equals (e.g. F(x1, x2, ..., xn) and F(x1', x2', ..., xn')) by returning
    a new mapping obtained by replacing x: y with {x1: x1', x2: x2', ..., xn: xn'}
    """
    for i in range(len(x.args)):
        if x.args[i] in s:
            s[s.get(x.args[i])] = y.args[i]
        else:
            s[x.args[i]] = y.args[i]


def first(iterable, default=None):
    """Return the first element of an iterable; or default."""
    return next(iter(iterable), default)


def parse_definite_clause(s):
    """Return the antecedents and the consequent of a definite clause."""
    assert is_definite_clause(s)
    if is_symbol(s.op):
        return [], s
    else:
        antecedent, consequent = s.args
        return conjuncts(antecedent), consequent