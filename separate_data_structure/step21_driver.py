import math
import numpy as np
class step21_driver:
    def __init__(self,level_start_source_box_nrs,source_boxes,src_weights,tree):
        self.level_start_source_box_nrs = level_start_source_box_nrs
        self.source_boxes = source_boxes
        self.src_weights = src_weights
        self.wrangler = step21_wrangler(tree.nboxes,tree.box_source_starts,tree.box_source_counts_nonchild)
    def multicore_step21(self,total_processors,part):
        return self.wrangler.multicore_form_multipoles(
            self.traversal.level_start_source_parent_box_nrs,
            self.traversal.source_parent_boxes,
            self.mpole_exps,total_processors,part)

class step21_wrangler:
    def __init__(self,nboxes,box_source_starts,box_source_counts_nonchild):
        self.box_source_starts = box_source_starts
        self.box_source_counts_nonchild = box_source_counts_nonchild
        self.nboxes = nboxes
        pass
    def multipole_expansion_zeros(self):
        return np.zeros(self.nboxes, dtype=np.float64)
    def _get_source_slice(self, ibox):
        pstart = self.box_source_starts[ibox]
        return slice(
                pstart, pstart + self.box_source_counts_nonchild[ibox])

    def multicore_form_multipoles(self, level_start_source_box_nrs, source_boxes, src_weights,total_processors,part):
        mpoles = self.multipole_expansion_zeros()
        ops = 0
        length = math.ceil(self.nboxes / total_processors)

        ops = 0
        seg_start = part * length
        seg_end = seg_start + length
        if part == total_processors - 1:
            seg_end = self.nboxes

        for ibox in source_boxes[seg_start:seg_end]:
            pslice = self._get_source_slice(ibox)
            mpoles[ibox] += np.sum(src_weights[pslice])
            ops += src_weights[pslice].size

        return mpoles#, self.timing_future(ops)