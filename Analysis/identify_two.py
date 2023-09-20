import json
import numpy as np
import collections
import argparse
import os
import traceback

MAIN_PATH = "C:/Users/lhi30/Haein/2023/YBIGTA/2023-2/DA/Big_Con/Share/"
KEYPOINTS_KEYS = {
    0: "Nose",
    1: "LEye",
    2: "REye",
    3: "LEar",
    4: "REar",
    5: "LShoulder",
    6: "RShoulder",
    7: "LElbow",
    8: "RElbow",
    9: "LWrist",
    10: "RWrist",
    11: "LHip",
    12: "RHip",
    13: "LKnee",
    14: "RKnee",
    15: "LAnkle",
    16: "RAnkle",
}
def get_args():
    parser = argparse.ArgumentParser()
    default_inpath = MAIN_PATH + "Data/alphapose_1.json"
    default_outpath = MAIN_PATH + "Output_Files/"
    parser.add_argument("--inpath", 
                        default = default_inpath,
                        help = "alphapose results path")
    parser.add_argument("--outpath",
                        required = False,
                        default = default_outpath,
                        help = "where to store the processed results")
    args = parser.parse_args()
    return args

def assign_keypoints(keypoints: list[int]) -> dict:
    num_kpoints = len(keypoints) // 3
    kp_dict = collections.defaultdict(list)
    for id in range(num_kpoints):
        x_id = id * 3
        y_id = x_id + 1
        c_id = x_id + 2
        kp_dict[id] = [keypoints[x_id], keypoints[y_id]]
    return kp_dict
def change_keys(og_dict: dict, key_dict: dict) -> dict:
    new_dict = {}
    for k, v in og_dict.items():
        new_dict[key_dict[k]] = v
    return new_dict
def get_num_bodies(result_dict: dict) -> dict:
    num_bodies = {}
    for k, v in result_dict.items():
        num_bodies[k] = len(v)
    return num_bodies

def open_process_file(path, label = True, get_num = False) -> dict:
    """
    Opens the Alphapose result json file from "path", and transforms into a format easier to work with.
    path: Contains path to Alphapose result json file. Assumed to be in COCO format.
    label: If True, returns the body-part names inside the dictionary too
    get_num: If True, returns how many bodies were recognized in frame, in a separate dictionary. Returns (result_dict, num_bodies)
    """
    if os.path.isfile(path):
        with open (path) as json_file:
            data = json.load(json_file)
    else:
        print("Not valid inpath!")
    result_dict = collections.defaultdict(list)
    for item in data:
        image_id = int(item['image_id'][:-4])
        if label:
            kp = assign_keypoints(item['keypoints'])
            result_dict[image_id].append({
                'keypoints_int': kp,
                'keypoints_name': change_keys(kp, KEYPOINTS_KEYS),
                'box': item['box']
            })
        else:
            result_dict[image_id].append({
                'keypoints_int': assign_keypoints(item['keypoints']),
                'box': item['box'],
            })
    if get_num:
        num_bodies = get_num_bodies(result_dict)
        return (result_dict, num_bodies)
    return result_dict


def calculate_distance(current_body: dict, previous_body: dict) -> float:
    """
    A function that calculates the mean euclidean distance between two bodies' keypoints. 

    Inputs:
    current_body: Contains keypoints for a body in the current frame.
    previous_body: Contains keypoints for a body in the previous frame.
    Output:
    mean_distance: Arithmetic mean of euclidean distance between two body keypoints.
    """
    if not (current_body or previous_body):
        return np.inf
    current_body = np.array(list(current_body.values()))
    previous_body = np.array(list(previous_body.values()))
    # Converted keypoints dictionary to numpy arrays for ease of calculation

    xy_distance = current_body - previous_body
    # Just simple difference between x coordinates and y coordinates
    x_dist_square = np.square(xy_distance[:, 0])
    y_dist_square = np.square(xy_distance[:, 1])
    distances = np.sqrt(x_dist_square + y_dist_square)
    mean_distance = np.mean(distances)
    # Calculated mean euclidean distance between keypoints
    return mean_distance

def return_nan(person_to_id: dict):
    for id_list in person_to_id.values():
        id_list.append(np.nan)
    return person_to_id

def assign_first_time(person_to_id: dict, keypoints_list: list):
    person_to_id[0].append(0)
    person_to_id[1].append(1)
    keypoints_0 = keypoints_list[0]['keypoints_int']
    keypoints_1 = keypoints_list[1]['keypoints_int']
    last_assigned = {0: (0, keypoints_0),
                     1: (1, keypoints_1)}
    return person_to_id, last_assigned

def calculate_all_distances(keypoints_list, last_assigned):
    distances = {}
    for body_id, keypoints_dict in enumerate(keypoints_list):
        current_keypoints = keypoints_dict['keypoints_int']
        per_body_dist = [-1, -1, -1]

        for person_id, info in last_assigned.items():
            prev_keypoints = info[1]
            per_body_dist[person_id] = calculate_distance(current_keypoints, prev_keypoints)

        per_body_dist[2] = min(per_body_dist[:2])
        distances[body_id] = per_body_dist

    return distances

