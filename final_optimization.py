from typing import Type

from step3_driver import step3_driver
from step4_driver import step4_driver
from step6_driver import step6_driver
from step5_driver import step5_with_extent_driver
from charm4py import charm, Chare, Group, Reducer,Array,threaded,ArrayMap,Options
from charm4py import readonlies as ro
import sys

from my_own_test import Mytest
import numpy as np
from boxtree import *
from my_own_fmm import *
from time import time

class MyChare(Chare):
    def __init__(self,future,total,driver):


        self.flag = None
        self.time = None
        self.future = future
        self.driver = driver
        self.total_processors = total
        self.pos = None

    def summation_setter(self,driver):
        self.driver = driver

    def flag_setter(self,flag):
        self.flag = flag
    def time_setter(self,time):
        self.time = time
    def index_setter(self,index):
        self.pos = index
    def work(self):

        if self.flag == "4":
            start = time()
            print("step4 on processor"+str( charm.myPe()))
            self.contribute(self.driver.multicore_separate_step4(self.total_processors,self.pos), Reducer.sum, self.future)
            print("step4 time to finish: " + str(time() - start)+" on processor "+str(str(charm.myPe())))
        elif self.flag == "3":
            print("step3 on processor " + str(charm.myPe()))
            st = time()
            partial_direct_interaction = self.driver.multicore_step3(self.total_processors, self.pos)
            self.contribute(partial_direct_interaction, Reducer.sum, self.future)
            print("time to calculate " + str(self.pos) + "th piece of the direct interaction:" + str(time() - st))
        elif self.flag == "6":
            start = time()
            print("step6 on processor "+str(charm.myPe()))
            self.contribute(self.driver.multicore_separate_step6(self.total_processors, self.pos), Reducer.sum, self.future)
            print("step6 time to finish: " + str(time() - start)+" on processor "+str(str(charm.myPe())))
        elif self.flag == "5":
            start = time()
            print("step5 on "+str(charm.myPe()))
            self.contribute(self.driver.step5_with_extent(self.total_processors, self.pos), Reducer.sum, self.future)
            print("step5 time to finish: " + str(time() - start)+" on processor "+str(str(charm.myPe())))




class WorkerMap(ArrayMap):
    def procNum(self, index):
        return (index[0] % (charm.numPes() - 1)) + 1

def main(args):

    my = Mytest()
    tree = my.tree
    driver = my.cal()

    very_start = time()

    f_step3 = charm.createFuture()
    f_step4 = charm.createFuture()
    f_step5 = charm.createFuture()
    f_step6 = charm.createFuture()

    step3_dr = step3_driver(driver.traversal.target_boxes,driver.traversal.neighbor_source_boxes_starts,
                            driver.traversal.neighbor_source_boxes_lists,
                            driver.src_weights,tree)
    step3_array = Array(MyChare, args=[f_step3,7,step3_dr], dims=7,map=Group(WorkerMap))


    for i in range(0,7):
        step3_array[i].index_setter(i)
        step3_array[i].flag_setter("3")
    step3_array.work()
    driver.step21()
    driver.step22()
    step4_dr = step4_driver(tree.nboxes,driver.traversal.level_start_target_or_target_parent_box_nrs,
                            driver.traversal.target_or_target_parent_boxes,
                            driver.traversal.from_sep_siblings_starts,
                            driver.traversal.from_sep_siblings_lists,
                            driver.mpole_exps)
    step4_array = Array(MyChare, args=[f_step4, 8,step4_dr], dims=8)
    step6_dr = step6_driver( driver.traversal.level_start_target_or_target_parent_box_nrs,
                             driver.traversal.target_or_target_parent_boxes,
                             driver.traversal.from_sep_bigger_starts,
                             driver.traversal.from_sep_bigger_lists,
                             driver.src_weights,tree)
    step6_array = Array(MyChare, args=[f_step6, 8, step6_dr], dims=8)

    for i in range(0,8):
        step4_array[i].index_setter(i)
        step4_array[i].flag_setter("4")
        step6_array[i].index_setter(i)
        step6_array[i].flag_setter("6")
    if driver.traversal.from_sep_close_smaller_starts is not None:
        step5_with_extent_dr = step5_with_extent_driver(driver.traversal.target_boxes,
                                                        driver.traversal.from_sep_close_smaller_starts,
                                                        driver.traversal.from_sep_close_smaller_lists,
                                                        driver.src_weights, tree)
        step5_array = Array(MyChare, args=[f_step5, 8, step5_with_extent_dr], dims=8)
        for i in range(0, 8):
            step5_array[i].index_setter(i)
            step5_array[i].flag_setter("5")
        step5_array.work()
    step4_array.work()
    step6_array.work()


    local_result = driver.separate_step5()
    if driver.traversal.from_sep_close_smaller_starts is not None:
        local_result+=f_step5.get()


    if driver.traversal.from_sep_close_bigger_starts is not None:
        step_6_extra = driver.step6_extra()
        local_result += step_6_extra
    local_result += f_step3.get()
    local_exps = f_step6.get() + f_step4.get()

    local_exps = driver.wrangler.refine_locals(driver.traversal.level_start_target_or_target_parent_box_nrs,
                                  driver.traversal.target_or_target_parent_boxes,
                                  local_exps)
    last_Step = time()
    local_result_from_exp = driver.wrangler.eval_locals(
        driver.traversal.level_start_target_box_nrs,
        driver.traversal.target_boxes,
        local_exps)



    #

    result = driver.wrangler.reorder_potentials(local_result_from_exp + local_result)
    result = driver.wrangler.finalize_potentials(result)
    end = time()
    print("total time:"+str(end - very_start))

    assert (result == driver.src_weights.sum() ).all()

    exit()




if __name__ == "__main__":

    charm.start(main)