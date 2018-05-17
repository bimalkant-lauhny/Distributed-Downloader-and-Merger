
class Calculation:
    """ Class for calculations """
    def __init__(self):
        pass

    # function to get a list of sizes to be downloaded by each thread
    def getDownloadSizesList(self, filesize, parts):
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

    # function to get a list of ranges to be downloaded by each thread
    def getDownloadRangesList(self, range_left, range_right, parts):

        filesize = range_right - range_left + 1
        sizes_list = self.getDownloadSizesList(filesize, parts)
        sizes_list.insert(0, 0)

        index = 2 
        while index < len(sizes_list):
            sizes_list[index] += sizes_list[index - 1]
            index += 1

        # list storing tuples of byte-ranges
        ranges_list = []
        index = 1
        while index < len(sizes_list):
            ranges_list.append((range_left + sizes_list[index - 1],range_left + sizes_list[index] - 1))
            index += 1

        return ranges_list