def keep_only_two(distances):
    while len(distances) > 2:
        max_dist = 0
        for body_id, dists in distances.items():
            if max_dist < dists[2]:
                max_dist = dists[2]
                max_body = body_id
        distances.pop(max_body)
    return distances

def assign(person_to_id, keypoints_list, distances, last_assigned):
    assigned = {}
    body_ids = []
    for body_id, dists in distances.items():
        if dists[0] < dists[1]:
            assigned[body_id] = 0
        else:
            assigned[body_id] = 1
    assigned_to = set(assigned.values())
    if len(assigned_to) < 2:
        # both bodies are assigned to the same person, oh no
        body_ids = list(distances.keys())
        min_dist = float("inf")
        min_body = None
        for body_id, dists in distances.items():
            if min_dist > dists[2]:
                min_dist = dists[2]
                min_body = body_id
        assigned[min_body] = assigned_to.pop()
        body_ids.pop(min_body)
        other_body = body_ids[0]
        if assigned[min_body] == 0:
            assigned[other_body] = 1
        else:
            assigned[other_body] = 0
    # based on assigned, let's now actually assign!
    last_assigned = {}
    for body_id, person_id in assigned.items():
        keypoints = keypoints_list[body_id]['keypoints_int']
        person_to_id[person_id].append(body_id)
        last_assigned[person_id] = (body_id, keypoints)

    return person_to_id, last_assigned

def identify_people(alphapose_results: dict):
    """
    A function that looks at Alphapose data (that has been preprocessed) and assigns them to people, base solely on mean Euclidean distance. 
    For definition of 'mean Euclidean distance', check the logic of calculate_distance(). 
    This is the main one.

    results_dict: preprocessed Alphapose results

    outputs a dictionary 'person_to_id', that has people's ids as keys, and a list of body indices for each frame
    """
    first_time = True
    person_to_id = {0: [], 1: []}
    for image_id, keypoints_list in alphapose_results.items():
        num_bodies = len(keypoints_list)
        if num_bodies < 2:
            try:
                person_to_id = return_nan(person_to_id)
            except:
                print("Error when num_bodies < 2")
                print("image_id:", image_id)
                print(traceback.format_exc())
            # Just returns nan
        elif (num_bodies == 2) and first_time:
            try:
                first_time = False
                person_to_id, last_assigned = assign_first_time(person_to_id, keypoints_list)
            except:
                print("Error when num_bodies == 2 for the first time")
                print("image_id:", image_id)
                if last_assigned:
                    print("last_assigned:", last_assigned)
                print(traceback.format_exc())
            # assign first time
        elif (num_bodies > 2) and not first_time:
            try:
                distances = calculate_all_distances(keypoints_list, last_assigned)
                two_distances = keep_only_two(distances)
                person_to_id, last_assigned = assign(person_to_id, keypoints_list, two_distances, last_assigned)
            except:
                print("Error when num_bodies > 2")
                print("image_id:", image_id)
                print("last_assigned:", last_assigned)
                print("distances:", distances)
                print("person_to_id:", person_to_id)
                print(traceback.format_exc())
            # assign normally
        # then assign based on distance
        elif (num_bodies == 2) and not first_time:
            try:
                distances = calculate_all_distances(keypoints_list, last_assigned)
                person_to_id, last_assigned = assign(person_to_id, keypoints_list, distances, last_assigned)
            except:
                print("Error when num_bodies == 2, not first time")
                print("image_id:", image_id)
                print("last_assigned:", last_assigned)
                print("distances:", distances)
                print("person_to_id:", person_to_id)
                print(traceback.format_exc())
        else:
            person_to_id = return_nan(person_to_id)
            print("Something weird happened")
            # Just returns nan
    return person_to_id

def match_keypoints(person_id, keypoints):
    person_to_keypoints = {}
    for person, index_list in person_id.items():
        person_keypoints = []
        for image_id, body_index in enumerate(index_list):
            if np.isnan(body_index):
                matched_keypoints = -1
                print("We skipped", image_id)
            else:
                try:
                    matched_keypoints = keypoints[image_id][body_index]['keypoints_int']
                except:
                    print("something went wrong at", image_id)
            person_keypoints.append(matched_keypoints)
        person_to_keypoints[person] = person_keypoints
    return person_to_keypoints

def save_analysis(data: dict, data_name, outpath = None):
    if outpath:
        with open (f"{outpath}{data_name}.json", "w") as json_file:
            json.dump(data, json_file)
    else:
        with open("person_id.json", "w") as json_file:
            json.dump(data, json_file)

def main():
    args = get_args()
    alphapose_results = open_process_file(path = args.inpath)
    person_to_body_id = identify_people(alphapose_results)
    save_analysis(person_to_body_id, data_name = "person_id", outpath = args.outpath)
    keypoints_matched = match_keypoints(person_to_body_id, alphapose_results)
    save_analysis(keypoints_matched, data_name = "person_keypoints", outpath = args.outpath)


if __name__ == "__main__":
    main()