# reduction.py
from charm4py import charm, Chare, Group, Reducer

class MyChare(Chare):

    def work(self, data):
        self.contribute(data, Reducer.sum, self.thisProxy[0].collectResult)

    def collectResult(self, result):
        print("Result is", result)
        exit()

def main(args):
    my_group = Group(MyChare)
    my_group.work([2,2,2])

charm.start(main)  # call main([]) in interactive mode