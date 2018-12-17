import math
import numpy as np
class step4_driver:
    def __init__(self,nboxes,level_start_target_or_target_parent_box_nrs,target_or_target_parent_boxes,
                 from_sep_siblings_starts,from_sep_siblings_lists,mpole_exps,tree):
        self.nboxes = nboxes
        self.level_start_target_or_target_parent_box_nrs = level_start_target_or_target_parent_box_nrs
        self.target_or_target_parent_boxes = target_or_target_parent_boxes
        self.from_sep_siblings_starts = from_sep_siblings_starts
        self.from_sep_siblings_lists = from_sep_siblings_lists
        self.mpole_exps = mpole_exps
    def multicore_separate_step4(self,total_processors,part):
        return self.wrangler.multipole_to_local_multicore(
            self.traversal.level_start_target_or_target_parent_box_nrs,
            self.traversal.target_or_target_parent_boxes,
            self.traversal.from_sep_siblings_starts,
            self.traversal.from_sep_siblings_lists,
            self.mpole_exps,total_processors,part)


class step4_wrangler:
    def __init__(self,nboxes,level_start_target_or_target_parent_box_nrs,target_or_target_parent_boxes,
                 from_sep_siblings_starts,from_sep_siblings_lists,mpole_exps,tree):
        self.nboxes = nboxes
        self.level_start_target_or_target_parent_box_nrs = level_start_target_or_target_parent_box_nrs
        self.target_or_target_parent_boxes = target_or_target_parent_boxes
        self.from_sep_siblings_starts = from_sep_siblings_starts
        self.from_sep_siblings_lists = from_sep_siblings_lists
        self.mpole_exps = mpole_exps

    def multipole_expansion_zeros(self):
        return np.zeros(self.tree.nboxes, dtype=np.float64)

    local_expansion_zeros = multipole_expansion_zeros

    def _get_source_slice(self, ibox):
        pstart = self.box_source_starts[ibox]
        return slice(
            pstart, pstart + self.box_source_counts_nonchild[ibox])

    def _get_target_slice(self, ibox):
        pstart = self.box_target_starts[ibox]
        return slice(
            pstart, pstart + self.box_target_counts_nonchild[ibox])
    def output_zeros(self):
        return np.zeros(self.ntargets, dtype=np.float64)

    def multipole_to_local_multicore(self,
                           level_start_target_or_target_parent_box_nrs,
                           target_or_target_parent_boxes,
                           starts, lists, mpole_exps,total_parts, part):
        local_exps = self.local_expansion_zeros()

        length = math.ceil(self.tree.nboxes / total_parts)


        seg_start = part * length
        seg_end = seg_start + length

        if part == total_parts - 1:
            seg_end = self.tree.nboxes
        ops = 0
        for itgt_box, tgt_ibox in enumerate(target_or_target_parent_boxes[seg_start:seg_end]):
            itgt_box +=seg_start
            start, end = starts[itgt_box:itgt_box + 2]

            contrib = 0
            # print tgt_ibox, "<-", lists[start:end]
            for src_ibox in lists[start:end]:
                contrib += mpole_exps[src_ibox]
                ops += 1

            local_exps[tgt_ibox] += contrib

        return local_exps  # , self.timing_future(ops)