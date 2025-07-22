from typing import Self
from typing import Callable, List, Tuple, Optional
from typing import TypeVar, Generic


T = TypeVar("T")


class Node(Generic[T]):
    def __init__(self, left: Optional["Node"], right: Optional["Node"], value: T):
        self.value: "T" = value
        self.left: Optional["Node"] = left
        self.right: Optional["Node"] = right
        self.parent: Optional["Node"] = None

    def get_val(self) -> "T":
        return self.value

    def get_left(self) -> Optional["Node"]:
        return self.left

    def get_right(self) -> Optional["Node"]:
        return self.right

    def set_parent(self, parent: "Node[T]"):
        self.parent = parent

    def get_sibling(self) -> "tuple[bool, Node]":
        if self.parent == None:
            raise ValueError("Cannot get sibling of root node")
        return self.parent.get_other_child(
            self
        )  # right sibling if False, left sibling if True

    def get_other_child(self, child: "Node") -> "tuple[bool, Node]":
        if self.left is None or self.right is None:
            raise ValueError("Cannot get sibling of a leaf node")

        if self.left == child:
            return (False, self.right)  # right child if False, left child if True
        return (True, self.left)


class Leaf(Node[T]):
    def __init__(self, value: "T"):
        super().__init__(None, None, value)


class BinaryTree(Generic[T]):
    def __init__(self, leaves: list[T], combine: Callable[[T, T], T]):
        self.n: "int" = len(leaves)
        self.leaves: "list[Node]" = [Leaf(value) for value in leaves]
        self.combine: Callable = combine
        self.root: "Node" = BinaryTree.construct_tree(self.leaves.copy(), combine)

    @staticmethod
    def construct_tree(leaves: "list[Node]", combine: Callable[[T, T], T]) -> Node:
        # I like the iterative version, but teach Come the recursive version as well

        if len(leaves) == 0:
            raise ValueError("Cannot construct a tree with no leaves")

        while len(leaves) > 1:
            sequence_of_pairs = [(2 * i, 2 * i + 1) for i in range(len(leaves) // 2)]
            storage = []
            for tuple in sequence_of_pairs:

                k, l = tuple
                node = Node(
                    leaves[k],
                    leaves[l],
                    combine(leaves[k].get_val(), leaves[l].get_val()),
                )

                leaves[k].set_parent(node)
                leaves[l].set_parent(node)

                storage.append(node)

            if len(leaves) % 2:
                storage.append(leaves[-1])
            leaves = storage

        return leaves[0]

    def get_root(self):
        return self.root

    def get_sibling_path_to_root(self, node) -> "list[tuple[bool, Node]]":
        path = []
        while node.parent is not None:  # while node is not the root
            is_left, sibling = node.get_sibling()
            path.append((is_left, sibling))
            node = node.parent
        return path

    @staticmethod
    def recombine_path_node(
        leaf_val: T, path: "list[tuple[bool, Node[T]]]", combine: Callable[[T, T], T]
    ) -> T:
        
        path_list = list(map(lambda x: (x[0], x[1].get_val()), path))
        return BinaryTree.recombine_path(leaf_val, path_list, combine)
    
    @staticmethod
    def recombine_path(
        leaf_val: T, path: "list[tuple[bool, T]]", combine: Callable[[T, T], T]
    ) -> T:
        curr_val = leaf_val
        for is_left, sibling in path:
            if is_left:
                curr_val = combine(sibling, curr_val)
            else:
                curr_val = combine(curr_val, sibling)
        return curr_val


class MerkleTree(Generic[T]):
    def __init__(self, leaves: "list", hash: Callable[[T, T], T]):
        self.n = len(leaves)
        self.tree = BinaryTree(leaves, hash)
        self.leaves = self.tree.leaves

    def get_root(self) -> Node[T]:
        return self.tree.get_root()

    def get_sibling_path_to_root(self, leaf_index: int) -> "list[tuple[bool, T]]":
        return list(
            map(
                lambda x: (x[0], x[1].value),
                self.tree.get_sibling_path_to_root(self.leaves[leaf_index]),
            )
        )
        
    @staticmethod
    def verify_path(
        leaf_val: T, path: "list[tuple[bool, T]]", root_val: T, combine: Callable[[T, T], T]
    ) -> bool:

        recombined_value = BinaryTree.recombine_path(leaf_val, path, combine)
        return recombined_value == root_val


if __name__ == "__main__":

    def path_test(leaves, combine):
        tree = BinaryTree(leaves, combine)
        root = tree.get_root()

        for leaf in tree.leaves:
            path = tree.get_sibling_path_to_root(leaf)
            recombined_value = BinaryTree.recombine_path(leaf.get_val(), path, combine)
            assert (
                recombined_value == root.get_val()
            ), f"Recombined value {recombined_value} does not match root value {root.get_val()} for leaf {leaf.get_val()}"

    def combine_int(a, b):  # commutative
        return a + b

    def combine_str(a, b):  # not commutative
        return a + b

    path_test([1, 2, 3, 4, 5, 6], combine_int)
    path_test(["a", "b", "c", "d", "e", "f"], combine_str)
