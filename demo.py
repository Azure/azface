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

from packaging import version
import azure.cognitiveservices.vision.face as faceAPI
if version.parse(faceAPI.__version__) <= version.parse('0.3.0'):
    from azure.cognitiveservices.vision.face.face_client import FaceClient  # The main interface to access Azure face API
else:
    from azure.cognitiveservices.vision.face import FaceClient
from mlhub.pkg import azkey
from msrest.authentication import CognitiveServicesCredentials  # To hold the subscription key
from utils import (
    KEY_FILE,
    SERVICE,
    azface_detect,
    azface_similar,
    get_face_api_key_endpoint,
    list_files,
    show_detection_results,
    show_similar_results,
)


# ----------------------------------------------------------------------
# Setup
# ----------------------------------------------------------------------

# Request subscription key and endpoint from user.

subscription_key, endpoint = get_face_api_key_endpoint(*azkey(KEY_FILE, SERVICE))

# Set credentials.

credentials = CognitiveServicesCredentials(subscription_key)

# Create client.

client = FaceClient(endpoint, credentials)  # Setup Azure face API client


# ----------------------------------------------------------------------
# Face detection
# ----------------------------------------------------------------------

# Setup

face_attrs = ['age', 'gender', 'glasses', 'emotion', 'occlusion']
detect_photo_dir = 'docs/photo/detection'

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

target_url = 'docs/photo/PersonGroup/Family1-Dad-Bill/Family1-Dad1.jpg'
candidate_url = 'docs/photo/identification/identification1.jpg'

# Memorize target faces

print("\nDetecting faces in the target photo:\n  {}".format(target_url))
target_faces = azface_detect(client, target_url)

# Find target faces in another photo

msg = "\nDetecting faces in the candidate photo:\n  {}"
print(msg.format(candidate_url))
candidate_faces = azface_detect(client, candidate_url)
matches = azface_similar(client, target_faces, candidate_faces)
show_similar_results(target_url, target_faces, candidate_url, candidate_faces, matches)
