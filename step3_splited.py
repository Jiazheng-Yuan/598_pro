from typing import Type


from charm4py import charm, Chare, Group, Reducer,Array,threaded,ArrayMap
from my_own_test import Mytest
import numpy as np
from boxtree import *
from my_own_fmm import *
from time import time

class MyChare(Chare):
    def __init__(self,future):


        self.flag = None
        self.time = None
        self.future = future
        self.driver = None
    def summation_setter(self,driver):
        self.driver = driver

    def flag_setter(self,flag):
        self.flag = flag
    def time_setter(self,time):
        self.time = time

    #@threaded
    def work(self):

        if self.flag == "467":
            start = time()
            print("step467 on "+str( charm.myPe()))
            #self.driver.step4()
            #self.driver.step6()
            self.contribute(self.driver.step4(), Reducer.sum, self.future)
            print("step467: " + str(time() - start))
        elif self.flag == "3":
            start = time()
            #self.flag = 100
            print("step3 on "+str( charm.myPe()))
            result = self.driver.step3()
            self.contribute(result, Reducer.sum, self.future)
            print("step3: "+ str(time() - start))
        elif self.flag == "5":
        #print("adjnaskaajsdnkjsanksaksnkajnk")
            start = time()
            print("step5 on "+str(charm.myPe()))
            self.contribute(self.driver.step5(), Reducer.sum, self.future)
            print("step5: " + str(time() - start))
        else:
            self.contribute(np.zeros(1000000), Reducer.sum, self.future)

    def collectResult(self, result):

        result = self.driver.wrangler.reorder_potentials(result)
        end = time()
        print( end- self.time)



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



class WorkerMap(ArrayMap):
    def procNum(self, index):
        #print(index)
        return (index[0] % (charm.numPes() - 1)) + 2
class ExpWorkerMap(ArrayMap):
    def procNum(self, index):
        #print(index)
        return (index[0] % (charm.numPes() - 1)) + 1

class step3_chare(Chare):
    def __init__(self,driver,total_processors,f):

        self.driver = driver
        self.total_processors = total_processors
        self.f = f
        self.pos = 0
    def index_setter(self,index):
        self.pos = index
    def calculate(self):
        print("this piece "+str(self.pos) + "   is on processor:" + str(charm.myPe()))
        st = time()
        partial_direct_interaction = self.driver.multicore_step3(self.total_processors,self.pos)
        self.contribute(partial_direct_interaction,Reducer.sum,self.f)
        print("time to calculate "+str(self.pos)+ "th piece of the direct interaction:" +str(time() - st))



def main(args):

    my = Mytest()
    tree = my.tree
    driver = my.cal()
    ti = time()
    very_start = time()

    f = charm.createFuture()
    f_other = charm.createFuture()
    creation_time = time()
    step3_array = Array(step3_chare, args=[driver, 6, f], dims=6,map=Group(WorkerMap))
    my_array = Array(MyChare, args=[f_other], dims=2)
    print("hehheh")
    #a = np.zeros(9000000)
    #driver.step3()

    for i in range(0,6):
        step3_array[i].index_setter(i)
    step3_array.calculate()
    driver.step21()
    driver.step22()


    #print("creation for step3 finished " + str(time() - creation_time))

    #start = time()
    #print(start - ti)
    #my_array = Array(MyChare, args=[driver, f_other], dims=2)

    # create one instance of MyChare on every processor
    #my_group = Group(MyChare)

    # create 3 instances of MyChare, distributed among the cores by the runtime

    #first = MyChare()

    # create 2 x 2 instances of MyChare, indexed using 2D index and distributed
    # among all cores by the runtime

    #my_2d_array = Array(MyChare, (2, 2))
    #charm.awaitCreation(my_array)

    #while(True):
    #    pass
    #print("###############################3")
    #charm.awaitCreation(first)


    #charm.awaitCreation(my_array)

    #from CustomGreen import CustomConstantOneExpansionWrangler
    #c = CustomConstantOneExpansionWrangler(tree)
    #my_array[0].time_setter(ti)
    #my_array[0].summation_setter(driver)

    my_array[0].summation_setter(driver)
    my_array[0].flag_setter("467")

    my_array[1].summation_setter(driver)
    my_array[1].flag_setter("5")
    #my_array[1].driver = driver
    my_array.work()

    tii = time()
    #print("time for creating two array, step1,2 and mmy array start:" + str(time() - start))
    #my_array.work()
    local_result = f.get()
    #print(local_result)
    print("time to get local_result:" + str(time() - tii))


    potential = f_other.get()


    #
    end = time()
    result = driver.wrangler.reorder_potentials(potential + local_result)
    print("at the end:"+str(end - very_start))
    #print(result)
    assert (result == 1000000).all()
    exit()


    #assert (result == 9000000).all()



    #future = my_array.work(li, ret=True)
    #individual = MyChare

    #individual




if __name__ == "__main__":
    #
    ti = time()
    charm.start(main)  # call main([]) in interactive mode
    #main("a")
    #print(time() - ti)