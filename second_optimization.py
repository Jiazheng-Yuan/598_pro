from typing import Type


from charm4py import charm, Chare, Group, Reducer,Array,ArrayMap
from separate_data_structure.my_own_test import Mytest
import numpy as np
from boxtree import *
from separate_data_structure.my_own_fmm import *
from time import time

class MyChare(Chare):
    def __init__(self):
        #print(str(self.thisIndex) + "   " + str(charm.myPe()))
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
            print("step3 time:" + str(time() - start))

        elif self.flag == "5":
            #print("adjnaskaajsdnkjsanksaksnkajnk")
            print("step5 " +  str(charm.myPe()))
            self.contribute(self.driver.step5(), Reducer.sum, f)
            print("step5 time:" + str(time() - start))

        #else:
        #    self.contribute(np.zeros(3000000), Reducer.sum, f)


    def sum_local_exp(self, f):
        start = time()
        print(str(self.thisIndex) + "   " + str(charm.myPe()))
        if self.flag == "4":
            print("step4 "+  str(charm.myPe()))
            self.contribute(self.driver.separate_step4(), Reducer.sum, f)
            print("step4 time:" + str(time() - start))

        elif self.flag == "6":
            # print("adjnaskaajsdnkjsanksaksnkajnk")
            print("step6 "+  str(charm.myPe()))
            self.contribute(self.driver.separate_step6(), Reducer.sum, f)
            print("step6 time:" + str(time() - start))
        #else:
        #    self.contribute(np.zeros(3000000), Reducer.sum, f)

class WorkerMap(ArrayMap):
    def procNum(self, index):
        #print(index)
        return (index[0] % (charm.numPes() - 1)) + 1

class DirectWorkerMap(ArrayMap):
    def procNum(self, index):
        #print(index)
        return (index[0] % (charm.numPes() - 1)) + 3


def hello(args):
    my_group = Group(MyChare)
    my_group.work(3)

class local_exp_eval(Chare):
    def __init__(self):

        self.flag = None

    def work(self, f):
        if self.flag == "4":
            self.contribute(self.driver.separate_step4(), Reducer.sum, f)
        elif self.flag == "6":
            self.contribute(self.driver.separate_step4(), Reducer.sum, f)


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
    #direct_result_future = charm.createFuture()

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

    #direct_result_future.sum_local_exp(local_result_future)

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

    '''

    my_array_3_5_4_6 = Array(MyChare, (3, 2))


    #charm.awaitCreation(my_array)

    from CustomGreen import CustomConstantOneExpansionWrangler
    c = CustomConstantOneExpansionWrangler(tree)
    my_array_3_5_4_6[(0, 0)].summation_setter(driver)#sum direct result
    my_array_3_5_4_6[(0, 0)].flag_setter('sum_3_5')
    my_array_3_5_4_6[(0, 1)].summation_setter(driver)
    my_array_3_5_4_6[(0, 1)].flag_setter("7")
    my_array_3_5_4_6[(1,0)].summation_setter(driver)
    my_array_3_5_4_6[(1,0)].flag_setter('3')
    my_array_3_5_4_6[(1,1)].summation_setter(driver)
    my_array_3_5_4_6[(1,1)].flag_setter("5")
    my_array_3_5_4_6[(2,0)].summation_setter(driver)
    my_array_3_5_4_6[(2,0)].flag_setter("4")
    my_array_3_5_4_6[(2,1)].summation_setter(driver)
    my_array_3_5_4_6[(2,1)].flag_setter("6")

    #direct_result_f = charm.createFuture()
    #local_exps_f = charm.createFuture()
    my_array_3_5_4_6.direct_result(direct_result_f, ret=True)
    my_array_3_5_4_6.sum_local_exp(local_exps_f, ret=True)

    direct_result = direct_result_f.get()
    local_exps = local_exps_f.get()

    end = time()
    print(end - ti)
    local_exps = driver.wrangler.refine_locals(driver.traversal.level_start_target_or_target_parent_box_nrs,
                                             driver.traversal.target_or_target_parent_boxes,
                                             local_exps)
    local_result = driver.wrangler.eval_locals(
        driver.traversal.level_start_target_box_nrs,
        driver.traversal.target_boxes,
        local_exps)
    result = driver.wrangler.reorder_potentials( direct_result + local_result)
    end = time()
    print(end - ti)
    assert (result == 3000000).all()
    exit()
    '''




    #future = my_array.work(li, ret=True)
    #individual = MyChare

    #individual



if __name__ == "__main__":
    charm.start(main)  # call main([]) in interactive mode