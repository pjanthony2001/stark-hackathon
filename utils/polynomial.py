from utils.field import FieldElement, Field, MainFieldElement
from utils.domain import Domain


class PolynomialException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"PolynomialException: {self.message}"


class Polynomial:
    def __init__(self, coef: "list[FieldElement]"):
        if len(coef) == 0:
            raise PolynomialException("Polynomials must have at least 1 coefficient.")
        if not FieldElement.field_eq(coef):
            raise PolynomialException(
                "Coefficients of the polynomial must belong to the same field."
            )
        self.coef = coef
        self.field = self.coef[0].field

    def deg(self) -> "int":
        n = len(self.coef) - 1
        while n >= 0 and self.coef[n].value == 0:
            n -= 1
        return n

    def is_zero(self) -> "bool":
        return self.deg() == -1

    def __repr__(self) -> "str":
        return f"Polynomial(coef = {self.coef}, field = {self.field})"

    def __str__(self) -> "str":
        if self.is_zero():
            return "0"
        poly = ""
        for index, coef in enumerate(self.coef):
            if coef.value != 0:
                if len(poly) != 0:
                    poly += " + "
                if index == 0:
                    poly += f"{coef.value}"
                elif coef.value == 1:
                    poly += f"X^{index}"
                else:
                    poly += f"{coef.value}*X^{index}"
        return poly

    @staticmethod
    def synchro(a: "Polynomial", b: "Polynomial|FieldElement") -> "int":

        if a.field != b.field:
            raise PolynomialException(
                "It makes no sense to synchronize two polynomials \
                    with coefficients from different fields."
            )
        if isinstance(b, FieldElement):
            b = Polynomial([b])
        d = max(a.deg(), b.deg())
        a.coef = a.coef[: a.deg() + 1]
        b.coef = b.coef[: b.deg() + 1]
        if len(a.coef) <= d:
            a.coef = a.coef + (d + 1 - len(a.coef)) * [FieldElement(a.field, 0)]
        if len(b.coef) <= d:
            b.coef = b.coef + (d + 1 - len(b.coef)) * [FieldElement(b.field, 0)]
        return d

    def __eq__(self, b: object) -> "bool":

        if not isinstance(b, Polynomial):
            return False

        if self.field == b.field:
            Polynomial.synchro(self, b)
            return self.coef == b.coef
        return False

    def __add__(self, b: "Polynomial|FieldElement") -> "Polynomial":
        if isinstance(b, FieldElement):
            b = Polynomial([b])
        if isinstance(b, Polynomial):
            if b.field != self.field:
                raise PolynomialException(
                    "Impossible to sum multivariate polynomials linked to different fields."
                )
            if b.is_zero():
                return self
            d = Polynomial.synchro(self, b)
            return Polynomial([self.coef[i] + b.coef[i] for i in range(d + 1)])
        else:
            print("Only polynomials or field elements can be added to polynomials.")

    def __radd__(self, b: "FieldElement"):
        return self.__add__(b)

    def __neg__(self) -> "Polynomial":
        return Polynomial([-coef for coef in self.coef])

    def __sub__(self, b: "Polynomial|FieldElement") -> "Polynomial":
        Polynomial.synchro(self, b)
        return self.__add__(-b)

    def __rsub__(self, b: "FieldElement"):
        return self.__sub__(b)

    def __mul__(self, b: "Polynomial|FieldElement") -> "Polynomial":  # type: ignore
        if isinstance(b, FieldElement):
            b = Polynomial([b])
        if isinstance(b, Polynomial):
            try:
                d = Polynomial.synchro(self, b)
                if self.deg() == -1 or b.deg() == -1:
                    return Polynomial.zero(self.field)
                prod_coef = []
                prod_deg = self.deg() + b.deg()
                for k in range(prod_deg + 1):
                    coef = FieldElement(self.field, 0)
                    for i in range(max(k - d, 0), min(d, k) + 1):
                        coef += self.coef[i] * b.coef[k - i]
                    prod_coef.append(coef)
                return Polynomial(prod_coef)
            except PolynomialException as e:
                raise PolynomialException(
                    "Error during multiplication of polynomials"
                ) from e
        else:
            raise TypeError(
                "Polynomials can only be multiplied by polynomials or by field elements."
            )

    def __rmul__(self, b: "FieldElement"):
        return self.__mul__(b)

    def __truediv__(self, b: "FieldElement"):
        return self.__mul__(b ** (-1))  # type: ignore

    def __pow__(self, exp: "int") -> "Polynomial":
        if exp == 0:
            return Polynomial.one(self.field)
        res = self
        for _ in range(exp - 1):
            res *= self
        return res

    @classmethod
    def X(cls, field: Field):
        return cls([field.zero, field.one])

    def __call__(self, arg: "Polynomial|FieldElement"):
        if isinstance(arg, Polynomial):
            if self.field != arg.field:
                raise PolynomialException(
                    "The polynomial and its argument must belong linked to the same field."
                )
            comp = Polynomial.zero(self.field)
            for index, coef in enumerate(self.coef):
                comp = comp + (arg**index) * coef
            return comp
        if isinstance(arg, FieldElement):
            if self.field != arg.field:
                raise PolynomialException(
                    "The polynomial and its argument must belong linked to the same field."
                )
            value = self.field.zero
            for index, coef in enumerate(self.coef):
                value += coef * (arg**index)  # type: ignore
            return value
        else:
            raise PolynomialException(
                "TypeError : the argument of the polynomials can only be \
                    a polynomial or a field element."
            )

    def evaluate_domain(self, domain: Domain):
        return [self(ele) for ele in domain.values]

    @staticmethod
    def zero(field: "Field") -> "Polynomial":
        return Polynomial([FieldElement(field, 0)])

    @staticmethod
    def one(field: "Field") -> "Polynomial":
        return Polynomial([FieldElement(field, 1)])

    @staticmethod
    def interpolate(x: "list[FieldElement]", y: "list[FieldElement]") -> "Polynomial":
        n = len(x)
        if n == 0:
            raise PolynomialException(
                "Impossible to interpolate from an empty list of abscissas."
            )
        if len(y) != n:
            raise PolynomialException(
                "Abscissas and ordinates lists must have the same length."
            )
        if not FieldElement.field_eq(x + y):
            raise PolynomialException(
                "Abscissas and ordinates lists must belong to the same field."
            )
        poly = Polynomial.zero(x[0].field)
        for i in range(n):
            product = Polynomial([y[i]])
            for j in range(n):
                if j != i:
                    product *= (Polynomial.X(x[0].field) - Polynomial([x[j]])) / (
                        x[i] - x[j]
                    )
            poly += product
        return poly
    
    @staticmethod
    def divide(numerator: "Polynomial", denominator: "Polynomial") -> tuple["Polynomial", "Polynomial"]:
        # Should only use for MainFieldElement
        if denominator.deg() == -1:
            raise PolynomialException("Cannot divide by zero polynomial")
        if numerator.deg() < denominator.deg():
            return (Polynomial([MainFieldElement(0)]), numerator)
    
        remainder = Polynomial(numerator.coef.copy())
        quotient_coefficients: list[FieldElement] = [MainFieldElement(0) for _ in range(numerator.deg() - denominator.deg() + 1)]
        for _ in range(numerator.deg() - denominator.deg() + 1):
            if remainder.deg() < denominator.deg():
                break
            coefficient = remainder.coef[remainder.deg()] / denominator.coef[denominator.deg()]
            shift = remainder.deg() - denominator.deg()
            subtractee = Polynomial([MainFieldElement(0)] * shift + [coefficient]) * denominator
            quotient_coefficients[shift] = coefficient
            remainder = remainder - subtractee
        quotient = Polynomial(quotient_coefficients)
        return quotient, remainder
    
    def __mod__(self, other: object):
        if not isinstance(other, Polynomial):
            raise PolynomialException(f"only take modulo with another poly")
        
        _, rem = Polynomial.divide(self, other) # type: ignore
        return rem