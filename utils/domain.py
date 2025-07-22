from utils.field import FieldElement
from typing import Callable

class Domain:
    def __init__(self, values: list[FieldElement]):
        self.values = values
        self.size = len(values)

    @staticmethod
    def generate_domain(generator: FieldElement, size: int):
        return Domain([generator**i for i in range(size)])  # type: ignore (issue with polynomial option)

    def map_domain(self, map: Callable[[FieldElement], FieldElement]):
        self.values = [map(ele) for ele in self.values]
        return self

    def offset_domain(self, offset: FieldElement):
        return self.map_domain(lambda x: offset * x)

    def sq_domain(self):
        return self.map_domain(lambda x: x * x)

    def __len__(self):
        return len(self.values)



