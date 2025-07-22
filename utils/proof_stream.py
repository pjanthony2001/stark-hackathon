import pickle
from hashlib import shake_256


class ProofStream:
    """
    Fiat-Shamir transform for proof generation and verification, 
    with serialization as bytes to enforce immutability.
    """

    def __init__(self):
        self.read_index: int = 0
        self.objects: list[bytes] = []

    def push(self, obj: object) -> None:
        serialized_obj = pickle.dumps(obj)
        self.objects.append(serialized_obj)

    def pull(self) -> object:
        if self.read_index >= len(self.objects):
            raise IndexError("ProofStream: cannot pull object; queue empty.")

        serialized_obj = self.objects[self.read_index]
        self.read_index += 1
        return pickle.loads(serialized_obj)

    def serialization(self) -> bytes:
        return pickle.dumps(self.objects)

    @staticmethod
    def deserialization(data: bytes):
        ps = ProofStream()
        ps.objects = pickle.loads(data)
        return ps

    def prover_communicating(self, num_bytes: int = 32) -> bytes:
        return shake_256(pickle.dumps(self.objects)).digest(num_bytes)

    def verifier_communicating(self, num_bytes: int = 32) -> bytes:
        return shake_256(pickle.dumps(self.objects[: self.read_index])).digest(
            num_bytes
        )


if __name__ == "__main__":

    def test_fiat_shamir():
        proof_stream = ProofStream()

        prover_commitments = [
            "round_0_commitment",
            "round_1_commitment",
            "round_2_commitment",
            "round_3_commitment",
            "final_data",
        ]
        prover_challenges = []
        for commitment in prover_commitments:
            proof_stream.push(commitment)
            prover_challenges.append(proof_stream.prover_communicating())

        verifier_challenges = []
        for _ in range(len(prover_commitments)):
            _ = proof_stream.pull()
            verifier_challenges.append(proof_stream.verifier_communicating())

        assert (
            prover_challenges == verifier_challenges
        ), "Mismatch between prover and verifier sequences."

    test_fiat_shamir()
