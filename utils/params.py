from utils.field import Field, FieldElement, MainFieldElement
import hashlib
from utils.domain import Domain


class GlobalParameters:
    main_field_prime = Field.main().p
    log_2_size_of_group = 10 
    size_of_group = 1 << log_2_size_of_group  # its easier if SIZE OF GROUP is a POWER OF 2
    num_rounds = log_2_size_of_group
    num_colinearity_tests = 20 # ensure that this is such that max_degree < 2 * num_colinearity_tests
    
        
    generator_int = 7


    g = MainFieldElement(7) ** ((1 << (119 - log_2_size_of_group))) # generator
    g = g ** 407
    w = MainFieldElement(3)  # offset

    group_domain = Domain.generate_domain(g, size_of_group)
    coset_domain = group_domain.offset_domain(w)

    @staticmethod
    def hash_function(x: FieldElement | int) -> int:
        if isinstance(x, FieldElement):
            x = x.value
        return int(hashlib.sha256(x.to_bytes(32, "big")).hexdigest(), 16)
    
    @staticmethod
    def combine_hash(x: FieldElement | int, y: FieldElement | int) -> int:
        return GlobalParameters.hash_function(x) ^ GlobalParameters.hash_function(y)
    
