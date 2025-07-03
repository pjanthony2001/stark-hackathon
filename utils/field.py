
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
        if isinstance(b, FieldElement) :
            try :
                return self.field.add(self, b)
            except Exception as e :
                print (e)
        else :
            return NotImplemented
    
    def __sub__(self, b : 'FieldElement') -> 'FieldElement' :
        if isinstance(b, FieldElement) :
            try :
                return self.field.sub(self, b)
            except Exception as e :
                print (e)
        else :
            return NotImplemented
    
    def __mul__(self, b : 'FieldElement') -> 'FieldElement' :
        if isinstance(b, FieldElement) :
            try :
                return self.field.mul(self, b)
            except Exception as e :
                print (e)
        else :
            return NotImplemented

    def __pow__(self, exp : 'int') -> 'FieldElement' :
        try :
            return self.field.power(self, exp)
        except Exception as e :
            print (e)

    def __truediv__(self, b : 'FieldElement') -> 'FieldElement' :
        try :
            return self.field.truediv(self)
        except Exception as e :
            print (e)

    def __neg__(self) -> 'FieldElement' :
        return FieldElement(self.field, -self.value)
    
    def inverse(self) -> 'FieldElement' :
        return 1/self
    
    def is_zero(self) -> 'bool' :
        return self.value == 0
    
    @staticmethod
    def field_eq(elts : 'list[FieldElement]') -> 'bool' :
        if len(elts) > 0 :
            for elt in elts[1:] :
                if elt.field != elts[0].field :
                    return False
        return True

class Field :

    def __init__(self, p : 'int') :
        self.p = p
        self.zero = FieldElement(self, 0)
        self.one = FieldElement(self, 1)
    
    def __eq__(self, field2 : 'Field') :
        return self.p == field2.p
    
    def __neq__(self, field2 : 'Field') :
        return self.p != field2.p
    
    def __repr__(self):
        return f'Z/{self.p}Z'
    
    def mod(self, value) :
        return value % self.p

    def add(self, a : 'FieldElement', b : 'FieldElement') -> 'FieldElement' :
        if a.field != b.field :
            raise Exception('Operations between terms from different fields are prohibited.')
        return FieldElement(self, (a.value + b.value) % self.p)
    
    def sub(self, a : 'FieldElement', b : 'FieldElement') -> 'FieldElement' :
        if a.field != b.field :
            raise Exception('Operations between terms from different fields are prohibited.')
        return FieldElement(self, (a.value - b.value) % self.p)

    def mul(self, a : 'FieldElement', b : 'FieldElement') -> 'FieldElement' :
        if a.field != b.field :
            raise Exception('Operations between terms from different fields are prohibited.')
        return FieldElement(self, (a.value*b.value) % self.p)
    
    def power(self, a : 'FieldElement', exp : 'int') -> 'FieldElement' :
        if exp == 0 :
            return self.one
        if exp == 1 :
            return a
        b = FieldElement(self, (a.value**2) % self.p)
        return self.power(b, exp//2)*self.power(a, exp%2)

    def truediv(self, a : 'FieldElement', b : 'FieldElement') -> 'FieldElement' :
        if a.field != b.field :
            raise Exception('Operations between terms from different fields are prohibited.')
        if b.is_zero() :
            raise Exception('Division by zero.')
        return FieldElement(self, (b.value * a.value**(self.p-1)) % self.p)
    
    def repr_element(self, a : 'FieldElement') -> 'str' :
        return f'{a.value} in {self}'
    
    def generator(self):
        assert(self.p == 1 + 407 * ( 1 << 119 )), "Do not know generator for other fields beyond 1+407*2^119"
        return FieldElement(self, 85408008396924667383611388730472331217)
        
    def primitive_nth_root(self, n):
        if self.p == 1 + 407 * ( 1 << 119 ):
            assert(n <= 1 << 119 and (n & (n-1)) == 0), "Field does not have nth root of unity where n > 2^119 or not power of two."
            root = FieldElement(self, 85408008396924667383611388730472331217)
            order = 1 << 119
            while order != n:
                root = root^2
                order = order/2
            return root
        else:
            assert(False), "Unknown field, can't return root of unity."
    
    @classmethod
    def main(cls):
        p = 1 + 407 * ( 1 << 119 ) # 1 + 11 * 37 * 2^119
        return cls(p)
