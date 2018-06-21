# rtfcma-prisma
Scripts for running rtFCMA experiment on the Prisma scanner.
Applicable to other scanners with minimal change.

## General Pipeline
Credit: [Prof. Ben Hutchinson](http://www.northeastern.edu/hutchinsonlab/)

When we run real time FCMA, we are applying a trained SVM model on a new participant.

The model was trained 'offline' using FCMA at BrainIAK. The full pipeline is much more elaborate,
but basically, it is based on 24 subjects and provides a set of weights to apply to a 2000 x 2000 matrix
of voxel to voxel correlations. We have to give the real-time processor the model (.pkl file) and
the mask of which 2000 voxels to use (based on training data), as well as a parameter telling
it how many time points to use in calculating the correlation values.

When a new participant comes in for a real-time study, we have to collect an anatomical image
(picture of the brain) and a functional image
(picture of the BOLD signal which is related to brain activity) for that person, for that session.
We use these two images to calculate how the incoming BOLD data can be aligned to 'standard space'
which is the space in which the training data/model resides. This is done using FSL and takes up to
15 minutes. It is not fully automated as it involves visual inspection to ensure that the registration
is good for this person/session. Once this transformation matrix (from raw, subject space to
standard space) is calculated, then we can collect the real-time data.

Real time processing consists of:

* Converting the .dcm files to .nii.gz format (using dcm2niix);
* Applying the transformation matrix to the .nii.gz file (using FSL);
* Applying the trained model to the specified number of most recent time points,
this returns a confidence value which is updated at each time point (using FCMA at BrainIAK).
* Reading in the confidence value from the text output to inform what to display to the participant
(using PsychToolbox in Matlab).

## Installation
The install script has been tested on a fresh Ubuntu 16.04 LTS instance.
```bash
./bin/server/install_deps
source ~/.bashrc
```

## Example
Get data from @danielsuo or @jhutchin (paths on intelrt02.pni.princeton.edu). For the for the following example we use the data listed below. There is a script that downloads these files, but assumes access to ```intelrt02```.

### Download server data
- Epoch file: ```/mnt/Data01/offline/strongbad01/epoch/sb_714tr.npy```
- Mask file: ```/mnt/Data01/offline/strongbad01/selection4mm/corr/allsubs_select_seq_top2000.nii.gz```
- Model file: ```/mnt/Data01/offline/strongbad01/model/svm_all_2000.pkl```
- Registration: ```/mnt/Data01/data/20161219.1219161_rtstrongbad01.1219161_rtstrongbad01/reg/f2mni.feat/reg/example_func2standard.mat```
- Template: ```/mnt/Data01/offline/strongbad01/anat4mm/canonical.nii.gz```

### Donwload client data
- DCM files: ```/mnt/Data01/data/20161219.1219161_rtstrongbad01.1219161_rtstrongbad01/*.dcm```

### To run on the server
```bash
# Start the virtual environment
source activate idp

# Start the REST server to listen for input with the description of experiment
# NOTE: you may need to modify the paths to data files and output directories
python server.py ./desc/example.json
```

### To run on the client
```bash
./bin/client/upload_dcm DIRECTORY_TO_DCM SERVER_ADDRESS
```
