from typing import Type


from charm4py import charm, Chare, Group, Reducer,Array,ArrayMap
from my_own_test import Mytest
import numpy as np
from boxtree import *
from my_own_fmm import *
from time import time

class MyChare(Chare):
    def __init__(self):
        self.driver = None
        self.flag = None
        self.time = None
    def summation_setter(self,driver):
        self.driver = driver

    def flag_setter(self,flag):
        self.flag = flag

    def time_setter(self,time):
        self.time = time

    def direct_result(self, f):
        start = time()

        if self.flag == "3":
            print("step3 " +  str(charm.myPe()))
            self.contribute(self.driver.step3(), Reducer.sum, f)
            print("step3 time to finish:" + str(time() - start))

        elif self.flag == "5":
            print("step5 on processor: " +  str(charm.myPe()))
            self.contribute(self.driver.step5(), Reducer.sum, f)
            print("step5 time to finish:" + str(time() - start))



    def sum_local_exp(self, f):
        start = time()
        print(str(self.thisIndex) + "   " + str(charm.myPe()))
        if self.flag == "4":
            print("step4 "+ str(charm.myPe()))
            self.contribute(self.driver.separate_step4(), Reducer.sum, f)
            print("step4 time to finish:" + str(time() - start))

        elif self.flag == "6":
            print("step6 "+ str(charm.myPe()))
            self.contribute(self.driver.separate_step6(), Reducer.sum, f)
            print("step6 time to finish:" + str(time() - start))

class WorkerMap(ArrayMap):
    def procNum(self, index):
        return (index[0] % (charm.numPes() - 1)) + 1

class DirectWorkerMap(ArrayMap):
    def procNum(self, index):
        return (index[0] % (charm.numPes() - 1)) + 3

def main(args):
    my = Mytest()
    tree = my.tree
    driver = my.cal()
    ti = time()
    direct_result_future = charm.createFuture()
    local_result_future = charm.createFuture()
    local_exp_workers = Array(MyChare, 2, map=Group(WorkerMap))
    local_exp_workers[0].summation_setter(driver)
    local_exp_workers[0].flag_setter('3')
    local_exp_workers[0].direct_result(direct_result_future)

    driver.step21()
    driver.step22()

    local_exp_workers[1].summation_setter(driver)
    local_exp_workers[1].flag_setter('5')
    local_exp_workers[1].direct_result(direct_result_future)

    direct_evl_workers = Array(MyChare, 2, map=Group(DirectWorkerMap))
    direct_evl_workers[0].summation_setter(driver)
    direct_evl_workers[0].flag_setter('4')
    direct_evl_workers[0].sum_local_exp(local_result_future)
    direct_evl_workers[1].summation_setter(driver)
    direct_evl_workers[1].flag_setter('6')
    direct_evl_workers[1].sum_local_exp(local_result_future)

    local_exps = local_result_future.get()
    last_step_start = time()
    driver.wrangler.refine_locals(driver.traversal.level_start_target_or_target_parent_box_nrs,
                                  driver.traversal.target_or_target_parent_boxes,
                                  local_exps)
    local_result = driver.wrangler.eval_locals(
        driver.traversal.level_start_target_box_nrs,
        driver.traversal.target_boxes,
        local_exps)


    direct_result = direct_result_future.get()

    result = driver.wrangler.reorder_potentials(direct_result + local_result)
    result = driver.wrangler.finalize_potentials(result)
    print("last step time" + str(time() - last_step_start))

    end = time()
    print(end - ti)
    assert (result == my.tree.nsources).all()
    exit()



if __name__ == "__main__":
    charm.start(main)  # call main([]) in interactive mode