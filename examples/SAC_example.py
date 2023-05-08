# TODO: append path???

import sys
sys.path.append("../JuPlot")

from JuPlot.SAC import SAC, semi_abstract_method

class A(SAC):
    def __init__(self):
        super().__init__()

    @semi_abstract_method
    def method_a(self):
        pass

    @semi_abstract_method
    def method_b(self):
        print("abstract method")

    @semi_abstract_method
    def method_c(self):
        pass

    @semi_abstract_method
    def method_d(self):
        pass

class B(A):
    def method_a(self):
        print("IMPLEMENTED METHOD a")


if __name__ == "__main__":
    cls = B()

    cls.method_b()