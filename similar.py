import argparse
import os

from azure.cognitiveservices.vision.face.face_client import FaceClient  # The main interface to access Azure face API
from msrest.authentication import CognitiveServicesCredentials  # To hold the subscription key

from mlhub.pkg import (
    azkey,
    is_url,
)

from utils import (
    SERVICE,
    azface_detect,
    azface_similar,
    get_abspath,
    getbox_points,
    option_parser,
    print_similar_results,
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
    'target',
    help='path or URL of a photo of the faces to be found')

parser.add_argument(
    'candidate',
    help='path or URL of a photo to find expected target faces')

args = parser.parse_args()

# ----------------------------------------------------------------------
# Setup
# ----------------------------------------------------------------------
target_url = args.target if is_url(args.target) else get_abspath(args.target)  # Get the photo of target faces
candidate_url = args.candidate if is_url(args.candidate) else get_abspath(args.candidate)  # Get the photo to be checked
subscription_key, endpoint = args.key, args.endpoint

if os.path.isdir(target_url) or os.path.isdir(candidate_url):
    stop("Only one photo allowed!")

# ----------------------------------------------------------------------
# Prepare Face API client
# ----------------------------------------------------------------------

if not subscription_key or not endpoint:  # Request subscription key and endpoint from user.
    subscription_key, endpoint = azkey(args.key_file, SERVICE, verbose=False)

credentials = CognitiveServicesCredentials(subscription_key)  # Set credentials
client = FaceClient(endpoint, credentials)  # Setup Azure face API client


# ----------------------------------------------------------------------
# Detect faces
# ----------------------------------------------------------------------

target_faces = azface_detect(client, target_url)
candidate_faces = azface_detect(client, candidate_url)
if not target_faces or not candidate_faces:
    stop("No faces found!")


# ----------------------------------------------------------------------
# Find similar faces
# ----------------------------------------------------------------------

matches = azface_similar(client, target_faces, candidate_faces)
print_similar_results(candidate_faces, matches)
