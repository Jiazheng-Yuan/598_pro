import math
import numpy as np
class step3_driver:
    def __init__(self,target_boxes,neighbor_source_boxes_starts,neighbor_source_boxes_lists,src_weights,tree):
        self.target_boxes = target_boxes
        self.neighbor_source_boxes_starts = neighbor_source_boxes_starts
        self.neighbor_source_boxes_lists = neighbor_source_boxes_lists
        self.src_weights = src_weights
        self.wrangler = step3_or_5_wrangler(tree.nboxes,tree.ntargets,
                                       tree.box_source_starts,tree.box_source_counts_nonchild,tree.box_target_starts,
                                       tree.box_target_counts_nonchild)
    def multicore_step3(self,total_processors,part):
        direct_interaction = self.wrangler.eval_direct_multicore(
            self.target_boxes,
            self.neighbor_source_boxes_starts,
            self.neighbor_source_boxes_lists,
            self.src_weights,total_processors,part)

        # self.recorder.add("eval_direct", self.timing_future)
        return direct_interaction


class step3_or_5_wrangler:
    def __init__(self,nboxes,ntargets,box_source_starts,box_source_counts_nonchild,box_target_starts,box_target_counts_nonchild):
        self.nboxes = nboxes
        self.ntargets = ntargets
        self.box_source_starts = box_source_starts
        self.box_source_counts_nonchild = box_source_counts_nonchild
        self.box_target_starts = box_target_starts
        self.box_target_counts_nonchild = box_target_counts_nonchild

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
    def eval_direct_multicore(self,target_boxes, neighbor_sources_starts,
            neighbor_sources_lists, src_weights, total_parts, part):
        from time import time
        ti = time()
        pot = self.output_zeros()

        length = math.ceil(self.nboxes / total_parts)


        ops = 0
        seg_start = part * length
        seg_end = seg_start + length

        if part == total_parts - 1:
            seg_end = self.nboxes
        #print("total number of boxes is " + str(self.tree.nboxes) + ",start at :" + str(seg_start) + "    end at: " + str(seg_end))
        for itgt_box, tgt_ibox in enumerate(target_boxes[seg_start:seg_end]):
            itgt_box += seg_start
            tgt_pslice = self._get_target_slice(tgt_ibox)

            src_sum = 0
            nsrcs = 0
            start, end = neighbor_sources_starts[itgt_box:itgt_box + 2]
            # print "DIR: %s <- %s" % (tgt_ibox, neighbor_sources_lists[start:end])
            for src_ibox in neighbor_sources_lists[start:end]:
                src_pslice = self._get_source_slice(src_ibox)
                nsrcs += src_weights[src_pslice].size

                src_sum += np.sum(src_weights[src_pslice])

            pot[tgt_pslice] = src_sum
            ops += pot[tgt_pslice].size * nsrcs
        #print("executing direct eval for part"+str(part)+": "+str(time() - ti))
        #print(pot)
        return pot  # , self.timing_future(ops)
