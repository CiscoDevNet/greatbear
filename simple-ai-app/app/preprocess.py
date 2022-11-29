"""
Copyright (c) 2022 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

import numpy as np

# Pre-processing function for ImageNet models using numpy
# from https://github.com/onnx/models/tree/main/vision/classification/inception_and_googlenet/googlenet#obtain-and-pre-process-image
def preprocess(img):
    '''
    Preprocessing required on the images for inference with mxnet gluon
    The function takes loaded image and returns processed tensor
    '''
    img = np.array(img.resize((224, 224))).astype(np.float32)
    img[:, :, 0] -= 123.68
    img[:, :, 1] -= 116.779
    img[:, :, 2] -= 103.939
    img[:,:,[0,1,2]] = img[:,:,[2,1,0]]
    img = img.transpose((2, 0, 1))
    img = np.expand_dims(img, axis=0)

    return img
