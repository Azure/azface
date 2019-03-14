print("Loading the required Python modules ...\n")
import argparse
import os

from azure.cognitiveservices.vision.face.face_client import FaceClient  # The main interface to access Azure face API
from msrest.authentication import CognitiveServicesCredentials  # To hold the subscription key

from utils import (
    ask_for_input,
    azface_detect,
    azface_similar,
    get_abspath,
    get_key,
    is_url,
    list_files,
    option_parser,
    stop,
)

# ----------------------------------------------------------------------
# Parse command line arguments
# ----------------------------------------------------------------------

parser = argparse.ArgumentParser(
    prog='similar',
    parents=[option_parser],
    description='Find similar faces between images.'
)

parser.add_argument(
    '--target',
    type=str,
    help='path or URL of a photo of the faces to be found')

parser.add_argument(
    '--candidate',
    type=str,
    help='path or URL of a photo to find expected target faces')

args = parser.parse_args()

# ----------------------------------------------------------------------
# Setup
# ----------------------------------------------------------------------

# Get Azure face API key and endpoint

key, endpoint = get_key(args.key, args.endpoint, args.key_file)

# **Note**:
# 1. The endpoint URL varies depending on the region of your service and can be found at Overview page of your service.
#    See 'https://westus.dev.cognitive.microsoft.com/docs/services/563879b61984550e40cbbe8d/operations/563879b61984550f30395236'
# 1. For Azure face API for Python, endpoint should omit the trailing part of
#    'https://southeastasia.api.cognitive.microsoft.com/face/v1.0'

endpoint = '/'.join(endpoint.split('/')[:3])  # Remove any trailing path

# Get the photo of target faces

if not args.target:
    msg = "\nPlease give the URL or path of a photo of the faces to be found:"
    target_url = ask_for_input(msg)
else:
    target_url = args.target

# Get the photo to be checked

if not args.candidate:
    msg = "\nPlease give the URL or path of a photo where you want to find the faces appear\nin {}:".format(target_url)
    candidate_url = ask_for_input(msg)
else:
    candidate_url = args.candidate


# ----------------------------------------------------------------------
# Detect target faces
# ----------------------------------------------------------------------

# Setup Azure face API client

client = FaceClient(endpoint, CognitiveServicesCredentials(key))

if not is_url(target_url):
    target_url = get_abspath(target_url)
    if os.path.isdir(target_url):
        stop("Only one target photo allowed!")

# Query Azure face API to detect target faces

print("\nDetecting faces in the target photo:\n  {}".format(target_url))
target_faces = azface_detect(client, target_url)

if not target_faces:
    stop("No faces found in {}\n".format(target_url))


# ----------------------------------------------------------------------
# Find similar faces
# ----------------------------------------------------------------------

msg = "\nDetecting faces in the candidate photo:\n  {}"


if is_url(candidate_url):  # Photo from URL

    # Query Azure face API to detect candidate faces

    print(msg.format(candidate_url))
    candidate_faces = azface_detect(client, candidate_url)

    azface_similar(client, target_url, target_faces, candidate_url, candidate_faces)

else:  # Photo from file

    candidate_url = get_abspath(candidate_url)
    if os.path.isdir(candidate_url):
        for path in list_files(candidate_url):

            print(msg.format(path))
            candidate_faces = azface_detect(client, path)

            azface_similar(client, target_url, target_faces, path, candidate_faces)

    else:
        print(msg.format(candidate_url))
        candidate_faces = azface_detect(client, candidate_url)

        azface_similar(client, target_url, target_faces, candidate_url, candidate_faces)

