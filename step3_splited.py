from typing import Type


from charm4py import charm, Chare, Group, Reducer,Array,threaded,ArrayMap,Options
from charm4py import readonlies as ro
import sys

from my_own_test import Mytest
import numpy as np
from boxtree import *
from my_own_fmm import *
from time import time

class MyChare(Chare):
    def __init__(self,future,total):


        self.flag = None
        self.time = None
        self.future = future
        self.driver = None
        self.total = total
    def summation_setter(self,driver):
        self.driver = driver

    def flag_setter(self,flag):
        self.flag = flag
    def time_setter(self,time):
        self.time = time

    def work(self):

        if self.flag == "4":
            start = time()
            print("step4 on "+str( charm.myPe()))
            self.contribute(self.driver.separate_step4(), Reducer.sum, self.future)
            print("step4: " + str(time() - start))

        elif self.flag == "6":
            start = time()
            print("step6 on "+str(charm.myPe()))
            self.contribute(self.driver.separate_step6(), Reducer.sum, self.future)
            print("step6: " + str(time() - start))
        else:
            self.contribute(np.zeros(self.total), Reducer.sum, self.future)


class WorkerMap(ArrayMap):
    def procNum(self, index):
        return (index[0] % (charm.numPes() - 1)) + 2
class ExpWorkerMap(ArrayMap):
    def procNum(self, index):
        return (index[0] % (charm.numPes() - 1)) + 1

class step3_chare(Chare):
    def __init__(self,total_processors,f):


        self.total_processors = total_processors
        self.f = f
        self.pos = 0
    def index_setter(self,index):
        self.pos = index
    def calculate(self):
        print("this piece "+str(self.pos) + "   is on processor:" + str(charm.myPe()))
        st = time()
        partial_direct_interaction = ro.driver.multicore_step3(self.total_processors,self.pos)
        self.contribute(partial_direct_interaction,Reducer.sum,self.f)
        print("time to calculate "+str(self.pos)+ "th piece of the direct interaction:" +str(time() - st))

def main(args):

    my = Mytest()
    tree = my.tree
    driver = my.cal()

    very_start = time()

    f = charm.createFuture()
    f_other = charm.createFuture()
    ro.driver = driver
    step3_array = Array(step3_chare, args=[6, f], dims=6,map=Group(WorkerMap))
    my_array = Array(MyChare, args=[f_other,tree.nsources], dims=2)


    for i in range(0,6):
        step3_array[i].index_setter(i)
    step3_array.calculate()
    driver.step21()
    driver.step22()


    my_array[0].summation_setter(driver)
    my_array[0].flag_setter("4")

    my_array[1].summation_setter(driver)
    my_array[1].flag_setter("6")

    my_array.work()


    local_result = driver.step5()
    if driver.traversal.from_sep_close_bigger_starts is not None:
        step_6_extra = driver.step6_extra()
        local_result += step_6_extra
    local_result += f.get()



    local_exps = f_other.get()

    local_exps = driver.wrangler.refine_locals(driver.traversal.level_start_target_or_target_parent_box_nrs,
                                  driver.traversal.target_or_target_parent_boxes,
                                  local_exps)
    local_result_from_exp = driver.wrangler.eval_locals(
        driver.traversal.level_start_target_box_nrs,
        driver.traversal.target_boxes,
        local_exps)

    end = time()
    result = driver.wrangler.reorder_potentials(local_result_from_exp + local_result)
    result = driver.wrangler.finalize_potentials(result)
    print("at the end:"+str(end - very_start))
    assert (result == tree.nsources).all()
    exit()




if __name__ == "__main__":
    charm.start(main)
