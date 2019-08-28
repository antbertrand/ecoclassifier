import json
import os


import pandas as pd
import numpy as np


# Prepare our training / validation / etc set
def renameData():
    filename = "./dataset/majurca-ecoclassifier-assets.json"

    # Read JSON data into the datastore variable
    if filename:
        with open(filename, "r") as f:
            list_info = json.load(f)

    output_dir = "./dataset_renamed"
    print(len(list_info))
    # Create folder for the test and training split
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

        k = 0
        j = 0

        for dict in list_info:
            print(k)
            if dict["thumbnail_320x200"] != None:
                cam = dict["path"].replace("192-168-0-31", "1")
                cam = cam.replace("192-168-0-32", "2")
                cam = cam.replace("acquisitions", "")
                if dict["tag_slugs"] != []:
                    new_name = cam[:-4] + "_" + dict["tag_slugs"][0] + ".png"

                else:
                    new_name = cam[:-4] + "_" + "not-labeled" + ".png"

                # print(new_name)

                new_path = output_dir + new_name
                name = dict["thumbnail_320x200_path"]
                path = "./dataset/" + name
                # print(k)
                print("cp " + path + " " + new_path)
                os.system("cp " + path + " " + new_path)
                k = k + 1

            else:
                j = j + 1
        print("Done")
        print(k)


renameData()
