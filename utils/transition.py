from utils.state_machine import StateMachine
from utils.matrix import Matrix
from utils.multivpolynomial import MultiVPolynomial
from utils.field import Field, FieldElement

class TransitionConstraint():

    def __init__(self, transition_matrix: 'Matrix'):
        self.transition_matrix = transition_matrix

    def to_polynomial(self):
        A = self.transition_matrix
        n = A.rows

        polynomials = []
        
        for j in range(n):
            keys = []
            for i in range(n + 1):
                L = [0] * (n + 1)
                L[i] = 1
                keys.append(tuple(L))
            
            dict_P_j = {}
            for k in range(A.columns):
                dict_P_j[keys[k + 1]] = - A[j][k]
            dict_P_j[keys[0]] = FieldElement(A[0][0].field(), 1)

            P_j = MultiVPolynomial(dict_P_j)
            polynomials.append(P_j)
        
        return polynomials