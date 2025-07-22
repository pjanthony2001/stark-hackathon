from utils.field import FieldElement
from typing import Callable

class Domain:
    def __init__(self, generator, values: list[FieldElement]):
        self.generator = generator
        self.values = values
        self.size = len(values)

    @staticmethod
    def generate_domain(generator: FieldElement, size: int):
        return Domain(generator, [generator**i for i in range(size)])  # type: ignore (issue with polynomial option)

    def map_domain(self, map: Callable[[FieldElement], FieldElement]):
        new_values = [map(ele) for ele in self.values]
        new_generator = map(self.generator)
        return Domain(new_generator, new_values)

    def offset_domain(self, offset: FieldElement):
        return self.map_domain(lambda x: offset * x)

    def sq_domain(self):
        new_size = self.size // 2
        new_values = [(self.values[i] ** 2) for i in range(new_size)]
        return Domain(self.generator ** 2, new_values) #type: ignore (issue with FieldElement)

    def __len__(self):
        return len(self.values)

