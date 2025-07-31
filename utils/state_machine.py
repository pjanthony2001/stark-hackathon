from utils.transition import TransitionConstraint
from utils.boundary import BoundaryConstraint
from utils.matrix import Matrix, Vector
from utils.domain import Domain
from utils.polynomial import Polynomial
from utils.field import Field, MainFieldElement, FieldElement


from utils.params import GlobalParameters


def ntt(coeffs: list[FieldElement], generator: FieldElement) -> list[FieldElement]:
    n = len(coeffs)

    # n must be a power of two.
    if n > 0 and (n & (n - 1)) != 0:
        raise ValueError("Length of coefficients list must be a power of two.")

    if n <= 1:
        return coeffs

    even_coeffs = coeffs[0::2]
    odd_coeffs = coeffs[1::2]

    generator_sq = generator**2

    ntt_even = ntt(even_coeffs, generator_sq)
    ntt_odd = ntt(odd_coeffs, generator_sq)

    return [
        ntt_even[i % (n // 2)] + (generator**i) * ntt_odd[i % (n // 2)]
        for i in range(n)
    ]


def intt(evals: list[FieldElement], generator: FieldElement) -> list[FieldElement]:

    n = len(evals)

    generator_inv = generator**-1

    coeffs_unscaled = ntt(evals, generator_inv)

    n_inv = MainFieldElement(n) ** -1

    coeffs = [(c * n_inv) for c in coeffs_unscaled]

    return coeffs

def primitive_root_check(primitive_root, root_order):
    return (primitive_root ** root_order == MainFieldElement(1)) and (primitive_root ** (root_order//2) != MainFieldElement(1))


def fast_multiply(lhs_poly: Polynomial, rhs_poly: Polynomial, primitive_root: FieldElement, root_order: int) -> Polynomial:
    assert primitive_root_check(primitive_root, root_order), "Issues with primitive root given for fast_multiply"

    if lhs_poly.is_zero() or lhs_poly.is_zero():
        return Polynomial([])

    max_degree = lhs_poly.deg() + rhs_poly.deg()

    if max_degree < 8:
        return lhs_poly * rhs_poly

    
    generator = primitive_root
    while max_degree < root_order // 2:
        generator = generator ** 2
        root_order = root_order // 2

    lhs_coefficients = lhs_poly.coef[:(lhs_poly.deg()+1)] #TODO: Should rectify with Synchro
    while len(lhs_coefficients) < root_order:
        lhs_coefficients += [MainFieldElement(0)]
    rhs_coefficients = rhs_poly.coef[:(rhs_poly.deg()+1)]  #TODO: Should rectify with Synchro
    while len(rhs_coefficients) < root_order:
        rhs_coefficients += [MainFieldElement(0)]

    lhs_codeword = ntt(lhs_coefficients, generator)
    rhs_codeword = ntt(rhs_coefficients, generator)

    product_in_eval_space = [l * r for (l, r) in zip(lhs_codeword, rhs_codeword)]

    product_poly_coefficients = intt(product_in_eval_space, generator)
    return Polynomial(product_poly_coefficients[0:(max_degree+1)]) # TODO: Should fix this with synchro


# TODO: Implement modulo division for polynomials 



def fast_zerofier(domain, primitive_root, root_order):
    assert primitive_root_check(primitive_root, root_order), "Issues with primitive root given for fast_zerofier"

    if len(domain) == 0:
        return Polynomial([])

    if len(domain) == 1:
        return Polynomial([-domain[0], MainFieldElement(1)])

    half = len(domain) // 2

    left = fast_zerofier(domain[:half], primitive_root, root_order)
    right = fast_zerofier(domain[half:], primitive_root, root_order)
    return fast_multiply(left, right, primitive_root, root_order)

def fast_evaluate(polynomial: Polynomial, domain: list[FieldElement], primitive_root, root_order ):
    assert primitive_root_check(primitive_root, root_order), "Issues with primitive root given for fast_evaluate"

    if len(domain) == 0:
        return []

    if len(domain) == 1:
        return [polynomial(domain[0])]

    half = len(domain) // 2

    left_zerofier = fast_zerofier(domain[:half], primitive_root, root_order)
    right_zerofier = fast_zerofier(domain[half:], primitive_root, root_order)

    left = fast_evaluate(polynomial % left_zerofier, domain[:half], primitive_root, root_order)
    right = fast_evaluate(polynomial % right_zerofier, domain[half:], primitive_root, root_order)

    return left + right


class StateMachine:
    def __init__(
        self, transition_matrix: "Matrix", init_vector: "Vector", T: int, domain: Domain
    ):
        self.transition_matrix = transition_matrix
        self.init_vector = init_vector
        self.T = T
        self.w = len(self.init_vector.values)
        self.domain = domain
        self.small_domain = domain
        while self.T < len(self.small_domain) // 2:
            print("SQ DOMAIN")
            self.small_domain = self.small_domain.sq_domain()  # Blowup factor of 4

        assert T < len(self.small_domain)
        assert self.transition_matrix.is_square()
        assert (
            self.transition_matrix.columns == self.init_vector.rows
        ), "Transition matrix columns must match initial vector rows."

    def compute_trace(self):
        curr_vector: "Matrix" = self.init_vector
        computation_trace: list[list[FieldElement]] = [curr_vector.values]

        for _ in range(1, self.T):
            curr_vector = self.transition_matrix.dot(curr_vector)
            computation_trace.append(curr_vector.values)

        assert len(computation_trace) == self.T
        return computation_trace

    def compute_trace_polynomials(self, computation_trace: list[list[FieldElement]]):

        registers = [
            [computation_trace[i][j] for i in range(self.T)] for j in range(self.w)
        ]
        
        return [
            Polynomial.interpolate(self.small_domain.values[:self.T], registers[i])
            for i in range(self.w)
        ]

    def trace_poly_lde(self, trace_polynomials: list[Polynomial]):
        result = []
        for trace_poly in trace_polynomials:
            trace_poly_lde = fast_evaluate(trace_poly, self.domain.values, self.domain.generator, len(self.domain))
            result.append(trace_poly_lde)
        return result
        
    def transition_poly(self, trace_polynomials: list[Polynomial]):
        # For each w_i = (TRACE[i][0], TRACE[i][1], ... TRACE[i][|w|-1]) where |w| is num registers
        # All the math on the whiteboard
        
        transition_polynomials = []
        generator_small_domain = self.small_domain.generator
        for j, row in enumerate(self.transition_matrix.matrix):
            dot_pdt = sum([trace_poly * scalar for scalar, trace_poly in zip(row, trace_polynomials)], Polynomial([MainFieldElement(0)]))
            print(type(generator_small_domain), type(Polynomial.X(Field.main())))
            t_j_o_times_x = trace_polynomials[j](Polynomial.X(Field.main()) * generator_small_domain)
            transition_polynomials.append(dot_pdt - t_j_o_times_x)
        return transition_polynomials
            
    def boundary_poly(self, boundary_registers_times, trace_polynomials: list[Polynomial], computation_trace: list[list[FieldElement]]):
        # For now just take the register_ of the computation to be used as boundaries
        boundary_polynomials = []
        for register, time in boundary_registers_times:
            boundary_polynomials.append(trace_polynomials[register] - computation_trace[time][register])
        return boundary_polynomials
    
    
    def boundary_zerofier(self, boundary_registers_times, trace_polynomials: list[Polynomial], computation_trace: list[list[FieldElement]]):
        pass
    
    def generate_AIR_polynomials(self, boundary_registers_times):
        computation_trace = self.compute_trace()
        trace_polynomials = self.compute_trace_polynomials(computation_trace)
        
        transition_polynomials = self.transition_poly(trace_polynomials)
        boundary_polynomials = self.boundary_poly(boundary_registers_times, trace_polynomials, computation_trace)
        
        boundary_zerofier = None


if __name__ == "__main__":
    
    # --- A. SETUP ---
    
    # Fibonacci: state is [a_{i-1}, a_i]. Next state is [a_i, a_{i-1}+a_i].
    # This corresponds to the transition matrix M = [[0, 1], [1, 1]].
    fib_matrix = Matrix(2, 2, [MainFieldElement(0), MainFieldElement(1), MainFieldElement(1), MainFieldElement(1)])
    
    # Initial state [a_0, a_1] = [1, 1]
    init_vector = Vector(2, [MainFieldElement(1), MainFieldElement(1)])
    
    # We want to compute 8 steps of the sequence.
    TRACE_LENGTH = 8
    
    # The LDE domain must be larger. Let's use a blowup factor of 4.
    LDE_DOMAIN_SIZE = TRACE_LENGTH * 4
    lde_domain = GlobalParameters.group_domain
    
    # Instantiate the state machine
    sm = StateMachine(fib_matrix, init_vector, TRACE_LENGTH, lde_domain)

    # --- B. EXECUTE WORKFLOW ---
    
    # 1. Compute the raw execution trace
    print("HERE")
    trace = sm.compute_trace()
    print("  Trace (first 5 rows):")
    for i in range(min(5, len(trace))):
        print(f"    Time {i}: {[fe.value for fe in trace[i]]}")

    # 2. Get the trace polynomials
    trace_polys = sm.compute_trace_polynomials(trace)
    print(f"  - Generated {len(trace_polys)} trace polynomials.")
    print(f"    P_0(x) = {trace_polys[0]}")
    print(f"    P_1(x) = {trace_polys[1]}")

    # 3. Get the LDE of the trace polynomials
    trace_ldes = sm.trace_poly_lde(trace_polys)
    print(f"  - Generated {len(trace_ldes)} LDEs, each of size {len(trace_ldes[0])}.")

    # 4. Get the transition constraint polynomials
    transition_polys = sm.transition_poly(trace_polys)
    print(f"  - Generated {len(transition_polys)} transition constraint polynomials.")
    print(f"    Transition 0: {transition_polys[0]}")
    print(f"    Transition 1: {transition_polys[1]}")

    # 5. Get the boundary constraint polynomials
    # Let's enforce that the start values are correct.
    # Constraint 1: Register 0 at time 0 must be 1.
    # Constraint 2: Register 1 at time 0 must be 1.
    boundary_definitions = [(0, 0), (1, 0)] 
    boundary_polys = sm.boundary_poly(boundary_definitions, trace_polys, trace)
    print(f"  - Generated {len(boundary_polys)} boundary constraint polynomials.")
    print(f"    Boundary 0: {boundary_polys[0]}")
    print(f"    Boundary 1: {boundary_polys[1]}")

    print("\nWorkflow demonstration complete.")