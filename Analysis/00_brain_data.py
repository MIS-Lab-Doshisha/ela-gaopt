"""
--------------------------------------------------
Tested with Python 3.13.2
--------------------------------------------------
Script for binarizing preprocessed data
--------------------------------------------------
"""

import numpy as np
import pandas as pd
from nilearn import image
from nilearn.interfaces.fmriprep import load_confounds
from nilearn.maskers import NiftiSpheresMasker
from nilearn import datasets
import pickle
import os

# --- Variable settings ---
TR = 2.0                                     # TR (seconds)
radius = 4                                   # ROI radius (mm)
raw_site_name = ["ABIDE2-USM_1"]             # List of raw data site names
session_list  = [""]                         # List of sessions

# --- Path settings ---
subjects_path = "Data//preprocessed//derivatives//" # Path to preprocessed data
behavioral_path = "Data//preprocessed//"            # Path to behavioral data
pkl_path = "Data//test_data_1//test//"              # Output path

# --- Load the atlas ---
dataset = datasets.fetch_coords_power_2011() # Power Atlas
rois_x = pd.DataFrame(dataset["rois"].x)     # x-coordinates of ROIs
rois_y = pd.DataFrame(dataset["rois"].y)     # y-coordinates of ROIs
rois_z = pd.DataFrame(dataset["rois"].z)     # z-coordinates of ROIs

rois = pd.concat([rois_x,rois_y],axis=1) 
rois = pd.concat([rois,rois_z],axis=1)                         # Concatenate ROI coordinates
all_mni_coords = list(rois.itertuples(index=False, name=None)) # List of all ROI coordinates

# --- binarization function ---
def binarize(TimeSeries_list,binarize_list):
    """
    Binarize time series data based on the mean of each ROI"""
    for i in range(len(TimeSeries_list)):
        TimeSeries = TimeSeries_list[i].T                    # Transpose the time series data
        TimeSeries_list_DF = pd.DataFrame(TimeSeries)        # Convert the extracted data to DataFrame
        mean_TimeSeries = TimeSeries_list_DF.mean(axis=1)    # Calculate the mean for each row (ROI)
        binarize_TimeSeries = []                             # Create a list to store binarized data
                                                             # Threshold the data using the mean
                                                             # Repeat for each row (ROI)
        print(len(mean_TimeSeries))

        for i in range(len(mean_TimeSeries)):
            binarize_TimeSeries_1 = np.where(TimeSeries[i]>mean_TimeSeries.iloc[i],1,0).tolist()    # Binarize each row using the mean as threshold
            binarize_TimeSeries.append(binarize_TimeSeries_1)                                       # Append the row to the list
        binarize_list.append(binarize_TimeSeries)
    return binarize_list 

# --- time series extraction function ---
def time_series(subject_list, session_list, subjects_location, all_mni_coords, radius, TimeSeries_list):
    """
    Extract time series data from fMRI images
    """
    for subject in subject_list:
        for session in session_list:
            # Construct the file name
            if session == "":
                bold_file = f'{subjects_location}sub-{subject}/func/sub-{subject}_task-rest_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz'
            else:
                bold_file = f'{subjects_location}sub-{subject}/func/sub-{subject}_task-rest_{session}_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz'
            # Check if the file exists
            if not os.path.exists(bold_file):
                print(f"File not found: {bold_file}")
                continue
            # Load the image file
            bold_img = image.load_img(bold_file)
            # Load confounds
            confounds, _ = load_confounds(
                bold_file,
                strategy=["high_pass", "motion", "wm_csf", "scrub"],
                motion="full",
                wm_csf="full",
                scrub=5,
                fd_threshold=0.5
            )
            # Create the masker
            masker = NiftiSpheresMasker(
                seeds=all_mni_coords,
                smoothing_fwhm=6,
                radius=radius,
                detrend=True, 
                low_pass=0.1, 
                high_pass=0.01,
                t_r=TR,
                memory='nilearn_cache',
                memory_level=1, 
                verbose=2
            )
            # Extract time series
            time_series = masker.fit_transform(bold_img, confounds=confounds)
            print(f'sub-{subject} {session} time series =', time_series.shape)
            # Append the extracted time series to the list
            TimeSeries_list.append(time_series)
    return TimeSeries_list



def main():
    """
    Main function to execute the binarization process"""
    for site_name in raw_site_name:
        behavioral_df = pd.read_csv(f"{behavioral_path}participants.tsv",sep="\t",encoding="latin1")                
        print(behavioral_df)
        subject_list = (behavioral_df["participant_id"].tolist())
        print(subject_list)
        print(len(subject_list))
        site_list = (behavioral_df["site_id"].tolist())
        task_data_list = []
        for i,subjects in enumerate(subject_list):
            print(f"Trial: {i+1}")
            subject = []
            subject.append(subjects)
            TimeSeries_list = []
            # Extract time series data
            TimeSeries_list = time_series(subject, session_list, subjects_path, all_mni_coords, radius, TimeSeries_list)
            # Binarization process
            binarize_list = []
            binarize_list = binarize(TimeSeries_list,binarize_list)
            binarize_df = pd.DataFrame(binarize_list)
            df_sum = binarize_df.apply(lambda x: np.concatenate(np.array(x).tolist(), axis=0))
            task_data = pd.DataFrame(df_sum)
            task_data = task_data.T
            print(task_data.shape)
            task_data_list.append(np.array(task_data))
        print(task_data_list)
        f = open(f'{pkl_path}test_data.pkl',"wb")
        pickle.dump(task_data_list,f)
        f.close()

if __name__ == "__main__":
    main()