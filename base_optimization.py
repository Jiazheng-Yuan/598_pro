from typing import Type


from charm4py import charm, Chare, Group, Reducer,Array,threaded,ArrayMap
from my_own_test import Mytest
import numpy as np
from boxtree import *
from my_own_fmm import *
from time import time

class MyChare(Chare):
    def __init__(self,total):
        self.total = total
        self.driver = None
        self.flag = None
        self.time = None
    def summation_setter(self,driver):
        self.driver = driver
    def flag_setter(self,flag):
        self.flag = flag
    def time_setter(self,time):
        self.time = time

    def work(self):

        if self.flag == "467":
            start = time()
            print("step467 on processor:"+str( charm.myPe()))
            self.contribute(self.driver.step4(), Reducer.sum, self.thisProxy[0].collectResult)
            print("step467 took " + str(time() - start)+" seconds to finish")
        elif self.flag == "3":
            start = time()
            print("step3 on processor:"+str( charm.myPe()))
            result = self.driver.step3()
            print(result)
            self.contribute(result, Reducer.sum, self.thisProxy[0].collectResult)
            print("step3 took "+ str(time() - start)+" seconds to finish")
        elif self.flag == "5":
            start = time()
            print("step5 on processor:"+str(charm.myPe()))
            self.contribute(self.driver.step5(), Reducer.sum, self.thisProxy[0].collectResult)
            print("step5 took " + str(time() - start) +" seconds to finish")
        else:
            self.contribute(np.zeros(self.total), Reducer.sum, self.thisProxy[0].collectResult)

    def collectResult(self, result):

        result = self.driver.wrangler.reorder_potentials(result)
        result = self.driver.wrangler.finalize_potentials(result)
        end = time()
        print( end- self.time)
        assert(result == self.total).all()


        exit()



class WorkerMap(ArrayMap):
    def procNum(self, index):
        return (index[0] % (charm.numPes() - 1)) + 1



def main(args):

    my = Mytest()
    tree = my.tree
    driver = my.cal()

    ti = time()
    my_array = Array(MyChare,args=[tree.nsources], dims=4,map=Group(WorkerMap))

    my_array[1].summation_setter(driver)
    my_array[1].flag_setter("3")
    my_array[1].work()

    driver.step21()
    driver.step22()



    from CustomGreen import CustomConstantOneExpansionWrangler
    c = CustomConstantOneExpansionWrangler(tree)
    my_array[0].time_setter(ti)
    my_array[0].summation_setter(driver)

    my_array[2].summation_setter(driver)
    my_array[2].flag_setter("467")
    my_array[3].summation_setter(driver)
    my_array[3].flag_setter("5")

    my_array[0].work()
    my_array[2].work()
    my_array[3].work()




if __name__ == "__main__":
    charm.start(main)  # call main([]) in interactive mode