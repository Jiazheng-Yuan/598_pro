from typing import Type


from charm4py import charm, Chare, Group, Reducer,Array
from my_own_test import Mytest
import numpy as np
from boxtree import *
from my_own_fmm import *
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

    def direct_result(self):
        #print(str(self.thisIndex) + "   " + str(charm.myPe()))

        if self.flag == "3":
            print("step3")
            self.contribute(self.driver.step3(), Reducer.sum, self.thisProxy[(0,0)].direct_result_sum)

        elif self.flag == "5":
            #print("adjnaskaajsdnkjsanksaksnkajnk")
            print("step5")
            self.contribute(self.driver.step5(), Reducer.sum, self.thisProxy[(0, 0)].direct_result_sum)
        #else:
        #    self.contribute(np.zeros(3000000), Reducer.sum, f)

    def direct_result_sum(self, result):
        print(self.flag)
        if self.flag == "7":
            evluated_exp = self.driver.wrangler.eval_locals(
                self.driver.traversal.level_start_target_box_nrs,
                self.driver.traversal.target_boxes,
                result)
            self.contribute(evluated_exp, Reducer.sum, self.thisProxy[(0, 0)].total_sum)
        else:
            self.contribute(result,Reducer.sum,self.thisProxy[(0, 0)].total_sum)

    def total_sum(self,result):
        result = self.driver.wrangler.reorder_potentials(result)
        end = time()
        print(end - self.time)
        assert (result == 300).all()

    def sum_local_exp(self):
        print(str(self.thisIndex) + "   " + str(charm.myPe()))
        if self.flag == "4":
            print("step4")
            self.contribute(self.driver.step4(), Reducer.sum, self.thisProxy[(0, 1)].direct_result_sum)

        elif self.flag == "6":
            # print("adjnaskaajsdnkjsanksaksnkajnk")
            print("step6")
            self.contribute(self.driver.step6(), Reducer.sum, self.thisProxy[(0, 1)].direct_result_sum)
        #else:
        #    self.contribute(np.zeros(3000000), Reducer.sum, f)



def hello(args):
    my_group = Group(MyChare)
    my_group.work(3)

class local_exp_eval(Chare):
    def __init__(self):

        self.flag = None
    def work(self, f):
        if self.flag == "4":
        #print("step4")
        # self.driver.step4()
        # self.driver.step6()
            self.contribute(self.driver.step4(), Reducer.sum, f)

        elif self.flag == "6":
        #print("step6")
            self.contribute(self.driver.step6(), Reducer.sum, f)


def main(args):
    my = Mytest()
    tree = my.tree
    driver = my.cal()


    ti = time()
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

    my_array_3_5_4_6 = Array(MyChare, (3, 2))
    my_array_3_5_4_6[(1, 0)].summation_setter(driver)
    my_array_3_5_4_6[(1, 0)].flag_setter('3')
    my_array_3_5_4_6[(1,0)].direct_result()
    driver.step21()
    driver.step22()

    #charm.awaitCreation(my_array)

    from CustomGreen import CustomConstantOneExpansionWrangler
    c = CustomConstantOneExpansionWrangler(tree)
    my_array_3_5_4_6[(0, 0)].summation_setter(driver)#sum direct result
    my_array_3_5_4_6[(0, 0)].flag_setter('sum_3_5')
    my_array_3_5_4_6[(0, 1)].summation_setter(driver)
    my_array_3_5_4_6[(0, 1)].flag_setter("7")

    my_array_3_5_4_6[(1, 1)].summation_setter(driver)
    my_array_3_5_4_6[(1, 1)].flag_setter("5")
    my_array_3_5_4_6[(2, 0)].summation_setter(driver)
    my_array_3_5_4_6[(2, 0)].flag_setter("4")
    my_array_3_5_4_6[(2, 1)].summation_setter(driver)
    my_array_3_5_4_6[(2, 1)].flag_setter("6")
    my_array_3_5_4_6[(1, 1)].direct_result()
    my_array_3_5_4_6[(2, 0)].sum_local_exp()
    my_array_3_5_4_6[(2, 1)].sum_local_exp()

    #direct_result_f = charm.createFuture()
    #local_exps_f = charm.createFuture()



    #exit()





    #future = my_array.work(li, ret=True)
    #individual = MyChare

    #individual



if __name__ == "__main__":
    charm.start(main)  # call main([]) in interactive mode