from __future__ import absolute_import
# STARTEXAMPLE
import pyopencl as cl
import numpy as np
from six.moves import range

def foo():
    print("a")
if __name__ == "__main__":

    ctx = cl.create_some_context()
    queue = cl.CommandQueue(ctx)

    dims = 2
    nparticles = 16

    # -----------------------------------------------------------------------------
    # generate some random particle positions
    # -----------------------------------------------------------------------------
    from pyopencl.clrandom import RanluxGenerator
    rng = RanluxGenerator(queue, seed=15)

    from pytools.obj_array import make_obj_array
    particles = make_obj_array([
        rng.normal(queue, nparticles, dtype=np.float64)
        for i in range(dims)])

    # -----------------------------------------------------------------------------
    # build tree and traversals (lists)
    # -----------------------------------------------------------------------------
    from boxtree import TreeBuilder
    tb = TreeBuilder(ctx)

    tree, _ = tb(queue, particles, max_particles_in_box=5,kind='non-adaptive')

    from boxtree.traversal import FMMTraversalBuilder
    #from boxtree.traversal import FMMTraversalInfo

    tg = FMMTraversalBuilder(ctx)
    trav, _ = tg(queue, tree)
    ctree = tree.get(queue)
    print(ctree.box_child_ids[:,1])
    print(ctree.box_parent_ids)

    '''
    print(ctree.nlevels)
    print(ctree.nboxes)
    print(ctree.box_source_starts)
    print(ctree.box_source_counts_cumul)

    ctrav = trav.get(queue)
    '''
    #print(ctrav.source_boxes)
    #print(ctrav.neighbor_source_boxes_lists)
    #print(ctrav.neighbor_source_boxes_starts)


    # ENDEXAMPLE

    # -----------------------------------------------------------------------------
    # plot the tree
    # -----------------------------------------------------------------------------

    import matplotlib.pyplot as pt

    pt.plot(particles[0].get(), particles[1].get(), "+")


    from boxtree.visualization import TreePlotter
    plotter = TreePlotter(tree.get(queue=queue))
    plotter.draw_tree(fill=False, edgecolor="black")
    #plotter.draw_box_numbers()
    plotter.set_bounding_box()
    pt.gca().set_aspect("equal")
    pt.tight_layout()
    pt.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom='off',      # ticks along the bottom edge are off
        top='off',         # ticks along the top edge are off
        labelbottom='off')
    pt.tick_params(
        axis='y',
        which='both',
        left='off',
        top='off',
        labelleft='off')
    pt.show()
    pt.savefig("tree.pdf")