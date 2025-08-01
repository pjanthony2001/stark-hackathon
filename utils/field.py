
class FieldException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"FieldException: {self.message}"


class FieldElement:

    def __init__(self, field: "Field", value: "int"):
        self.field = field
        self.value = self.field.mod(value)

    def __eq__(self, b: object) -> "bool":
        if not isinstance(b, FieldElement):
            return False
        return self.field == b.field and self.value == b.value

    def __repr__(self):
        return self.field.repr_element(self)

    def __str__(self):
        return f"{self.value}"

    def __add__(self, b: "FieldElement") -> "FieldElement":
        if isinstance(b, FieldElement):
            return self.field.add(self, b)

        raise FieldException(
            "Addition is only defined between two FieldElement instances."
        )

    def __sub__(self, b: "FieldElement") -> "FieldElement":
        if isinstance(b, FieldElement):
            return self.field.sub(self, b)
        
        raise FieldException(
            "Subtraction is only defined between two FieldElement instances.")

    def __mul__(self, b: "FieldElement") -> "FieldElement":
        if isinstance(b, FieldElement):
            return self.field.mul(self, b)
        else:
            raise FieldException(
                "Multiplication is only defined between two FieldElement instances."
            )

    def __pow__(self, exp: "int") -> "FieldElement":
        return self.field.pow(self, exp)


    def __truediv__(self, b: "FieldElement") -> "FieldElement":
        return self.field.truediv(self, b)  # type: ignore


    def __neg__(self) -> "FieldElement":
        return FieldElement(self.field, -self.value)

    def is_zero(self) -> "bool":
        return self.value == 0

    @staticmethod
    def field_eq(elts: "list[FieldElement]") -> "bool":
        if len(elts) > 0:
            for elt in elts[1:]:
                if elt.field != elts[0].field:
                    return False
        return True


class Field:

    def __init__(self, p: "int"):
        self.p = p
        self.zero = FieldElement(self, 0)
        self.one = FieldElement(self, 1)

    def __eq__(self, field2: object):
        if not isinstance(field2, Field):
            return False
        return self.p == field2.p

    def __neq__(self, field2: "Field"):
        return self.p != field2.p

    def __repr__(self):
        return f"Z/{self.p}Z"

    def mod(self, value):
        return value % self.p

    def add(self, a: "FieldElement", b: "FieldElement") -> "FieldElement":
        if a.field != b.field:
            raise FieldException(
                "Operations between terms from different fields are prohibited."
            )
        return FieldElement(self, (a.value + b.value) % self.p)

    def sub(self, a: "FieldElement", b: "FieldElement") -> "FieldElement":
        if a.field != b.field:
            raise FieldException(
                "Operations between terms from different fields are prohibited."
            )
        return FieldElement(self, (a.value - b.value) % self.p)

    def mul(self, a: "FieldElement", b: "FieldElement") -> "FieldElement":
        if a.field != b.field:
            raise FieldException(
                "Operations between terms from different fields are prohibited."
            )
        return FieldElement(self, (a.value * b.value) % self.p)

    def pow(self, a: "FieldElement", exp: "int") -> "FieldElement":
        if exp == -1:
            return a ** int(self.p - 2)
        if exp == 0:
            return self.one
        if exp == 1:
            return a
        b = FieldElement(self, (a.value**2) % self.p)
        return self.pow(b, exp // 2) * self.pow(a, exp % 2)

    def truediv(self, a: "FieldElement", b: "FieldElement") -> "FieldElement":
        if a.field != b.field:
            raise FieldException(
                "Operations between terms from different fields are prohibited."
            )
        if b.is_zero():
            raise FieldException("Division by zero.")
        assert isinstance(b, FieldElement)
        return self.mul(a, b ** - 1)

    def repr_element(self, a: "FieldElement") -> "str":
        return f"{a.value} in {self}"

    def generator(self):
        assert self.p == 1 + 407 * (
            1 << 119
        ), "Do not know generator for other fields beyond 1+407*2^119"
        return FieldElement(self, 85408008396924667383611388730472331217)

    def primitive_nth_root(self, n):
        if self.p == 1 + 407 * (1 << 119):
            assert (
                n <= 1 << 119 and (n & (n - 1)) == 0
            ), "Field does not have nth root of unity where n > 2^119 or not power of two."
            root = FieldElement(self, 85408008396924667383611388730472331217)
            order = 1 << 119
            while order != n:
                root = root**2  # type: ignore
                order = order / 2
            return root
        else:
            assert False, "Unknown field, can't return root of unity."

    @classmethod
    def main(cls):
        p = 1 + 407 * (1 << 119)  # 1 + 11 * 37 * 2^119
        return cls(p)


class MainFieldElement(FieldElement):
    def __init__(self, p: int):
        super().__init__(Field.main(), p)
