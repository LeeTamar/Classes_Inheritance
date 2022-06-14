class Variable:
    def get_name(self):
        pass


class Assignment:
    def get_var(self) -> Variable:
        pass

    def get_value(self) -> float:
        pass

    def set_value(self, f: float):
        pass


class Assignments:
    def __getitem__(self, v: Variable) -> float:
        pass

    def __iadd__(self, ass: Assignment):
        pass


class Expression:
    def evaluate(self, assgms: Assignments) -> float:
        pass

    def derivative(self, v: Variable):
        pass

    def __repr__(self) -> str:
        pass

    def __eq__(self, other):
        if str(self) == str(other):
            return True
        else:
            return False

    def __add__(self, other):
        if issubclass(type(other), Expression) is True:
            return Addition(self, other)
        else:
            raise TypeError('other should be an Expression object')

    def __sub__(self, other):
        if issubclass(type(other), Expression) is True:
            return Subtraction(self, other)
        else:
            raise TypeError('other should be an Expression object')

    def __mul__(self, other):
        if issubclass(type(other), Expression) is True:
            return Multiplication(self, other)
        else:
            raise TypeError('other should be an Expression object')

    def __pow__(self, power: float, modulo=None):
        return Power(self, power)


class ValueAssignment(Assignment):
    def __init__(self, v: Variable, value: float):
        self.v = v
        self.value = float(value)

    def get_var(self) -> Variable:
        return self.v

    def get_value(self) -> float:
        return float(self.value)

    def set_value(self, f: float):
        self.value = f
        return self

    def __eq__(self, other) -> bool:
        if self.value == other.value and self.v == other.v:
            return True
        else:
            return False

    def __repr__(self) -> str:
        return str(self.v) + "=" + str(float(self.value))


class SimpleDictionaryAssignments(Assignments):
    def __init__(self):
        self.dicto = {}

    def __getitem__(self, v: Variable) -> float:
        if str(v) in self.dicto:
            return self.dicto[str(v)]
        else:
            return None

    def __iadd__(self, ass: Assignment):
        self.dicto[str(ass.get_var())] = ass.get_value()
        return self


class Constant(Expression):

    def __init__(self, value: float=0.0):
        self.value = float(value)

    def evaluate(self, assgms: Assignments = ()) -> float:
        return float(self.value)

    def derivative(self, v: Variable):
        return Constant()

    def __repr__(self) -> str:
        return str(self.value)


class VariableExpression(Variable,Expression):
    def __init__(self, variable_name):
        self.variable_name = variable_name

    def get_name(self):
        return self.variable_name

    def evaluate(self, assgms: Assignments) -> float:
        try:
            val = assgms[self.variable_name]
            return val
        except ValueError:
            print("\nThere is no assignment for this variable\n")

    def derivative(self, v: Variable):
        if VariableExpression(self.variable_name) == v:
            dev = Constant(1.0)
        else:
            dev = Constant()
        return dev

    def __repr__(self) -> str:
        return str(self.variable_name)


class Addition(Expression):
    def __init__(self, A: Expression, B: Expression) -> Expression:
        self.A = A
        self.B = B
        self.str_addi = str(self.A) + '+' + str(self.B)
        self.str_addi = "(" + self.str_addi + ")"

    def evaluate(self, assgms: Assignments) -> float:
        try:
            val = (self.A.evaluate(assgms) + self.B.evaluate(assgms))
        except ValueError:
            print("\nThere is no assignment for this variable\n")
        else:
            return val

    def derivative(self, v: Variable):
        return Addition(self.A.derivative(v), self.B.derivative(v))

    def __repr__(self) -> str:
        return self.str_addi


class Subtraction(Expression):
    def __init__(self, A: Expression, B: Expression) -> Expression:
        self.A = A
        self.B = B
        self.str_sub = str(self.A) + '-' + str(self.B)
        self.str_sub = "(" + self.str_sub + ")"

    def evaluate(self, assgms: Assignments) -> float:
        try:
            val = (self.A.evaluate(assgms) - self.B.evaluate(assgms))
            return val
        except ValueError:
            print("\nThere is no assignment for this variable\n")

    def derivative(self, v: Variable):
        return Subtraction(self.A.derivative(v), self.B.derivative(v))

    def __repr__(self) -> str:
        return self.str_sub


