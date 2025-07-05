from utils.field import Field, FieldElement
from utils.matrix import Matrix
from utils.multivpolynomial import MultiVPolynomial

class BoundaryConstraint():

    def __init__(self, initial_value: list[FieldElement], final_value: list[FieldElement]):
        self.initial_value = initial_value
        self.final_value = final_value
        self.length = len(self.initial_value)

    def to_polynomial_initial_constraint(self):
        value = self.initial_value
        n = self.length

        polynomial = {}
        keys = []
        for i in range(n + 1):
            L = (n + 1) * [0]
            L[i + 1] = 1
            keys.append(tuple(L))
        
        for i in range(n):
            polynomial[keys[i + 1]] = - value[i]
        
        polynomial[0] = FieldElement(value[0].field, 1)
        
        return MultiVPolynomial(polynomial)