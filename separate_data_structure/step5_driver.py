import math
import numpy as np
from step3_driver import step3_or_5_wrangler
class step5_with_extent_driver:
    def __init__(self,target_boxes,from_sep_close_smaller_starts,from_sep_close_smaller_lists,src_weights,tree):
        self.target_boxes = target_boxes
        self.from_sep_close_smaller_starts = from_sep_close_smaller_starts
        self.from_sep_close_smaller_lists = from_sep_close_smaller_lists
        self.src_weights = src_weights
        self.wrangler = step3_or_5_wrangler(tree.nboxes,tree.ntargets,
                                       tree.box_source_starts,tree.box_source_counts_nonchild,tree.box_target_starts,
                                       tree.box_target_counts_nonchild)
    def step5_with_extent(self,total_processors,part):

        if self.from_sep_close_smaller_starts is not None:

            direct_result = self.wrangler.eval_direct_multicore(
                self.target_boxes,
                self.from_sep_close_smaller_starts,
                self.from_sep_close_smaller_lists,
                self.src_weights,total_processors,part)


            return direct_result
        return None
