### Installing

1. Install Python 3.
2. Install Pytorch
3. cudnn/v7.0-cuda.9.0 (optional)

### Data Preprocessing
Data preprocessing is in tools/ folder

### Training
python train_model/train_vqa_layout.py --model_type rl_layout  --data_dir /home/active_vqa/data --image_feat_dir /home/active_vqa/data/vgg_pool5/train --out_dir /home/active_vqa/data/temp_out

### Loss
Loss is in models/custom_loss.py and models/end2endModuleNet.py

### Algorithm
Visual_Task_Selection_Algorithm.pdf
