from utils.field import MainFieldElement, FieldElement
from utils.polynomial import Polynomial
from utils.merkle_tree import MerkleTree
from utils.state_machine import StateMachine

import random
from typing import Callable
import hashlib
from utils.proof_stream import ProofStream
from utils.domain import Domain

class ReedSolomonCode:
    def __init__(self, values: list[FieldElement], max_degree: int, domain: Domain):
        self.values = values
        self.max_degree = max_degree
        self.domain = domain
        self.p = None  # polynomial

    def get_index(self, i: int) -> FieldElement:
        return self.values[i]

    def check_poly(self) -> bool:
        self.p = Polynomial.interpolate(self.domain.values, self.values)
        return self.p.deg() <= self.max_degree and all(self.p(x) == self.values[i] for i, x in enumerate(self.domain.list)), "Values do not interpolate properly."  # type: ignore

    def poly_eval(self, x: FieldElement) -> FieldElement:
        if self.p == None:
            self.p = Polynomial.interpolate(self.domain.values, self.values)

        return self.p(x)  # type: ignore

    def __len__(self):
        return len(self.values)
    
    def __getitem__(self, index: int) -> FieldElement:
        if index < 0 or index >= len(self.values):
            raise IndexError("Index out of bounds for ReedSolomonCode.")
        return self.values[index]
    
    
class GlobalParameters:
    q = Polynomial(
        [MainFieldElement(0), MainFieldElement(0), MainFieldElement(1)]
    )  # Fix q to be X^2
    size_of_group = 2**10  # starting size of group is 1024
    num_rounds = 10  # lg(1024)
    num_colinearity_tests = 10
    g = MainFieldElement(5)  # generator
    w = MainFieldElement(2)  # offset

    combine_hash = lambda x, y: GlobalParameters.hash_function(
        x
    ) ^ GlobalParameters.hash_function(y)

    group_domain = Domain.generate_domain(g, size_of_group)
    coset_domain = group_domain.offset_domain(w)
    
    @staticmethod
    def hash_function(x: FieldElement | int) -> int:
        if isinstance(x, FieldElement):
            x = x.value
        return int(hashlib.sha256(x.to_bytes(32, "big")).hexdigest(), 16)



class Query:
    def __init__(
        self,
        a_pair: tuple[FieldElement, FieldElement],
        b_pair: tuple[FieldElement, FieldElement],
        c_pair: tuple[FieldElement, FieldElement],
        proof_a: list[tuple[bool, int]],
        proof_b: list[tuple[bool, int]],
        proof_c: list[tuple[bool, int]],
    ):

        self.a, self.f_a = a_pair
        self.b, self.f_b = b_pair
        self.c, self.c_f_star = c_pair
        self.proof_a = proof_a
        self.proof_b = proof_b
        self.proof_c = proof_c

        def check_query(self, curr_merkle_root, next_merkle_root):
            # Check if the query is valid by verifying the Merkle proofs
            return (
                curr_merkle_root.verify(self.proof_a, self.a, self.f_a)
                and curr_merkle_root.verify(self.proof_b, self.b, self.f_b)
                and next_merkle_root.verify(self.proof_c, self.c, self.c_f_star)
            )


