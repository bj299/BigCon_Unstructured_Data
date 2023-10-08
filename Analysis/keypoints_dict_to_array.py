MAIN_PATH = "C:/Users/lhi30/Haein/2023/YBIGTA/2023-2/DA/Big_Con/Share/"
KEYPOINTS_PATH = MAIN_PATH + "Data/more_json/"
OUTPATH = MAIN_PATH + "Output_Files/Numpy/"
import json
from sklearn.preprocessing import StandardScaler
import os
import numpy as np
from pathlib import Path

def get_json_list(path):
    if os.path.isdir(path):
        json_path_list = os.listdir(path)
    else:
        print("Not valid inpath!")
        return
    return json_path_list
def get_json_file(json_path, inpath):
    if Path(json_path).suffix == ".json":
        with open (inpath + json_path) as json_file:
            alphapose_raw = json.load(json_file)
        return alphapose_raw
    else:
        print("There's a file that isn't a json file!")
        return

def dictlist_to_array(dictlist: list) -> np.ndarray:
    num_keypoints = 17
    num_frames = len(dictlist)
    result_array = np.zeros(shape = (num_keypoints, 2 * num_frames))
    for i, keypoint in enumerate(dictlist):
        if(keypoint == -1):
            frame_array = np.zeros(shape = (num_keypoints, 2))
            continue
        frame_array = np.array(list(keypoint.values()))
        result_array[:, 2*i:2*i+2] = frame_array
    return result_array

def save_analysis(data: np.ndarray, outpath, data_name):
    if outpath:
        np.save(file = f"{outpath}{data_name}.npy", arr = data)
    else:
        np.save(file = f"{data_name}.npy", arr = data)
def main():
    keypoints_folder = get_json_list(KEYPOINTS_PATH)
    print(keypoints_folder)
    for path in keypoints_folder:
        person_keypoints = get_json_file(path, KEYPOINTS_PATH)
        array_keypoints_0 = dictlist_to_array(person_keypoints['0'])
        array_keypoints_1 = dictlist_to_array(person_keypoints['1'])

        standardizer = StandardScaler()
        standard_0 = standardizer.fit_transform(array_keypoints_0)
        standard_1 = standardizer.fit_transform(array_keypoints_1)
        final = np.concatenate((standard_0, standard_1), axis = 0)
        save_analysis(final, outpath = OUTPATH, data_name = f"{path[:-5]}")

if __name__ == "__main__":
    main()