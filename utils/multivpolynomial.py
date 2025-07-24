from utils.field import FieldElement, Field
from utils.polynomial import Polynomial, PolynomialException

class MultiVPolynomial :

    ALPHABET = 'XYZWTUVABCDEFGHIJKLMNOPQRSxyzwtuvabcdefghijklmnopqrs'
    
    def __init__(self, coef : 'dict[tuple]') : # type: ignore
        if len(coef.keys()) == 0 :
            raise PolynomialException('Multivariate olynomials must have at least 1 coefficient.')
        self.exp = list(coef.keys())
        for exp in self.exp :
            for alpha in exp :
                if not isinstance(alpha, int) :
                    raise PolynomialException('Exponents must be integers.')
        if not FieldElement.field_eq([coef[exp] for exp in self.exp]) :
            raise PolynomialException('Coefficients of the polynomial must belong to the same field.')
        self.field = coef[self.exp[0]].field
        self.var = len(self.exp[0])
        if False in [len(exp_list) == self.var for exp_list in self.exp] :
            raise PolynomialException('The keys of the expomials dictionary must have the same length.')
        self.coef = coef

    @staticmethod
    def synchro(a : 'MultiVPolynomial', b : 'MultiVPolynomial') :
        if a.field != b.field :
            raise PolynomialException('It makes no sense to synchronise two polynomials with coefficients from different fields.')
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
        sum_ = 0
        for k in l :
            if not isinstance(k, int) :
                raise TypeError('This list contains non integer elements.')
            sum_ += k
        return sum_

    def monom_recalibration(self) -> None :
        if self.is_zero() :
            self = MultiVPolynomial.zero(self.field, 1) # TODO: rework this to change the  object attributes instead of self assignment
        else :
            for exp in self.exp :
                if self.coef[exp].value == 0 :
                    del self.coef[exp]

    def var_recalibration(self) -> None :
        self.actu()
        n = self.var
        stopper = False
        for i in range(n) :
            while not stopper and n >= 0 :
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
    
    def __eq__(self, b : 'MultiVPolynomial') -> 'bool' : # type: ignore
        return self.coef == b.coef

    @staticmethod
    def monom_str(exp : 'tuple[int]', coef : 'FieldElement') -> 'str' :
        monom = ''
        for i, exponent in enumerate(exp) :
            var = ''
            if exponent != 0 :
                var += f'{MultiVPolynomial.ALPHABET[i]}'
                if exponent != 1 :
                    var = '(' + var + f'^{exponent})'
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
        value = self.field.zero
        v = self.var
        for exp in self.exp :
            exp_val = self.coef[exp]
            for k in range(v) :
                exp_val *= ant[k]**exp[k]
            value += exp_val
        return value
    
    def __add__(self, b : 'MultiVPolynomial|FieldElement|Polynomial') -> 'MultiVPolynomial':
        if isinstance(b, FieldElement) :
            b = MultiVPolynomial({(0, 0) : b})
        if isinstance(b, Polynomial) :
            b = MultiVPolynomial.multivariation(b)
        if not isinstance(b, MultiVPolynomial) :
            raise TypeError('A multivariate polynomial can only be summed with multivariate polynomials.')
        MultiVPolynomial.synchro(self, b)
        if b.field != self.field :
            raise PolynomialException('Impossible to sum multivariate polynomials linked to different fields.')
        sum_ = self
        for exp in b.exp :
            if exp in sum_.exp :
                sum_.coef[exp] += b.coef[exp]
            else :
                sum_.coef[exp] = b.coef[exp]
        return sum_
    
    def __radd__(self, b : 'FieldElement|Polynomial') -> 'MultiVPolynomial' :
        return self.__add__(b)

    def __neg__(self) -> 'MultiVPolynomial' :
        coef_neg = {}
        for exp in self.exp :
            coef_neg[exp] = -self.coef[exp]
        return MultiVPolynomial(coef_neg)

    def __sub__(self, b : 'MultiVPolynomial|FieldElement|Polynomial') -> 'MultiVPolynomial' :
        return self.__add__(-b)

    def __rsub__(self, b : 'FieldElement|Polynomial') -> 'MultiVPolynomial' :
        return self.__sub__(b)

    def __mul__(self, b : 'MultiVPolynomial|FieldElement|Polynomial') -> 'MultiVPolynomial' :
        if isinstance(b, FieldElement) :
            coef_b = {tuple(self.var*[0]) : b.value}
            b = MultiVPolynomial(coef_b)
        if isinstance(b, Polynomial) :
            b = MultiVPolynomial.multivariation(b)
        if not isinstance(b, MultiVPolynomial) :
            raise TypeError('A multivariate polynomial can only be multiplied with multivariate polynomials.')
        MultiVPolynomial.synchro(self, b)
        print(self.var)
        print(b.var)
        if b.field != self.field :
            raise PolynomialException('Impossible to multiply multivariate polynomials linked to different fields.')
        prod = MultiVPolynomial.zero(self.field, self.var)
        for exp_b in b.exp :
            for exp_self in self.exp :
                exp_prod = tuple([exp_b[i] + exp_self[i] for i in range(self.var)])
                if exp_prod in prod.exp :
                    prod.coef[exp_prod] += b.coef[exp_b]*self.coef[exp_self]
                else :
                    prod.coef[exp_prod] = b.coef[exp_b]*self.coef[exp_self]
        return prod
    
    def __rmul__(self, b : 'FieldElement|Polynomial') -> 'MultiVPolynomial' :
        return self.__mul__(b)

    def __truediv__(self, b : 'FieldElement') -> 'MultiVPolynomial' :
        return self.__mul__(FieldElement(b.field, b.value**int(-1)))

    def __pow__(self, alpha : int) -> 'MultiVPolynomial' :
        if alpha == 0 :
            return MultiVPolynomial.one(self.field, self.var)
        if alpha == 1 :
            return self
        b = self*self
        return b.__pow__(alpha//2)*self.__pow__(alpha%2)

    @staticmethod
    def one(field : 'Field', var : 'int') :
        return MultiVPolynomial({tuple(var*[0]) : FieldElement(field, 1)})

    @staticmethod
    def zero(field : 'Field', var : 'int') -> 'MultiVPolynomial' :
        if var <= 0 :
            raise PolynomialException('Zero multivariable polynomial mustt have at least 1 variable.')
        return MultiVPolynomial({tuple(var*[0]) : FieldElement(field, 0)})
    
    def is_zero(self) -> 'bool' :
        self.actu()
        zero = self.field.zero
        for exp in self.exp :
            if self.coef[exp] != zero :
                return False
        return True
    
    @classmethod
    def X(cls, field : 'Field', n : 'int') :
        return MultiVPolynomial({tuple((n - 1)*[0] + [1]) : FieldElement(field, 1)})

    @staticmethod
    def interpolate(x : 'list[list[FieldElement]]', y : 'list[FieldElement]') :
        n = len(x)
        if n == 0 :
            raise PolynomialException('Impossible to interpolate from an empty list of abscissas.')
        if len(y) != n :
            raise PolynomialException('Abscissas and ordinates lists must have the same length.')
        list_x = []
        for var_list in x :
            list_x += var_list 
        if not FieldElement.field_eq(list_x + y) :
            raise PolynomialException('Abscissas and ordinates lists must belong to the same field.')
        var = len(x[0])
        if var == 0 :
            raise PolynomialException('Abscissas\' list contains only empty lists : impossible to interpolate a no-variate polyomial.') 
        field = x[0][0].field
        P = MultiVPolynomial.zero(field, var)
        for i in range(n) :
            product = MultiVPolynomial({tuple(var*[0]) : y[i]})
            for j in range (n) :
                for k in range(var) :
                    if j != i :
                        product *= (MultiVPolynomial.X(field, k) - x[j][k])/(x[i][k] - x[j][k])
            P += product
        return P
    
    def monovariation(self, polys : 'list[Polynomial]') -> 'Polynomial':
        self.actu()
        if len(polys) != self.var - 1 :
            raise PolynomialException('Not enough polynomials given.')
        monovariate = Polynomial.zero(self.field)
        for exp in self.exp :
            monom = Polynomial([self.coef[exp]])*(Polynomial.X(self.field)**exp[0])
            for k in range(1, self.var) :
                monom *= polys[k-1]**exp[k]
            monovariate += monom
        return monovariate

    @classmethod
    def multivariation(cls, poly : 'Polynomial') -> 'MultiVPolynomial' :
        multiv_coef = {}
        for exp, coef in enumerate(poly.coef) :
            multiv_coef[tuple([exp])] = coef
        return cls(multiv_coef)