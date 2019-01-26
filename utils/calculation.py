"""
Handles calculation related tasks
"""

import random


class Calculation:
    """ Class for calculations """
    def __init__(self):
        pass

    def get_download_sizes_list(self, filesize, parts):
        """ function to get a list of sizes to be downloaded by each thread """
        # no of bytes per thread
        size_per_thread = filesize//parts
        # stores size to be downloaded by each thread
        sizes_list = [size_per_thread] * parts
        # remaining size not assigned to any thread
        rem = filesize % parts
        # loop to equally assign sizes to download, to each thread
        index = 0
        while rem != 0:
            sizes_list[index] += 1
            rem -= 1
            index += 1

        return sizes_list

    def get_download_ranges_list(self, range_left, range_right, parts):
        """ function to get a list of ranges to be downloaded by each thread """

        filesize = range_right - range_left + 1
        sizes_list = self.get_download_sizes_list(filesize, parts)
        sizes_list.insert(0, 0)

        index = 2
        while index < len(sizes_list):
            sizes_list[index] += sizes_list[index - 1]
            index += 1

        # list storing tuples of byte-ranges
        ranges_list = []
        index = 1
        while index < len(sizes_list):
            ranges_list.append(
                (range_left + sizes_list[index - 1], range_left + sizes_list[index] - 1)
            )
            index += 1

        return ranges_list

    def generate_random_string(self, length):
        """ function to generate a random alphanumeric string of given length """

        alphabets = [
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
            '1', '2', '3', '4', '5', '6', '7', '8', '9', '0'
        ]

        max_length = 62

        name = ''
        index = random.randint(0, 37273729)

        for _ in range(length):
            index = (index + 6268282) % max_length
            name += alphabets[index]
        return name
