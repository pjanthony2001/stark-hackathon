
class FieldElement :

    def __init__(self, field : 'Field', value : 'int'):
        self.field = field
        self.value = self.field.mod(value)
    
    def __eq__(self, b : 'FieldElement'):
        return self.field == b.field * self.value == b.value
    
    def __neq__(self, b : 'FieldElement'):
        return 1 - self.__eq__(b)

    def __repr__(self):
        return self.field.repr_element(self)

    def __str__(self):
        return f'{self.value}'

    def __add__(self, b : 'FieldElement') -> 'FieldElement' :
        assert self.field == b.field
        return self.field.add(self, b)
    
    def __sub__(self, b : 'FieldElement') -> 'FieldElement' :
        assert self.field == b.field
        return self.field.sub(self, b)
    
    def __mul__(self, b : 'FieldElement') -> 'FieldElement' :
        assert self.field == b.field
        return self.field.mul(self, b)

    def __power__(self, exp : 'int') -> 'FieldElement' :
        assert exp >= 0
        return self.field.power(self, exp)
    
    def __truediv__(self, b : 'FieldElement') -> 'FieldElement' :
        assert self.field == b.field
        assert not b.is_zero()
        return self.field.truediv(self)
    
    def __neg__(self) -> 'FieldElement' :
        return FieldElement(self.field, -self.value)
    
    def inverse(self) -> 'FieldElement' :
        return 1/self
    
    def is_zero(self) -> 'bool' :
        return self == 0

class Field :

    def __init__(self, p : 'int') :
        self.p = p
        self.zero = FieldElement(self, 0)
        self.one = FieldElement(self, 1)
    
    def __eq__(self, field2 : 'Field') :
        return self.p == field2.p
    
    def __repr__(self):
        return f'Z/{self.p}Z'
    
    def mod(self, value) :
        return value % self.p

    def add(self, a : 'FieldElement', b : 'FieldElement') -> 'FieldElement' :
        return FieldElement((a.value + b.value) % self.p)
    
    def sub(self, a : 'FieldElement', b : 'FieldElement') -> 'FieldElement' :
        return FieldElement((a.value - b.value) % self.p)

    def mul(self, a : 'FieldElement', b : 'FieldElement') -> 'FieldElement' :
        return FieldElement((a.value*b.value) % self.p)
    
    def power(self, a : 'FieldElement', exp : 'int') -> 'FieldElement' :
        if exp == 1 :
            return a
        b = FieldElement(self, (a.value**2) % self.p)
        return self.power(b, exp//2 + exp%2) 

    def truediv(self, a : 'FieldElement', b : 'FieldElement') -> 'FieldElement' :
        return FieldElement((b.value * a.value**(self.p-1)) % self.p)
    
    def repr_element(self, a : 'FieldElement') -> 'str' :
        return f'{a.value} in {self}'

