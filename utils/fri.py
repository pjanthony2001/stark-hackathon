import math
from hashlib import blake2b
from utils.field import Field, FieldElement
from utils.proof_stream import ProofStream
class Fri:

    def __init__(self, omega, domain_length, offset, number_of_colinearity_tests, expansion_factor):
        self.omega = omega
        self.offset = offset
        self.field = omega.field
        self.domain_length = domain_length
        self.number_of_colinearity_tests = number_of_colinearity_tests
        self.expansion_factor = expansion_factor

    def num_rounds( self ):
        codeword_length = self.domain_length
        num_rounds = 0
        while codeword_length > self.expansion_factor and 4*self.number_of_colinearity_tests < codeword_length:
            codeword_length = codeword_length/2
            num_rounds += 1
        return num_rounds
    
    def eval_domain(self):
        return [ self.offset * self.omega**i for i in range(self.domain_length)]
    
    def prove(self, codeword, proofstream):
        assert self.domain_length == len(codeword)
        proofstream.push(codeword)
        proofstream.prover_communicating()


