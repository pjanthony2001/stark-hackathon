from field import FieldElement, Field


class MultiVPolynomial :
    ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    def __init__(self, coef : 'dict[list[int]]') :
        if len(dict.keys()) == 0 :
            raise Exception('Multivariate olynomials must have at least 1 coefficient.')
        self.exp = coef.keys()
        if not FieldElement.field_eq([coef[exp] for exp in self.exp]) :
            raise Exception('Coefficients of the polynomial must belong to the same field.')
        self.field = coef[self.exp[0]].field
        self.var = len(self.exp[0])
        if False in [len(exp_list) == self.var for exp_list in self.exp] :
            raise Exception('The keys of the expomials dictionary must have the same length.')
        self.coef = coef

    def __eq__(self, b : 'MultiVPolynomial') -> 'bool' :

        return self.coef == b.coef

    def monom_str(exp : 'list[int]', coef : 'FieldElement') -> 'str' :
        monom = ''
        for i in range(len(exp)) :
            monom += f'({MultiVPolynomial.ALPHABET[i]}^{exp[i]})'
        if coef.value == 1 :
            return monom
        return str(coef) + '*' + monom


    def __str__(self) -> 'str' :
        if self.is_zero() :
            return '0'
        poly = ''
        for exp in self.exp :
            coef = self.coef[exp]
            if coef.value != 0 :
                if len(poly) != 0 :
                    poly += ' + '
                if exp == self.var*[0] :
                    poly += f'{coef}'
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
            coef_b = {self.var*[0] : b.value}
            b = MultiVPolynomial(coef_b)
        if not isinstance(b, MultiVPolynomial) :
            raise TypeError('A multivariate polynomial can only be multiplied with multivariate polynomials.')
        if b.var != self.var :
            raise Exception('Impossible to multiply multivariate polynomials with different number of variables.')
        if b.field != self.field :
            raise Exception('Impossible to multiply multivariate polynomials linked to different fields.')
        prod = MultiVPolynomial.zero(self.field, self.var)
        for exp_b in b.exp :
            for exp_self in self.exp :
                exp_prod = [exp_b[i] + exp_self[i] for i in range(self.var)]
                if exp_prod in prod.exp :
                    prod.coef[exp_prod] += b.coef[exp_b]*self.coef[exp_self]
                else :
                    prod.coef[exp_prod] = b.coef[exp_b]*self.coef[exp_self]
        return prod
    
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
        return MultiVPolynomial({var*[0] : FieldElement(field, 0)})
    
    def is_zero(self) -> 'bool' :
        return len(self.exp) == 1 and self.coef[self.exp[0]].value == 0