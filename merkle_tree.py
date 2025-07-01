class BinaryTree:
    def __init__(self, leaves):
        self.n = len(leaves)
        self.leaves = [Leaf(value) for value in leaves]
        self.root = BinaryTree.construct_tree(self.leaves.copy())
        
    
    def construct_tree(leaves):
        while len(leaves) > 1:
            sequence_of_pairs = [ (2*i,2*i+1) for i in range( len(leaves) // 2) ]
            storage = []
            for tuple in sequence_of_pairs:

                k,l = tuple
                node = Node(leaves[k], leaves[l], leaves[k].get_val()+ leaves[l].get_val())
                
                leaves[k].set_parent(node)
                leaves[l].set_parent(node)

                storage.append(node)
            if len(leaves) % 2 == 1:
                storage.append(leaves[-1])
            leaves = storage

        return leaves[0]

        

class Node:
    def __init__(self, left, right, value):
        self.value = value
        self.left = left
        self.right = right
        self.parent = None

    def get_val(self):
        return self.value
    
    def get_left(self):
        return self.left
    
    def get_right(self):
        return self.right
    
    def set_parent(self, parent :'Node'):
        self.parent = parent
    
    def get_sibling(self):
        if self.parent != None:
            return self.parent.get_other_child(self)
        
    def get_other_child(self, child):
        if self.left == child:
            return self.right
        return self.left

    
class Leaf(Node):
    def __init__(self, value):
        super().__init__(None, None, value)



    
class MerkleTree:
    def __init__(self, leaves : 'list', hash):
        self.n = len(leaves)
        self.tree = BinaryTree(leaves)



if __name__ == '__main__':
    leaf1 = Leaf(1)
    print(leaf1.get_val())
    print(leaf1.get_left())