from field import FieldElement


class MultiVPolynomial :
    def __init__(self, mon : 'dict[list[int]]') :
        self.var = len(mon.keys()[0])
        if False in [len(exp_list) == self.var for exp_list in mon.keys()] :
            raise Exception('The keys of the monomials dictionary must have the same length.')
        self.mon = mon
    
    def __call__(self, ant : 'list[FieldElement]') -> 'FieldElement' :
        value = 0
        v = self.var
        for mon in self.mon.keys() :
            mon_val = self.mon[mon]
            for k in range(v) :
                mon_val *= ant[k]**mon[k]
            value += mon_val
        return value