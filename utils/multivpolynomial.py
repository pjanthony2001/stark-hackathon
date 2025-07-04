from utils.field import FieldElement, Field
from utils.polynomial import Polynomial

class MultiVPolynomial :

    ALPHABET = 'XYZWTUVABCDEFGHIJKLMNOPQRSxyzwtuvabcdefghijklmnopqrs'
    
    def __init__(self, coef : 'dict[tuple[int]]') :
        if len(coef.keys()) == 0 :
            raise Exception('Multivariate olynomials must have at least 1 coefficient.')
        self.exp = list(coef.keys())
        if not FieldElement.field_eq([coef[exp] for exp in self.exp]) :
            raise Exception('Coefficients of the polynomial must belong to the same field.')
        self.field = coef[self.exp[0]].field
        self.var = len(self.exp[0])
        if False in [len(exp_list) == self.var for exp_list in self.exp] :
            raise Exception('The keys of the expomials dictionary must have the same length.')
        self.coef = coef

    @staticmethod
    def synchro(a : 'MultiVPolynomial', b : 'MultiVPolynomial') :
        if a.field != b.field :
            raise Exception('It makes no sense to synchronise two polynomials with coefficients from different fields.')
        a.monom_recalibration()
        b.monom_recalibration()
        a.var_recalibration()
        b.var_recalibration()
        if a.var < b.var :
            for exp in a.exp :
                a.coef[exp + tuple((b.var - a.var)*[0])] = a.coef[exp]
                del a.coef[exp]
        elif b.var < a.var :
            for exp in b.exp :
                b.coef[exp + tuple((a.var - b.var)*[0])] = b.coef[exp]
                del b.coef[exp] 
        a.actu()
        b.actu()


    @staticmethod
    def sum_list(l : 'list[int]') -> 'int' :
        sum = 0
        for k in l :
            if not isinstance(k, int) :
                raise TypeError('This list contains non integer elements.')
            sum += k
        return sum

    def monom_recalibration(self) -> None :
        print('monom_recalibration')
        print(self)
        if self.is_zero() :
            self = MultiVPolynomial.zero(self.field, 1)
        else :
            for exp in self.exp :
                if self.coef[exp].value == 0 :
                    del self.coef[exp]
        print(self)

    def var_recalibration(self) -> None :
        self.actu()
        n = self.var
        stopper = False
        for i in range(n) :
            while not stopper :
                print([exp[i] for exp in self.exp])
                if MultiVPolynomial.sum_list([exp[i] for exp in self.exp]) == 0 :
                    n -= 1
                else :
                    stopper = True
        if n < self.var :
            for exp in self.exp :
                self.coef[exp[:n]] = self.coef[exp]
                del self.coef[exp]
        self.actu()

    def actu(self) -> None :
        self.var = len(self.exp[0])
        self.exp = list(self.coef.keys())
    
    def __eq__(self, b : 'MultiVPolynomial') -> 'bool' :
        return self.coef == b.coef

    def monom_str(exp : 'list[int]', coef : 'FieldElement') -> 'str' :
        monom = ''
        for i in range(len(exp)) :
            var = ''
            if exp[i] != 0 :
                var += f'{MultiVPolynomial.ALPHABET[i]}'
                if exp[i] != 1 :
                    var = '(' + var + f'^{exp[i]})'
            monom += var
        if coef.value == 1 :
            return monom
        return str(coef) + '*' + monom

    def __str__(self) -> 'str' :
        if self.is_zero() :
            return '0'
        poly = ''
        self.actu()
        for exp in self.exp :
            coef = self.coef[exp]
            if coef.value != 0 :
                if len(poly) != 0 :
                    poly += ' + '
                if exp == tuple(self.var*[0]) :
                    poly += f'{coef.value}'
                else :
                    poly += f'{MultiVPolynomial.monom_str(exp, coef)}'
        return poly
    
    def __call__(self, ant : 'list[FieldElement]') -> 'FieldElement' :
        value = 0
        v = self.var
        for exp in self.exp :
            exp_val = self.coef[exp]
            for k in range(v) :
                exp_val *= ant[k]**exp[k]
            value += exp_val
        return value
    
    def __add__(self, b : 'MultiVPolynomial') -> 'MultiVPolynomial':
        if not isinstance(b, MultiVPolynomial) :
            raise TypeError('A multivariate polynomial can only be summed with multivariate polynomials.')
        self.actu()
        b.actu()
        if b.var != self.var :
            raise Exception('Impossible to sum multivariate polynomials with different number of variables.')
        if b.field != self.field :
            raise Exception('Impossible to sum multivariate polynomials linked to different fields.')
        sum = self
        for exp in b.exp :
            if exp in sum.exp :
                sum.coef[exp] += b.coef[exp]
            else :
                sum.coef[exp] = b.coef[exp]
        return sum
    
    def __radd__(self, b : 'FieldElement') -> 'MultiVPolynomial' :
        return self.__add__(b)

    def __neg__(self) -> 'MultiVPolynomial' :
        coef_neg = {}
        for exp in self.exp :
            coef_neg[exp] = -self.coef[exp]
        return MultiVPolynomial(coef_neg)

    def __sub__(self, b : 'MultiVPolynomial') -> 'MultiVPolynomial' :
        return self.__add__(-b)

    def __mul__(self, b : 'MultiVPolynomial|FieldElement') -> 'MultiVPolynomial' :
        if isinstance(b, FieldElement) :
            coef_b = {tuple(self.var*[0]) : b.value}
            b = MultiVPolynomial(coef_b)
        if not isinstance(b, MultiVPolynomial) :
            raise TypeError('A multivariate polynomial can only be multiplied with multivariate polynomials.')
        self.actu()
        b.actu()
        MultiVPolynomial.synchro(self, b)
        if b.var != self.var :
            raise Exception('Impossible to multiply multivariate polynomials with different number of variables.')
        if b.field != self.field :
            raise Exception('Impossible to multiply multivariate polynomials linked to different fields.')
        prod = MultiVPolynomial.zero(self.field, self.var)
        for exp_b in b.exp :
            print(f'exp_b = {exp_b}')
            for exp_self in self.exp :
                exp_prod = tuple([exp_b[i] + exp_self[i] for i in range(self.var)])
                if exp_prod in prod.exp :
                    prod.coef[exp_prod] += b.coef[exp_b]*self.coef[exp_self]
                else :
                    prod.coef[exp_prod] = b.coef[exp_b]*self.coef[exp_self]
        print()
        return prod
    
    def __rmul__(self, b : 'FieldElement') -> 'MultiVPolynomial' :
        return self.__mul__(b)

    def __truediv__(self, b : 'FieldElement') -> 'MultiVPolynomial' :
        return self.__mul__(FieldElement(b.field, 1/b.value))

    def __pow__(self, alpha : int) -> 'MultiVPolynomial' :
        if alpha == 0 :
            return self.one
        if alpha == 1 :
            return self
        b = self*self
        return self.__pow__(b, alpha//2)*self.__pow__(b, alpha%2)

    @staticmethod
    def zero(field : Field, var : 'int') -> 'MultiVPolynomial' :
        if var <= 0 :
            raise Exception('Zero multivariable polynomial mustt have at least 1 variable.')
        return MultiVPolynomial({tuple(var*[0]) : FieldElement(field, 0)})
    
    def is_zero(self) -> 'bool' :
        self.actu()
        zero = self.field.zero
        for exp in self.exp :
            if self.coef[exp] != zero :
                return False
        return True
    
    @classmethod
    def X(cls, field : Field, n : int) :
        return MultiVPolynomial({tuple((n - 1)*[0] + [1]) : FieldElement(field, 1)})

    @staticmethod
    def interpolate(x : 'list[list[FieldElement]]', y : 'list[FieldElement]') :
        n = len(x)
        if n == 0 :
            raise Exception('Impossible to interpolate from an empty list of abscissas.')
        if len(y) != n :
            raise Exception('Abscissas and ordinates lists must have the same length.')
        list_x = []
        for var_list in x :
            list_x += var_list 
        if not FieldElement.field_eq(list_x + y) :
            raise Exception('Abscissas and ordinates lists must belong to the same field.')
        P = MultiVPolynomial.zero()
        var = len(x)
        for i in range(n) :
            product = MultiVPolynomial({tuple(var*[0]) : y[i]})
            for j in range (n) :
                for k in range(var) :
                    if j != i :
                        product *= (MultiVPolynomial.X(k) - x[j][k])/(x[i][k] - x[j][k])
            P += product
        return P
    
    def monovariation(self, polys : 'list[Polynomial]') -> 'Polynomial':
        self.actu()
        if len(polys) != self.var - 1 :
            raise Exception('Not enough polynomials given.')
        monovariate = Polynomial.zero(self.field)
        for exp in self.exp :
            monom = Polynomial([self.coef[exp]])*(Polynomial.X(self.field)**exp[0])
            for k in range(1, self.var) :
                monom *= polys[k-1]**exp[k]
            monovariate += monom
        return monovariate