class Multiplication(Expression):
    def __init__(self, A: Expression, B: Expression) -> Expression:
        self.A = A
        self.B = B
        self.str_mul = str(self.A) + '*' + str(self.B)
        self.str_mul = "(" + self.str_mul + ")"

    def evaluate(self, assgms: Assignments) -> float:
        try:
            val = (self.A.evaluate(assgms) * self.B.evaluate(assgms))
        except ValueError:
            print("\nThere is no assignment for this variable\n")
        else:
            return val

    def derivative(self, v: Variable):
        A_dev = self.A.derivative(v)
        B_dev = self.B.derivative(v)
        dev = A_dev*self.B + self.A*B_dev
        return dev

    def __repr__(self) -> str:
        return self.str_mul


class Power(Expression):
    def __init__(self, exp: Expression, p: float) -> Expression:
        self.exp = exp
        self.p = p
        self.str_pow = str(self.exp) + '^' + str(float(self.p))
        self.str_pow = "(" + self.str_pow + ")"

    def evaluate(self, assgms: Assignments) -> float:
        try:
            basis = self.exp.evaluate(assgms)
            ev_pow = basis ** self.p
            return ev_pow
        except ValueError:
            print("\nThere is no assignment for this variable\n")

    def derivative(self, v: Variable):
        elem1 = Constant(self.p)
        elem2 = Power(self.exp, (self.p - 1))
        elem3 = self.exp.derivative(v)
        dev = elem1*elem2*elem3
        return dev

    def __repr__(self) -> str:
        return self.str_pow


class Polynomial(Expression):
    def __init__(self, v: Variable, coefs: list) -> Expression:
        self.v = v
        self.coefs = coefs

    def NR_evaluate(self, ass:ValueAssignment, epsilon: int = 0.0001, times: int = 100):
        x = ass.get_value()
        fn = self
        dfn = self.derivative(self.v)
        for i in range(times):
            new_ass = ValueAssignment(self.v, x)
            sda = SimpleDictionaryAssignments()
            sda += new_ass
            up = fn.evaluate(sda)
            down = dfn.evaluate(sda)
            xnew = x - (up/down)
            if abs(xnew-x) < epsilon:
                break
            x = xnew
        if abs(xnew-x) > epsilon:
            raise ValueError("the function did not converge to the desired accuracy in 'times' number of iterations")
        return x

    def evaluate(self, assgms: Assignments) -> float:
        try:
            lst_pol = self.coefs
            var_val = assgms.__getitem__(self.v)
            value = 0
            N = len(lst_pol)
            n = 0
            while N - n > 0:
                value += lst_pol[n] * (var_val ** n)
                n += 1
            return value
        except ValueError:
            print("\nThere is no assignment for this variable\n")

    def derivative(self, u: Variable):
        if self.v == u:
            dev_lst = []
            for i in range(1, len(self.coefs)):
                if i == 1:
                    dev_lst.append(self.coefs[i])
                else:
                    coef = self.coefs[i] * i
                    dev_lst.append(coef)
            return Polynomial(self.v,dev_lst)
        else:
            return 0.0

    def __repr__(self) -> str:
        var = self.v
        lst_pol = self.coefs
        if lst_pol[0] > 0:
            poly = '+' + str(lst_pol[0])
        elif lst_pol[0] < 0:
            poly = str(lst_pol[0])
        else:
            poly = ""
        t = 0
        for i in range(1, len(lst_pol)):
            z = lst_pol[i]
            t += 1
            if z != 0:
                if t > 1:
                    if i == len(lst_pol) - 1 or z < 0:
                        poly = str(z) + str(var) + '^' + str(t) + poly
                    elif z > 0:
                        poly = '+' + str(z) + str(var) + '^' + str(t) + poly
                elif t == 1:
                    if i == len(lst_pol) - 1 or z < 0:
                        poly = str(z) + str(var) + poly
                    elif z > 0:
                        poly = '+' + str(z) + str(var) + poly
                elif t == 0:
                    if i == len(lst_pol) - 1 or z < 0:
                        poly = str(z) + poly
                    elif z > 0:
                        poly = '+' + str(z) + poly
        poly = '('+poly+')'
        self.poly = poly
        return poly