class QueryGenerator:
    

    def __init__(
        self, seed: int, curr_codeword, next_codeword
    ):
        self.seed = random.Random(seed)
        num_to_sample = min(len(next_codeword.domain), GlobalParameters.num_colinearity_tests)
        self.query_indexes = self.seed.sample(
            range(len(next_codeword.domain)),
            num_to_sample,
        ) # sampling from 0 to N // 2 - 1
        
        
        self.query_indexes.sort()
        self.curr_codeword = curr_codeword
        self.next_codeword = next_codeword

    def generate_query(
        self, alpha, curr_merkle: MerkleTree[int], next_merkle: MerkleTree[int]
    ) -> list[Query]:

        res = []
        N = len(self.curr_codeword.domain)
        
        for i in self.query_indexes:
            a = self.curr_codeword.domain.values[i]  # type: ignore
            f_a = self.curr_codeword.get_index(i)

            print(i, N // 2 + i, N)
            
            b = self.curr_codeword.domain.values[N // 2 + i]  # type: ignore
            f_b = self.curr_codeword.get_index(
                N // 2 + i
            )

            c = a * a
            c_f_star = self.next_codeword.get_index(i)
            
            # CHECK COLINEARITY FOR GODS SAKE
            two_inv = MainFieldElement(2) ** -1
            a_inv = a ** -1
            c_f_star_expected = two_inv * (
                (f_a + f_b) + alpha * (f_a - f_b) * (a_inv)
            )  # type: ignore
            
            print(f"c_f_star_expected: {c_f_star_expected}, c_f_star: {c_f_star}")

            proof_a = curr_merkle.get_sibling_path_to_root(i)
            proof_b = curr_merkle.get_sibling_path_to_root(
                N // 2 + i
            )
            proof_c = next_merkle.get_sibling_path_to_root(i)

            query = Query((a, f_a), (b, f_b), (c, c_f_star), proof_a, proof_b, proof_c)
            res.append(query)

        return res


class Round:
    def __init__(
        self, merkle_root: int, queries: list[Query]):
        self.merkle_root = merkle_root
        self.queries = queries

    @staticmethod
    def generate_next_round(
        alpha,
        curr_codeword: ReedSolomonCode,
        next_codeword: ReedSolomonCode,
        curr_merkle: MerkleTree[int],
        next_merkle: MerkleTree[int],
    ) -> "Round":

        next_merkle_root = next_merkle.get_root().value

        query_generator = QueryGenerator(
            alpha.value, curr_codeword, next_codeword
        )
        queries = query_generator.generate_query(alpha, curr_merkle, next_merkle)

        return Round(next_merkle_root, queries)


class Prover:
    global_params = GlobalParameters

    def __init__(self, state_machine: StateMachine) -> None:
        self.state_machine = state_machine
        self.max_degree = 10  # NEED TO FIX ???
        self.composite_poly = state_machine.compute_polynomial(
            self.global_params.group_domain
        )  # assume boundary and transition constraints are combined into one polynomial
        self.start_codeword_val = self.composite_poly.evaluate_domain(
            self.global_params.group_domain
        )  # expand by 4 * colinearity for ZK
        self.start_codeword = ReedSolomonCode(self.start_codeword_val, self.max_degree, self.global_params.group_domain)  # type: ignore

    def prove(self, proof_stream: ProofStream):
        curr_codeword = self.start_codeword
        curr_merkle = MerkleTree(
            curr_codeword.values, self.global_params.combine_hash
        )  # need to check if this works
        curr_domain = None  # TODO: Update this once

        proof_stream.push(Round(curr_merkle.get_root().value, []))
        for _ in range(10):  # TODO: Check number of Rounds
            alpha = int.from_bytes(proof_stream.prover_communicating(), 'big') # TODO: Check proof_stream issues
            alpha = MainFieldElement(alpha)
            next_codeword = self.generate_next_codeword(
                alpha, curr_codeword, curr_codeword.domain
            )
            next_merkle = MerkleTree(
                next_codeword.values, self.global_params.combine_hash
            )

            next_round = Round.generate_next_round(
                alpha,
                curr_codeword,
                next_codeword,
                curr_merkle,
                next_merkle,
            )

            proof_stream.push(next_round)

            curr_codeword = next_codeword
            curr_merkle = next_merkle
            curr_domain = None  # TODO: Update this once
            
        proof_stream.push(curr_codeword.values)

    def generate_next_codeword(self, alpha: FieldElement, curr_codeword: ReedSolomonCode, curr_domain: Domain) -> ReedSolomonCode:
        n = len(curr_codeword)
        two_inv = MainFieldElement(2) ** -1
        
        next_codeword_val = []
        for i in range(n // 2):
            x = curr_domain.values[i]
            f_x = curr_codeword[i]
            f_minus_x = curr_codeword[i + n // 2]
            
            val = two_inv * ((f_x + f_minus_x) + alpha * (f_x - f_minus_x) * (x ** -1)) #type: ignore
            next_codeword_val.append(val)
        
        next_domain = curr_domain.sq_domain()
        next_max_degree = curr_codeword.max_degree // 2
        
        return ReedSolomonCode(next_codeword_val, next_max_degree, next_domain)


class Verifier:
    global_params = GlobalParameters
    
    def __init__(self, max_degree: int):
        self.max_degree = max_degree

    def verify(self, proof_stream: ProofStream) -> bool:
        rounds: list[Round] = [proof_stream.pull() for _ in range(self.global_params.num_rounds + 1)] # type: ignore
        final_codeword_values: list = proof_stream.pull() #type: ignore
        if not all(isinstance(r, Round) for r in rounds):
            return False

        # Phase 2: Re-derive all challenges.
        alphas = []
        challenge_ps = ProofStream()
        for i in range(self.global_params.num_rounds):
            challenge_ps.push(rounds[i])
            alpha_bytes = challenge_ps.prover_communicating()
            alpha = MainFieldElement(int.from_bytes(alpha_bytes))
            alphas.append(alpha)
            _ = challenge_ps.prover_communicating()
        
        for i in range(self.global_params.num_rounds - 1):
            prev_round = rounds[i]
            curr_round = rounds[i+1]
            alpha = alphas[i]
            
            if not curr_round.queries:
                return False

            for query in curr_round.queries:
                proof_a_valid = MerkleTree.verify_path(query.f_a.value, query.proof_a, prev_round.merkle_root, self.global_params.combine_hash)
                proof_b_valid = MerkleTree.verify_path(query.f_b.value, query.proof_b, prev_round.merkle_root, self.global_params.combine_hash)
                proof_c_valid = MerkleTree.verify_path(query.c_f_star.value, query.proof_c, curr_round.merkle_root, self.global_params.combine_hash)
                
                if not (proof_a_valid and proof_b_valid and proof_c_valid):
                    return False

                two_inv = MainFieldElement(2) ** -1
                f_a, f_b, a = query.f_a, query.f_b, query.a
                expected_c_f_star = two_inv * ((f_a + f_b) + alpha * (f_a - f_b) * (a ** -1))
                if expected_c_f_star != query.c_f_star:
                    return False
        
        final_domain_size = len(final_codeword_values)
        if final_domain_size == 0:
            return False

        final_g = self.global_params.g ** (2 ** self.global_params.num_rounds)
        final_domain = Domain.generate_domain(final_g, final_domain_size)
        
        final_poly = Polynomial.interpolate(final_domain.values, final_codeword_values)
        print(f"Final polynomial: {final_poly}")
        
        expected_degree = self.max_degree // (2 ** self.global_params.num_rounds)
        
        if final_poly.deg() > expected_degree:
            return False
            
        return True

if __name__ == "__main__":
    state_machine = StateMachine(None, None, 10, 1) # type: ignore
    # this proves to verifier that that the polynomial is X
    max_degree = 10

    prover = Prover(state_machine)
    prover.max_degree = max_degree  # Set the degree bound

    proof_stream = ProofStream()

    prover.prove(proof_stream)

    proof_bytes = proof_stream.serialization()
    print(f"Total proof size: {len(proof_bytes)} bytes.")

    verifier = Verifier(max_degree)

    is_valid = verifier.verify(proof_stream)

    assert is_valid, "The FRI proof did not pass verification."
