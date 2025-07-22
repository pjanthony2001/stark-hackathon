import pickle
from hashlib import shake_256


class ProofStream:

    def __init__(self, read_index=0):
        self.read_index = 0
        self.objects = []

    def push(self, object):
        self.objects.append(object)

    def pull(self):
        assert self.read_index < len(
            self.objects
        ), "ProofStream: cannot pull object; queue empty."
        object = self.objects[self.read_index]
        self.read_index += 1
        return object

    def serialization(self):
        return pickle.dumps(self.objects)

    @staticmethod
    def deserialization(pickled_list):
        ps = ProofStream()
        ps.objects = pickle.loads(pickled_list)
        return ps

    def prover_communicating(self, num_bytes=32):
        return shake_256(self.serialization()).digest(num_bytes)

    def verifier_communicating(self, num_bytes=32):
        return shake_256(pickle.dumps(self.objects[: self.read_index])).digest(
            num_bytes
        )
