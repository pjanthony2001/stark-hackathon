from utils.field import MainFieldElement, Field, FieldElement
from utils.polynomial import Polynomial
from utils.merkle_tree import Node, MerkleTree
from utils.state_machine_bis import StateMachine

import random
from typing import Self, Callable
import hashlib
from utils.proof_stream import ProofStream


class Domain:
    def __init__ (self, values: list[FieldElement]):
        self.values = values
        self.size = len(values)

    @staticmethod
    def generate_domain(generator: FieldElement, size: int) :
        return Domain([generator ** i for i in range(size)])  # type: ignore (issue with polynomial option)
    
    def map_domain(self, map: Callable[[FieldElement], FieldElement]):
        self.values = [map(ele) for ele in self.values]
        return self 
    
    def offset_domain(self, offset: FieldElement):
        return self.map_domain(lambda x: offset * x)
    
    def sq_domain(self):
        return self.map_domain(lambda x: x * x)
    
    def __len__(self):
        return len(self.values)
    
class ReedSolomonCode:
    def __init__(self, values: list[FieldElement], max_degree: int, domain: Domain):
        self.values = values
        self.max_degree = max_degree
        self.domain = domain
        self.p = None # polynomial
    
    def get_index(self, i: int) -> FieldElement:
        return self.values[i]
    
    def check_poly(self) -> bool:
        self.p = Polynomial.interpolate(self.domain.values, self.values)
        return p.deg() <= max_degree and all(p(x) == values[i] for i, x in enumerate(self.domain.list)), "Values do not interpolate properly." # type: ignore
        
    def poly_eval(self, x: FieldElement) -> FieldElement:
        if self.p == None:
            self.p = Polynomial.interpolate(self.domain.values, self.values)
        
        return self.p(x) # type: ignore
    
    def __len__(self):
        return len(self.values)
    


class GlobalParameters:
    q = Polynomial([MainFieldElement(0), MainFieldElement(0), MainFieldElement(1)]) # Fix q to be X^2
    size_of_group = 2 ** 10 # starting size of group is 1024
    num_rounds = 10 # lg(1024)
    num_colinearity_tests = 10
    g = MainFieldElement(5) # generator
    w = MainFieldElement(2) # offset
    
    hash_function = lambda x: int(hashlib.sha256(x.to_bytes(32, 'big')).hexdigest(), 16) # Hash fun
    combine_hash = lambda x, y: GlobalParameters.hash_function(x) ^ GlobalParameters.hash_function(y)
    
    group_domain = Domain.generate_domain(g, size_of_group)
    coset_domain = group_domain.offset_domain(w)
    
    
    
    
    
class RoundParameters:
    global_ = GlobalParameters
    
    def __init__(self, g: FieldElement, w: FieldElement, size_of_group: int, domain: Domain):
        self.g = g # generator 
        self.w = w # offset
        self.size_of_group = size_of_group # 1024
        self.domain = domain
        
    
    def generate_next_round_parameters(self):
        g = self.g * self.g
        w = self.w * self.w
        size_of_group = self.size_of_group // 2
        domain = self.domain.sq_domain()
        
        return RoundParameters(g, w, size_of_group, domain)
        
        

class Query:
    def __init__(self, a_pair: tuple[FieldElement, FieldElement], b_pair: tuple[FieldElement, FieldElement], c_pair: tuple[FieldElement, FieldElement], 
                proof_a: list[tuple[bool, int]], proof_b: list[tuple[bool, int]], proof_c: list[tuple[bool, int]]):
        
        self.a, self.f_a = a_pair
        self.b, self.f_b = b_pair
        self.c, self.c_f_star = c_pair
        self.proof_a = proof_a
        self.proof_b = proof_b
        self.proof_c = proof_c
        
        def check_query(self, curr_merkle_root, next_merkle_root):
            # Check if the query is valid by verifying the Merkle proofs
            return (curr_merkle_root.verify(self.proof_a, self.a, self.f_a) and 
                    curr_merkle_root.verify(self.proof_b, self.b, self.f_b) and 
                    next_merkle_root.verify(self.proof_c, self.c, self.c_f_star))
        
        
        
