import os, sys
#os.environ['DLClight']='True'
import deeplabcut
from pathlib import Path

nmspath = 'deeplabcut/pose_estimation_tensorflow/lib/nms_cython'
sys.path.append(os.path.join('/usr/local/lib/python3.6/dist-packages',nmspath))

task='MontBlanc'
scorer='Daniel'

saveiters=4000
displayiters=500
maxiters=6000

#print("CREATING PROJECT")
#path_config_file=deeplabcut.create_new_project(task,scorer,video,copy_videos=True,multianimal=True)
basefolder='/media/alex/dropboxdisk/Dropbox/Collaborations/MultiAnimalTests/DLCExampleProjects/MontBlanc-Daniel-2019-12-16'
videotype='.mov'

video=[os.path.join(basefolder,'videos/montblanc.mov')]
path_config_file=os.path.join(basefolder,'config.yaml')
videopath=os.path.join(basefolder,'videos')

shuffle=0
trainingsetindex=0


print("Plot labels...") #NEW:
deeplabcut.check_labels(path_config_file,draw_skeleton=True,visualizeindividuals=True)
deeplabcut.check_labels(path_config_file,draw_skeleton=True,visualizeindividuals=False)


print("Crop images...") #RECOMMENDED:
deeplabcut.cropimagesandlabels(path_config_file,userfeedback=False)
#then we uncommented the large-scale full frame data > it is not used for training!

print("Plot labels...") #NEW:
print("Creating multianimal training set...")
deeplabcut.create_multianimaltraining_dataset(path_config_file,Shuffles=[shuffle])


print("Creating multianimal training set...")

deeplabcut.train_network(path_config_file, shuffle=shuffle,trainingsetindex=trainingsetindex,
    saveiters=saveiters,displayiters=displayiters,max_snapshots_to_keep=2,maxiters=maxiters)

trainposeconfigfile,testposeconfigfile,snapshotfolder=deeplabcut.return_train_network_path(path_config_file,shuffle=shuffle)
cfg_dlc=deeplabcut.auxiliaryfunctions.read_plainconfig(testposeconfigfile)
cfg_dlc['partaffinityfield_predict']=True
cfg_dlc['dataset_type']='multi-animal-imgaug'
cfg_dlc['nmsradius']=5.
cfg_dlc['minconfidence']=.05
deeplabcut.auxiliaryfunctions.write_plainconfig(testposeconfigfile,cfg_dlc)

print("Evaluating network for shuffle ", shuffle)
deeplabcut.evaluate_network(path_config_file,Shuffles=[shuffle],plotting=True)
deeplabcut.evaluate_multianimal_crossvalidate(path_config_file,Shuffles=[shuffle])

print("Extracting maps...")
deeplabcut.extract_save_all_maps(path_config_file, Indices=[0, 1, 2, 3, 4, 5])

################## Analyze video #NEW:
trainposeconfigfile,testposeconfigfile,snapshotfolder=deeplabcut.return_train_network_path(path_config_file,shuffle=shuffle)
edits = {'partaffinityfield_predict': True,
         'dataset_type': 'multi-animal-imgaug',
         'nmsradius': 10.,
         'minconfidence': .05}
cfg_dlc = deeplabcut.auxiliaryfunctions.edit_config(testposeconfigfile, edits)

print("Starting inference for", shuffle)
deeplabcut.analyze_videos(path_config_file,[videopath],shuffle=shuffle,videotype=videotype)
#deeplabcut.analyze_videos(path_config_file,[videopath],shuffle=shuffle,videotype=videotype,c_engine=True)

model='DLC_resnet50_MontBlancDec16shuffle'+str(shuffle)+'_'+str(maxiters)
deeplabcut.create_video_with_all_detections(path_config_file, [video[0]], model)


for tm in ['skeleton', 'box']:
    deeplabcut.convert_detections2tracklets(path_config_file,[videopath],shuffle=shuffle,videotype=videotype,track_method=tm)
    #deeplabcut.convert_raw_tracks_to_h5(path_config_file,)
    if tm == 'skeleton':
        tmn='sk'
    else:
        tmn='bx'

    tracks_pickle=os.path.join(videopath,Path(video[0]).stem+model+'_'+tmn+'.pickle')

    deeplabcut.convert_raw_tracks_to_h5(path_config_file, tracks_pickle)
    deeplabcut.create_labeled_video(path_config_file,[videopath],shuffle=shuffle,videotype=videotype,track_method=tm)
    deeplabcut.create_labeled_video(path_config_file,[videopath],shuffle=shuffle,videotype=videotype,track_method='box',color_by='individual')


    #deeplabcut.extract_outlier_frames(path_config_file,[videopath],shuffle=shuffle,videotype=videotype,track_method=tm,epsilon=40)
