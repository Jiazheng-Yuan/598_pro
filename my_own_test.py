

__copyright__ = "Copyright (C) 2013 Andreas Kloeckner"

__license__ = """
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from six.moves import range

import numpy as np
import numpy.linalg as la
import pyopencl as cl

import pytest
from pyopencl.tools import (  # noqa
        pytest_generate_tests_for_pyopencl as pytest_generate_tests)

from boxtree.tools import (  # noqa: F401
        make_normal_particle_array as p_normal,
        make_surface_particle_array as p_surface,
        make_uniform_particle_array as p_uniform,
        particle_array_to_host,
        ConstantOneExpansionWrangler)
from CustomGreen import CustomConstantOneExpansionWrangler

import logging
logger = logging.getLogger(__name__)


# {{{ fmm interaction completeness test
class Mytest:

    def __init__(self,ctx_getter=cl.create_some_context, enable_extents=False):
        ctx = ctx_getter()
        queue = cl.CommandQueue(ctx)

        from pyopencl.characterize import has_struct_arg_count_bug
        if has_struct_arg_count_bug(queue.device):
            pytest.xfail("won't work on devices with the struct arg count issue")

        logging.basicConfig(level=logging.INFO)

        dims = 2
        nsources = 3000000
        ntargets = 3000000
        dtype = np.float32

        from boxtree.fmm import drive_fmm
        sources = p_normal(queue, nsources, dims, dtype, seed=15)
        targets = p_normal(queue, ntargets, dims, dtype, seed=15)

        from pyopencl.clrandom import PhiloxGenerator
        rng = PhiloxGenerator(queue.context, seed=12)

        if enable_extents:
            target_radii = 2**rng.uniform(queue, ntargets, dtype=dtype, a=-10, b=0)
        else:
            target_radii = None

        from boxtree import TreeBuilder
        tb = TreeBuilder(ctx)

        tree, _ = tb(queue, sources,
                max_particles_in_box=30,
                #target_radii=target_radii,
                debug=True) #stick_out_factor=0.25)

        from boxtree.traversal import FMMTraversalBuilder
        tbuild = FMMTraversalBuilder(ctx)
        trav, _ = tbuild(queue, tree, debug=True)


        weights = np.ones(nsources)
        weights_sum = np.sum(weights)

        host_trav = trav.get(queue=queue)
        host_tree = host_trav.tree
        self.tree = host_tree
        self.trav = host_trav

        self.input = [host_tree,weights,weights_sum,host_trav]
        self.pot = None


    '''

    wrangler = ConstantOneExpansionWrangler(host_tree)
    #print(host_tree)

    pot = drive_fmm(host_trav, wrangler, weights)

    assert (pot == weights_sum).all()
    '''
    #return [host_tree,weights,weights_sum,host_trav]
    def cal(self):
        input = self.input
        host_tree, weights, weights_sum, host_trav = input
        from boxtree.fmm import drive_fmm
        wrangler = CustomConstantOneExpansionWrangler(host_tree)
        #print(host_tree)

        #pot = drive_fmm(host_trav, wrangler, weights)
        #assert (pot == weights_sum).all()

        from my_own_fmm import My_own_fmm
        driver = My_own_fmm(host_trav,wrangler,weights,self)
        return driver


    def check(self):
        assert (self.pot == self.input[2]).all()

# }}}


# You can test individual routines by typing
# $ python test_fmm.py 'test_routine(cl.create_some_context)'

if __name__ == "__main__":
    import sys
    '''
    if len(sys.argv) > 1:
        exec(sys.argv[1])
    else:
        from pytest import main
        main([__file__])
        '''

    mt = Mytest()
    d = mt.cal()


    d.step21()
    d.step22()
    d.step3()
    d.step4()
    d.step6()
    d.step7()
    d.step5()

    d.step8()
    #Process(target=d.step9()).start()
    mt.check()


# vim: fdm=marker