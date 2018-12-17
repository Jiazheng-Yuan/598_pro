from typing import Type


from charm4py import charm, Chare, Group, Reducer,Array,threaded,ArrayMap,Options
from charm4py import readonlies as ro

from separate_data_structure.my_own_test import Mytest
import numpy as np
from boxtree import *
from separate_data_structure.my_own_fmm import *
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

        if self.flag == "4":
            start = time()
            print("step4 on "+str( charm.myPe()))
            #self.driver.step4()
            #self.driver.step6()
            self.contribute(self.driver.separate_step4(), Reducer.sum, self.future)
            print("step4: " + str(time() - start))
        elif self.flag == '6':
            start = time()
            print("step6 on " + str(charm.myPe()))
            # self.driver.step4()
            # self.driver.step6()
            self.contribute(self.driver.separate_step6(), Reducer.sum, self.future)
            print("step6: " + str(time() - start))
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
            self.contribute(np.zeros(9000000), Reducer.sum, self.future)

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
        return (index[0] % (charm.numPes() - 1)) + 4
class ExpWorkerMap(ArrayMap):
    def procNum(self, index):
        #print(index)
        return (index[0] % (charm.numPes() - 1))

class ExpWorkerMap2(ArrayMap):
    def procNum(self, index):
        # print(index)
        return (index[0] % (charm.numPes() - 1)) + 2

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
class step4_chare(Chare):
    def __init__(self,total_processors,f):


        self.total_processors = total_processors
        self.f = f
        self.pos = 0
    def index_setter(self,index):
        self.pos = index
    def calculate(self):
        print("this piece "+str(self.pos) + "   is on processor:" + str(charm.myPe()))
        st = time()
        local_exp = ro.driver.multicore_separate_step4(self.total_processors,self.pos)
        self.contribute(local_exp,Reducer.sum,self.f)
        print("time to calculate "+str(self.pos)+ "th piece of the step4:" +str(time() - st))
class step6_chare(Chare):
    def __init__(self,total_processors,f):


        self.total_processors = total_processors
        self.f = f
        self.pos = 0
    def index_setter(self,index):
        self.pos = index
    def calculate(self):
        print("this piece "+str(self.pos) + "   is on processor:" + str(charm.myPe()))
        st = time()
        local_exp = ro.driver.multicore_separate_step6(self.total_processors,self.pos)
        self.contribute(local_exp,Reducer.sum,self.f)
        print("time to calculate "+str(self.pos)+ "th piece of the step6:" +str(time() - st))



def main(args):

    my = Mytest()
    tree = my.tree
    driver = my.cal()
    ti = time()
    very_start = time()

    f = charm.createFuture()
    f_other = charm.createFuture()
    creation_time = time()
    step4_future = charm.createFuture()
    step6_future = charm.createFuture()
    step3_array = Array(step3_chare, args=[driver, 4, f], dims=4, map=Group(WorkerMap))
    for i in range(0,4):
        step3_array[i].index_setter(i)

    step3_array.calculate()
    ro.driver = driver


    print("hehheh")
    #a = np.zeros(9000000)
    #driver.step3()


    driver.step21()
    driver.step22()

    step4_array = Array(step4_chare, args=[ 2, step4_future], dims=2, map=Group(ExpWorkerMap))
    step6_array = Array(step6_chare, args=[ 2, step6_future], dims=2, map=Group(ExpWorkerMap2))
    for i in range(0,2):
        step4_array[i].index_setter(i)
        step6_array[i].index_setter(i)
    step4_array.calculate()
    step6_array.calculate()

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


    tii = time()
    #print("time for creating two array, step1,2 and mmy array start:" + str(time() - start))
    #my_array.work()

    #print(local_result)


    local_exps = step4_future.get() + step6_future.get()
    local_result = f.get()
    local_result += driver.step5()
    print("time to get local_result:" + str(time() - tii))

    local_exps = driver.wrangler.refine_locals(driver.traversal.level_start_target_or_target_parent_box_nrs,
                                  driver.traversal.target_or_target_parent_boxes,
                                  local_exps)
    local_result_from_exp = driver.wrangler.eval_locals(
        driver.traversal.level_start_target_box_nrs,
        driver.traversal.target_boxes,
        local_exps)



    #
    end = time()
    result = driver.wrangler.reorder_potentials(local_result_from_exp + local_result)
    result = driver.wrangler.finalize_potentials(result)
    print("at the end:"+str(end - very_start))
    #print(result)
    assert (result == 9000000).all()
    charm.printStats()
    exit()


    #assert (result == 9000000).all()



    #future = my_array.work(li, ret=True)
    #individual = MyChare

    #individual




if __name__ == "__main__":
    Options.PROFILING = True
    #
    ti = time()
    charm.start(main)  # call main([]) in interactive mode
    #main("a")
    #print(time() - ti)