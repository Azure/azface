# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# Author: Simon.Zhao@microsoft.com
#
# This demo is based on the Azure Cognitive Services Face API Quick Start

print("""=============
Face Services
=============

Welcome to a demo of the pre-built models for Face provided through Azure's 
Cognitive Services. This cloud service accepts images and can perform 
various analyses of the images, returning the results locally.
""")

# The main interface to access Azure face API:

from azure.cognitiveservices.vision.face.face_client import FaceClient

# To hold the subscription key:

from msrest.authentication import CognitiveServicesCredentials

from utils import (
    azface_detect,
    azface_similar,
    get_key,
    list_files,
    show_detection_results,
)

# ----------------------------------------------------------------------
# Setup
# ----------------------------------------------------------------------

key, endpoint = get_key(None, None, None)

# **Note**:
# 1. The endpoint URL varies depending on the region of your service and can be found at Overview page of your service.
#    See 'https://westus.dev.cognitive.microsoft.com/docs/services/563879b61984550e40cbbe8d/operations/563879b61984550f30395236'
# 1. For Azure face API for Python, endpoint should omit the trailing part of
#    'https://southeastasia.api.cognitive.microsoft.com/face/v1.0'

endpoint = '/'.join(endpoint.split('/')[:3])  # Remove any trailing path
client = FaceClient(endpoint, CognitiveServicesCredentials(key))  # Setup Azure face API client

# ----------------------------------------------------------------------
# Face detection
# ----------------------------------------------------------------------

# Setup

face_attrs = ['age', 'gender', 'glasses', 'emotion', 'occlusion']
detect_photo_dir = 'photo/detection'

# Detection

msg = "\nDetecting faces in photo:\n  {}\nPlease close each image window (Ctrl-w) to proceed.\n"
for path in list_files(detect_photo_dir):
    print(msg.format(path))
    faces = azface_detect(client, path, return_face_attributes=face_attrs)
    show_detection_results(path, faces)


# ----------------------------------------------------------------------
# Face recognition
# ----------------------------------------------------------------------

# Setup

target_url = 'photo/PersonGroup/Family1-Dad-Bill/Family1-Dad1.jpg'
candidate_url = 'photo/identification/identification1.jpg'

# Memorize target faces

print("\nDetecting faces in the target photo:\n  {}".format(target_url))
target_faces = azface_detect(client, target_url)

# Find target faces in another photo

msg = "\nDetecting faces in the candidate photo:\n  {}"
print(msg.format(candidate_url))
candidate_faces = azface_detect(client, candidate_url)
azface_similar(client, target_url, target_faces, candidate_url, candidate_faces)
