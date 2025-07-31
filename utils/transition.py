from utils.matrix import Matrix
from utils.multivpolynomial import MultiVPolynomial
from utils.field import Field, FieldElement
from utils.domain import Domain
class TransitionConstraint():

    def __init__(self, transition_matrix: Matrix, domain: Domain, field: Field):
        self.transition_matrix = transition_matrix
        self.domain = domain
        self.field = field
        
    