class QueryGenerator:
    
    def __init__(self, seed: int, round_parameters: RoundParameters, curr_codeword, next_codeword): 
        self.round_parameters = round_parameters
        self.seed = random.Random(seed)
        self.query_indexes = self.seed.sample(range(self.round_parameters.size_of_group), self.round_parameters.global_.num_colinearity_tests)
        self.query_indexes.sort()
        self.curr_codeword = curr_codeword
        self.next_codeword = next_codeword
    
    
        
    def generate_query(self, alpha, curr_merkle: MerkleTree[int], next_merkle: MerkleTree[int]) -> list[Query]:
        
        res = []
        
        for i in self.query_indexes:
            a = self.round_parameters.w * (self.round_parameters.g ** i) # type: ignore
            f_a  = self.curr_codeword.get_index(i)
            
            b = self.round_parameters.w * (self.round_parameters.g ** (self.round_parameters.size_of_group // 2  + i)) # type: ignore
            f_b = self.curr_codeword.get_index(self.round_parameters.size_of_group // 2  + i)
            
            c = alpha
            c_f_star = self.next_codeword.get_index(2 * i)
            
            proof_a = curr_merkle.get_sibling_path_to_root(i)
            proof_b = curr_merkle.get_sibling_path_to_root(self.round_parameters.size_of_group // 2 + i)
            proof_c = next_merkle.get_sibling_path_to_root(2 * i)
            
            
            query = Query((a, f_a), (b, f_b), (c, c_f_star), proof_a, proof_b, proof_c)
            res.append(query)
            
        return res
        
            

class Round: 
    def __init__(self, merkle_root: int, queries: list[Query], round_parameters: RoundParameters):
        self.round_parameters = round_parameters
        self.merkle_root = merkle_root
        self.queries = queries
        
    @staticmethod
    def generate_next_round(alpha, round_parameters: RoundParameters, curr_codeword: ReedSolomonCode, next_codeword: ReedSolomonCode, curr_merkle: MerkleTree[int], next_merkle: MerkleTree[int]) -> 'Round':
        next_round_parameters = round_parameters.generate_next_round_parameters()
        
        next_merkle_root = next_merkle.get_root().value
        
        query_generator = QueryGenerator(alpha, next_round_parameters, curr_codeword, next_codeword)
        queries = query_generator.generate_query(alpha, curr_merkle, next_merkle)
        
        return Round(next_merkle_root, queries, next_round_parameters)        


class Prover:
    global_params = GlobalParameters
    
    def __init__(self, state_machine: StateMachine) -> None:
        self.state_machine = state_machine
        self.max_degree = 10 # NEED TO FIX ???
        self.composite_poly = state_machine.compute_polynomial(self.global_params.group_domain) # assume boundary and transition constraints are combined into one polynomial
        self.start_codeword_val = self.composite_poly.evaluate_domain(self.global_params.group_domain) # expand by 4 * colinearity for ZK
        self.start_codeword = ReedSolomonCode(self.start_codeword_val, self.max_degree, self.global_params.group_domain) # type: ignore
        
        
    def prove(self, proof_stream: ProofStream):
        curr_codeword = self.start_codeword
        curr_merkle = MerkleTree(curr_codeword.values, self.global_params.combine_hash) # need to check if this works
        curr_round_params = RoundParameters(self.global_params.g, self.global_params.w, self.global_params.size_of_group, self.global_params.group_domain)
        curr_domain = None #TODO: Update this once
        
        proof_stream.push(Round(curr_merkle.get_root().value, [], curr_round_params))
        
        for _ in range(10): #TODO: Check number of Rounds
            alpha = int(proof_stream.prover_communicating()) #TODO: Check proof_stream issues
            next_codeword = self.generate_next_codeword(alpha, curr_codeword, curr_round_params.domain)
            next_merkle = MerkleTree(next_codeword.values, self.global_params.combine_hash)
            
            next_round = Round.generate_next_round(alpha, curr_round_params, curr_codeword, next_codeword, curr_merkle, next_merkle)
        
            proof_stream.push(next_round)
            
            curr_codeword = next_codeword
            curr_merkle = next_merkle
            curr_round_params = next_round.round_parameters
            curr_domain = None #TODO: Update this once
            

    def generate_next_codeword(self, alpha, curr_codeword, curr_domain: Domain):
        N = len(curr_codeword)
        generator = self.global_params.g ** (self.global_params.size_of_group // len(curr_domain))
        two_inv = MainFieldElement(2)**-1
        alpha_omega_i = lambda i: MainFieldElement(alpha) * (generator ** i)
        next_codeword_val = [two_inv * ((MainFieldElement(1) + alpha_omega_i(-i)) * curr_codeword[i] + (MainFieldElement(1) - alpha_omega_i(-i)) * curr_codeword(N // 2 + i)) for i in range(N // 2)]
        
        return ReedSolomonCode(next_codeword_val, curr_codeword.max_degree // 2, curr_domain.sq_domain())