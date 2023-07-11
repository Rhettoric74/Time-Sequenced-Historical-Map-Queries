import os
import random
import shutil
import csv
def random_sample(input_dir, output_dir, sample_size):
    """
    Randomly sample a subset of the files in a directory
    :param input_dir: directory containing files to sample from
    :param output_dir: directory to write sampled files to
    :param sample_size: number of files to sample
    :return: None
    """
    files = os.listdir(os.getcwd() + "\\" + input_dir)
    sample = random.sample(files, sample_size)
    os.mkdir(os.getcwd() + "\\" + output_dir)
    for file in sample:
        shutil.copy(os.path.join(input_dir, file), os.getcwd() + "\\" + output_dir + "\\" + file)
def dated_sample(earliest = - float("inf"), latest = 2023):
    """
    Purpose: List all map ids from the David Rumsey collection from a specified time interval
    Parameters: earliest and latest (Numbers) the date bounds to search for
    Returns: A list of map ids with dates between the range
    """
    with open("luna_omo_metadata_56628_20220724.csv", "r", errors="ignore") as fp:
        map_ids = []
        reader = csv.DictReader(fp)
        for row in reader:
            try:
                if float(row["date"]) >= earliest and float(row["date"]) <= latest:
                    map_ids.append(row["filename"])
            except ValueError:
                print("Date could not be converted to integer")
        return map_ids


if __name__ == "__main__":
    print(dated_sample(1941)[1])