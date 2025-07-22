from utils.transition import TransitionConstraint
from utils.boundary import BoundaryConstraint
from utils.matrix import Matrix
from utils.domain import Domain
from utils.polynomial import Polynomial
from utils.field import Field, MainFieldElement
class StateMachine():
    
    def __init__(self, transition_constraint: TransitionConstraint, boundary_constraint: BoundaryConstraint, T: int, w: int):

        self.transition = transition_constraint
        self.boundary_constraint = boundary_constraint
        self.T = T
        self.w = w

    def compute_trace(self):
        A = self.transition.transition_matrix
        x = Matrix(self.boundary_constraint.length, 1, self.boundary_constraint.initial_value)
        values = x.values

        for i in range(self.T):
            x = A.dot(x)
            values = values + x.values

        return Matrix(self.T, self.w, values)
    
    def compute_polynomial(self, domain: Domain) -> Polynomial:
        return Polynomial.X(Field.main()) ** 2 + Polynomial([MainFieldElement(1)]) # REWORK WITH proper AIR 