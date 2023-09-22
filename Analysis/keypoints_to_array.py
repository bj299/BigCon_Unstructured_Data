MAIN_PATH = "C:/Users/lhi30/Haein/2023/YBIGTA/2023-2/DA/Big_Con/Share/"
KEYPOINTS_PATH = MAIN_PATH + "Output_Files/person_keypoints.json"
OUTPATH = MAIN_PATH + "Output_Files/"
import json
import numpy as np
from sklearn.preprocessing import StandardScaler
import os

def open_file(path):

    if os.path.isfile(path):
        with open (path) as json_file:
            data = json.load(json_file)
    else:
        print("Not valid inpath!")
    return data

def dictlist_to_array(dictlist: list) -> np.ndarray:
    num_keypoints = len(dictlist[0].values())
    num_frames = len(dictlist)
    result_array = np.zeros(shape = (num_keypoints, 2 * num_frames))
    for i, keypoint in enumerate(dictlist):
        if(keypoint == -1):
            frame_array = np.zeros(shape = (num_keypoints, 2))
            continue
        frame_array = np.array(list(keypoint.values()))
        print(frame_array.shape)
        result_array[:, 2*i:2*i+2] = frame_array
    return result_array

def save_analysis(data: np.ndarray, outpath, data_name):
    if outpath:
        np.save(file = f"{outpath}{data_name}.npy", arr = data)
    else:
        np.save(file = f"{data_name}.npy", arr = data)
def main():
    person_keypoints = open_file(KEYPOINTS_PATH)
    array_keypoints_0 = dictlist_to_array(person_keypoints[0])
    array_keypoints_1 = dictlist_to_array(person_keypoints[1])

    standardizer = StandardScaler()
    standard_0 = standardizer.fit_transform(array_keypoints_0)
    standard_1 = standardizer.fit_transform(array_keypoints_1)
    final = np.concatenate((standard_0, standard_1), axis = 0)
    save_analysis(final, outpath = OUTPATH, data_name = "numpy_array")

if __name__ == "__main__":
    main()