import json
import numpy as np
import collections
import argparse
import os

MAIN_PATH = "C:/Users/lhi30/Haein/2023/YBIGTA/2023-2/DA/Big_Con/Pose/identify_people/"
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

def calculate_min_distances(current_bodies, prev_bodies):
    """
    Calculate the minimum distances between current and previous bodies.

    current_bodies: a list of keypoints dictionaries of the current frame
    prev_bodies: a list of keypoints dictionaries of the previous frame
    """
    min_distances = {}
    for current_id, current_body in enumerate(current_bodies):
        # Get a body from current frame
        current_pose = current_body['keypoints_int']
        distances = []

        for prev_id, prev_body in enumerate(prev_bodies):
            # Get a body from previous frame
            prev_pose = prev_body['keypoints_int']
            # And calculate the distance
            dist = calculate_distance(current_pose, prev_pose)
            distances.append((prev_id, dist))

        if distances:
            # If there was something calculated, figure out what was the minimum of that and only keep that one
            min_prev_id, min_distance = min(distances, key=lambda x: x[1])
            min_distances[current_id] = (min_prev_id, min_distance)
        else:
            # If there was nothing calculated, then just go with the current id, and put infinity as the distance
            min_distances[current_id] = (current_id, float('inf'))

    return min_distances

def identify_people(results_dict: dict) -> dict:
    """
    A function that looks at Alphapose data (that has been preprocessed) and assigns them to people, base solely on mean Euclidean distance. 
    For definition of 'mean Euclidean distance', check the logic of calculate_distance(). 
    This is the main one.

    results_dict: preprocessed Alphapose results

    outputs a dictionary 'total_people', that has people's ids as keys, and a list of body indices for each frame
    """
    # Initialize data structures
    total_people = {}  # Dictionary to store people and their assigned body IDs
    prev_people = {}   # Dictionary to store the previous frame's assignments

    for image_id, current_bodies in results_dict.items():
        prev_bodies = results_dict.get(image_id - 1, [])

        # Calculate minimum distances between current and previous bodies
        current_min_distances = calculate_min_distances(current_bodies, prev_bodies)

        # Handle changes in the number of people
        diff = len(current_bodies) - len(prev_bodies)
        if diff > 0:
            total_people, prev_people = handle_increase(total_people, prev_people, current_min_distances, diff, image_id)
        else:
            total_people, prev_people = assign_people(current_min_distances, prev_people, total_people, image_id)
        # Pad any people that weren't filled with np.nan
        if total_people:
            max_list_length = max(len(ids) for ids in total_people.values())
            for _, body_ids in total_people.items():
                body_ids.extend([np.nan] * (max_list_length - len(body_ids)))

    return total_people

def handle_increase(total_people, prev_people, current_min_distances, diff, image_id):
    """
    Handle an increase in the number of people.
    """
    new_person_ids = list(range(len(total_people), len(total_people) + diff))
    if total_people:
        # if there is a value in total_people, pad the newly added peoples' inputs to match it
        max_list_length = max(len(bodies) for bodies in total_people.values())
        for new_person_id in new_person_ids:
            total_people[new_person_id] = [np.nan] * max_list_length
    else:
        total_people.update({new_person_id: [] for new_person_id in new_person_ids})
    total_people, prev_people = assign_people(current_min_distances, prev_people, total_people, image_id, new_person_ids)
    
    return total_people, prev_people

def assign_people(current_min_distances, prev_people, total_people, image_id, new_person_ids=[]):
    """
    Assign current bodies to people based on minimum distances.
    """
    sorted_min_distances = sorted(current_min_distances.items(), key=lambda x: x[1][1])
    new_person_ids.sort(reverse=True)

    new_prev_people = {}

    for current_id, (prev_id, _) in sorted_min_distances:
        if prev_people:
        # If there's record of assigning people in the previous frame
            try:
                person_id = prev_people.pop(prev_id)
                # assign it to the right person, based on that info
                # and pop it
            except:
                # and if there's something wrong, because the body you're looking for as been assigned to a person already
                # idk what to do
                # THIS IS THE POINT WE NEED TO FIX AND HANDLE!!
                print("image_id:", image_id)
                print("prev_people:", prev_people)
                print("prev_id:", prev_id)
        elif new_person_ids:
            # If we've run out of previous records, but still have current_id's left, then we need to assign them to new people
            person_id = new_person_ids.pop()
            # and pop
        else:
            # and if otherwise, something is wrong in the logic, but idk what to do, so let's ignore you and continue
            continue
        # actually assign! and update prev_people
        total_people[person_id].append(current_id)
        new_prev_people[current_id] = person_id

    return total_people, new_prev_people

def save_analysis(data: dict, outpath = None):
    if outpath:
        with open (f"{outpath}person_id.json", "w") as json_file:
            json.dump(data, json_file)
    else:
        with open("person_id.json", "w") as json_file:
            json.dump(data, json_file)

def main():
    args = get_args()
    alphapose_results = open_process_file(path = args.inpath)
    person_to_body_id = identify_people(alphapose_results)
    save_analysis(person_to_body_id, outpath = args.outpath)

if __name__ == "__main__":
    main()