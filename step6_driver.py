import math
import numpy as np
class step6_driver:
    def __init__(self,level_start_target_or_target_parent_box_nrs,target_or_target_parent_boxes,
                 from_sep_bigger_starts,from_sep_bigger_lists,src_weights,tree):
        self.level_start_target_or_target_parent_box_nrs = level_start_target_or_target_parent_box_nrs
        self.target_or_target_parent_boxes = target_or_target_parent_boxes
        self.from_sep_bigger_starts = from_sep_bigger_starts
        self.from_sep_bigger_lists = from_sep_bigger_lists
        self.src_weights = src_weights
        self.wrangler = step6_wrangler(tree.nboxes,tree.box_source_starts,tree.box_source_counts_nonchild)

    def multicore_separate_step6(self, total_processors, part):
        return self.wrangler.form_locals_multicore(
            self.level_start_target_or_target_parent_box_nrs,
            self.target_or_target_parent_boxes,
            self.from_sep_bigger_starts,
            self.from_sep_bigger_lists,
            self.src_weights, total_processors, part)
class step6_wrangler:
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

    local_expansion_zeros = multipole_expansion_zeros
    def form_locals_multicore(self,
            level_start_target_or_target_parent_box_nrs,
            target_or_target_parent_boxes, starts, lists, src_weights,total_parts, part):
        local_exps = self.local_expansion_zeros()

        length = math.ceil(self.nboxes / total_parts)

        ops = 0
        seg_start = part * length
        seg_end = seg_start + length

        if part == total_parts - 1:
            seg_end = self.nboxes
        ops = 0


        for itgt_box, tgt_ibox in enumerate(target_or_target_parent_boxes[seg_start:seg_end]):
            itgt_box += seg_start
            start, end = starts[itgt_box:itgt_box+2]

            #print "LIST 4", tgt_ibox, "<-", lists[start:end]
            contrib = 0
            nsrcs = 0
            for src_ibox in lists[start:end]:
                src_pslice = self._get_source_slice(src_ibox)
                nsrcs += src_weights[src_pslice].size

                contrib += np.sum(src_weights[src_pslice])

            local_exps[tgt_ibox] += contrib
            ops += nsrcs

        return local_exps#, self.timing_future(ops)