from time import time
from datetime import timedelta
import os


# Modified from https://github.com/shackenberg/pbar.py/blob/master/pbar.py
class ProgressBar(object):
    def __init__(
        self,
        max_value,
        title=None,
        start_state=0,
        max_refreshrate=0.3,
        zero_index=True,
        width=None,
    ):
        self.width = width
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
        if self.width is not None:
            return self.width
        else:
            try:
                return self.get_width_of_terminal()
            except:
                rule_of_thumb_standard_value = 80
                return rule_of_thumb_standard_value

    def get_width_of_terminal(self):
        _, ncolumns = os.popen("stty size", "r").read().split()
        width = int(ncolumns)
        return width

    def prepare_title(self, title):
        if title is None:
            return ""
        else:
            return title + os.linesep

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

    def computed_estimate_time_left(self, complete_elapsed_time):
        estimated_time_left = complete_elapsed_time * (
            self.max_value / float(self.state) - 1
        )
        return estimated_time_left

    def build_output_string(self, current_time):
        self.length = self.determine_length_pbar()
        progress = int(round(self.state * 100.0 / self.max_value))
        complete_elapsed_time = current_time - self.start_time
        # time format has always 7 letters: `0:00:00`
        time_len = len("0:00:00")
        complete_elapsed_time_pretty = (
            f"{self.time_div_to_short_str(complete_elapsed_time):>{time_len}}"
        )

        if (complete_elapsed_time > 3) & (self.state > 0):
            estimated_time_left = self.computed_estimate_time_left(
                complete_elapsed_time
            )
            estimated_time_left_pretty = (
                f" - {self.time_div_to_short_str(estimated_time_left)} remaining"
            )
        else:
            estimated_time_left_pretty = ""

        # remaining time format has always 20 letters: ` - 0:00:00 remaining"
        remaining_len = len(" - 0:00:00 remaining")
        estimated_time_left_pretty_formatted = (
            f"{estimated_time_left_pretty:>{remaining_len}}"
        )

        # progress string has max 3 digits (100%)
        progress_str = f" {progress:3d}% in "

        len_of_brackets = 2
        len_backticks = 2
        overhead = (
            len_of_brackets
            + len_backticks
            + len(progress_str)
            + len(complete_elapsed_time_pretty)
            + len(estimated_time_left_pretty_formatted)
        )

        max_bar_length = self.length - overhead
        bar_length = int(progress * max_bar_length / 100)
        filled = "#" * bar_length
        progressbar_string = f"[{filled:<{max_bar_length}}]"

        backtick = "`"

        ordered_output_string_fields = [
            os.linesep,
            self.title,
            backtick,
            progressbar_string,
            progress_str,
            complete_elapsed_time_pretty,
            estimated_time_left_pretty_formatted,
            backtick,
        ]

        output_string = "".join(ordered_output_string_fields)

        self.old_length = self.length

        return output_string

    def print_pbar(self, output_string):
        return output_string

    def jump_to_newline(self):
        print
