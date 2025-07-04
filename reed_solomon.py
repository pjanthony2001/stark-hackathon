from utils.field import MainFieldElement, Field, FieldElement
from utils.polynomial import Polynomial
from utils.merkle_tree import Node, MerkleTree


import random
from typing import Self
import hashlib


class Domain:
    def __init__ (self, list: list[FieldElement]):
        self.list = list
        self.size = len(list)


class ReedSolomonCode:
    def __init__(self, values: list[FieldElement], max_degree: int, domain: Domain):
        self.values = values
        self.max_degree = max_degree
        self.domain = domain
        self.p = None
    
    def get_index(self, i: int) -> FieldElement:
        return self.values[i]
    
    def check_poly(self) -> bool:
        self.p = Polynomial.interpolate(self.domain.list, self.values)
        return p.deg() <= max_degree and all(p(x) == values[i] for i, x in enumerate(self.domain.list)), "Values do not interpolate correctly" # type: ignore
        
    def poly_eval(self, x: FieldElement) -> FieldElement:
        if self.p == None:
            self.p = Polynomial.interpolate(self.domain.list, self.values)
        
        return self.p(x) # type: ignore
    


class GlobalParameters:
    q = Polynomial([MainFieldElement(0), MainFieldElement(0), MainFieldElement(1)]) # Fix q to be X^2
    size_of_group = 2 ** 10 # starting size of group is 1024
    num_colinearity_tests = 10
    g = MainFieldElement(5) 
    w = MainFieldElement(2)
    
    hash_function = lambda x: int(hashlib.sha256(x.to_bytes(32, 'big')).hexdigest(), 16) # Hash fun
    combine_hash = lambda x, y: GlobalParameters.hash_function(x) ^ GlobalParameters.hash_function(y)
    
    
    
class RoundParameters:
    global_ = GlobalParameters
    
    def __init__(self, g: FieldElement, w: FieldElement, size_of_group: int):
        self.g = g # generator 
        self.w = w # offset
        self.size_of_group = 2 ** 10 # 1024
        
    
    def generate_next_round_parameters(self):
        g = self.g * self.g
        w = self.w * self.w
        size_of_group = self.size_of_group // 2
        
        return RoundParameters(g, w, size_of_group)
        
        

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
    
    
        
    def generate_query(self, alpha, curr_codeword: ReedSolomonCode, next_codeword: ReedSolomonCode, curr_merkle: MerkleTree[int], next_merkle: MerkleTree[int]) -> list[Query]:
        
        res = []
        
        for i in self.query_indexes:
            a = self.round_parameters.w * (self.round_parameters.g ** i)
            f_a  = curr_codeword.get_index(i)
            
            b = self.round_parameters.w * (self.round_parameters.g ** (self.round_parameters.size_of_group // 2  + i))
            f_b = curr_codeword.get_index(self.round_parameters.size_of_group // 2  + i)
            
            c = alpha
            c_f_star = next_codeword.get_index(2 * i)
            
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
        
    def generate_next_round(self, curr_codeword: ReedSolomonCode, next_codeword: ReedSolomonCode) -> 'Round':
        next_round_parameters = self.round_parameters.generate_next_round_parameters()
        
        next_merkle = MerkleTree([x.value for x in next_codeword.values], self.round_parameters.global_.combine_hash)
        next_merkle_root = next_merkle.get_root().value
        curr_merkle = MerkleTree([x.value for x in curr_codeword.values], self.round_parameters.global_.combine_hash)
        curr_merkle_root = curr_merkle.get_root().value
        
        
        query_generator = QueryGenerator(random.randint(0, 1000000), next_round_parameters, curr_codeword, next_codeword)
        queries = query_generator.generate_query(alpha, curr_codeword, next_codeword, curr_merkle, next_merkle)
        
        return Round(next_merkle_root, queries, next_round_parameters)        


class Prover:
    