from typing import Type


from charm4py import charm, Chare, Group, Reducer,Array
from my_own_test import Mytest
import numpy as np
from boxtree import *
from my_own_fmm import *
from time import time

class MyChare(Chare):
    def __init__(self):
        print("Hello from MyChare instance in processor", charm.myPe())
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
            print("step467")
            #self.driver.step4()
            #self.driver.step6()

            ti = time()
            self.contribute(self.driver.step4(), Reducer.sum, self.thisProxy[0].collectResult)
            print(time() - ti)
        elif self.flag == "3":
            print("step3")
            ti = time()
            self.contribute(self.driver.step3(), Reducer.sum, self.thisProxy[0].collectResult)
            print(time() - ti)
            return 4
        elif self.flag == "5":
        #print("adjnaskaajsdnkjsanksaksnkajnk")
            print("step5")
            self.contribute(self.driver.step5(), Reducer.sum, self.thisProxy[0].collectResult)
        else:
            self.contribute(np.zeros(9000000), Reducer.sum, self.thisProxy[0].collectResult)

    def collectResult(self, result):

        result = self.driver.wrangler.reorder_potentials(result)
        end = time()
        print( end- self.time)
        assert(result == 9000000).all()


        exit()

def hello(args):
    my_group = Group(MyChare)
    my_group.work(3)

class Distributed_Driver(Chare):
    def __init__(self):

        pass

    def work(self, driver,flag):
        data = 3
        print(data)
        self.contribute(data,Reducer.sum,self.sumation_chare.collectResult)






def main(args):

    my = Mytest()
    tree = my.tree
    driver = my.cal()
    ti = time()
    #driver.step21()
    #driver.step22()
    start = time()
    print(start - ti)
    direct_result_f = charm.createFuture()

    # create one instance of MyChare on every processor
    #my_group = Group(MyChare)

    # create 3 instances of MyChare, distributed among the cores by the runtime

    #first = MyChare()

    # create 2 x 2 instances of MyChare, indexed using 2D index and distributed
    # among all cores by the runtime

    #my_2d_array = Array(MyChare, (2, 2))

    #charm.awaitCreation(my_group, my_array, my_2d_array)
    #print("###############################3")
    #charm.awaitCreation(first)

    my_array = Array(MyChare,4)
    #charm.awaitCreation(my_array)

    from CustomGreen import CustomConstantOneExpansionWrangler
    c = CustomConstantOneExpansionWrangler(tree)
    my_array[0].time_setter(ti)
    my_array[0].summation_setter(driver)
    my_array[1].summation_setter(driver)
    my_array[1].flag_setter("3")
    my_array[1].work()

    driver.step21()
    driver.step22()
    my_array[2].summation_setter(driver)
    my_array[2].flag_setter("467")
    my_array[3].summation_setter(driver)
    my_array[3].flag_setter("5")
    my_array[0].work()
    my_array[2].work()
    my_array[3].work()

    #my_array.work()





    #future = my_array.work(li, ret=True)
    #individual = MyChare

    #individual



if __name__ == "__main__":
    #print(time())
    charm.start(main)  # call main([]) in interactive mode