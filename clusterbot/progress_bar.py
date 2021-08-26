from time import time
from datetime import timedelta
import os


# Modified from https://github.com/shackenberg/pbar.py/blob/master/pbar.py
class ProgressBar(object):
    def __init__(self, max_value, title=None, start_state=0,
                 max_refreshrate=0.3, zero_index=True):
        self.max_value = max_value
        self.start_time = time()
        self.state = start_state
        self.old_length = self.determine_length_pbar()
        self.title = self.prepare_title(title)
        self.time_last_update = 0
        self.max_refreshrate = max_refreshrate
        self.is_last_update = False
        self.zero_index = zero_index

    def init(self):
        output_string = self.build_output_string(time())
        return self.print_pbar(output_string)

    def determine_length_pbar(self):
        try:
            return self.get_width_of_terminal()
        except:
            rule_of_thumb_standard_value = 80
            return rule_of_thumb_standard_value

    def get_width_of_terminal(self):
        _, ncolumns = os.popen('stty size', 'r').read().split()
        width = int(ncolumns)
        return width

    def prepare_title(self, title):
        if title is None:
            return ''
        else:
            return title + ' '

    def update(self, current_value=None):
        if current_value is None:
            self.state += 1
        else:
            if self.zero_index:
                self.state = current_value + 1
            else:
                self.state = current_value
        if self.state > self.max_value:
            raise ValueError("state >= max_value")
        current_time = time()
        time_since_last_update = current_time - self.time_last_update
        if self.state == self.max_value:
            self.is_last_update = True
        if (time_since_last_update > self.max_refreshrate) | self.is_last_update:
            output_string = self.build_output_string(current_time)
            self.time_last_update = current_time
            return self.print_pbar(output_string)
        if self.is_last_update:
            self.jump_to_newline()

    def time_div_to_short_str(self, time_div):
        return str(timedelta(seconds=round(time_div)))

    def compute_bar_length(self, overhead, progress):
        max_bar_length = self.length - overhead
        return progress * max_bar_length / 100

    def compute_filling_length(self, overhead, progress):
        max_bar_length = self.length - overhead
        bar_length = progress * max_bar_length / 100
        return max_bar_length - bar_length

    def computed_estimate_time_left(self, complete_elapsed_time):
        estimated_time_left = complete_elapsed_time * (self.max_value / float(self.state) - 1)
        return estimated_time_left

    def build_output_string(self, current_time):
        self.length = self.determine_length_pbar()
        progress = int(round(self.state * 100.0 / self.max_value))
        complete_elapsed_time = current_time - self.start_time
        complete_elapsed_time_pretty = self.time_div_to_short_str(complete_elapsed_time)

        if (complete_elapsed_time > 3) & (self.state > 0):
                estimated_time_left = self.computed_estimate_time_left(complete_elapsed_time)
                estimated_time_left_pretty = self.time_div_to_short_str(estimated_time_left)
                estimated_time_left_pretty_formatted = " - " + estimated_time_left_pretty + " remaining"
        else:
                estimated_time_left_pretty_formatted = ''
        progress_str = " " + str(progress) + "% in "
        len_of_brackets = 2
        overhead = len_of_brackets + \
                   len(progress_str) + \
                   len(complete_elapsed_time_pretty) + \
                   len(self.title) + \
                   len(estimated_time_left_pretty_formatted)
        bar_length = self.compute_bar_length(overhead, progress)
        filling_length = self.compute_filling_length(overhead, progress)
        progressbar_string = '[' + '#' * int(bar_length) + ' ' * int(filling_length) + ']'

        complete_elapsed_time_pretty = str(complete_elapsed_time_pretty)

        if self.length == self.length:
            carriage_return = "\r"
        else:
            carriage_return = '\n'

        ordered_output_string_fields = [carriage_return,
                                self.title,
                                progressbar_string,
                                progress_str,
                                complete_elapsed_time_pretty,
                                estimated_time_left_pretty_formatted]

        output_string = "".join(ordered_output_string_fields)

        self.old_length = self.length

        return output_string

    def print_pbar(self, output_string):
        return output_string

    def jump_to_newline(self):
        print
