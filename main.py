def main():
    """
    Main function that simulates a simple STARK proof of a computation C(t) (over a finite field),
    where t is the time step, such that

    C(0) = 0 and C(25) = 225075.
    C(t + 1) = C(t) + C(t - 1) for t > 1.


    We will do a proof in the clear plaintext, without any cryptographic primitives.
    """
    c_0 = 0
    c_1 = 3
    print(f"Clear Computation: C(0) = {c_0}")
    print(f"Clear Computation: C(1) = {c_1}")
    for _ in range(2, 26):
        c_0, c_1 = c_1, c_0 + c_1
        print(f"Clear Computation: C({_}) = {c_1}")


main()
