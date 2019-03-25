print("Loading the required Python modules ...\n")
import argparse
import os

from azure.cognitiveservices.vision.face.face_client import FaceClient  # The main interface to access Azure face API
from msrest.authentication import CognitiveServicesCredentials  # To hold the subscription key

from utils import (
    ask_for_input,
    azface_detect,
    get_abspath,
    is_url,
    list_files,
    option_parser,
    setup_key_endpoint,
    show_detection_results,
)

# ----------------------------------------------------------------------
# Parse command line arguments
# ----------------------------------------------------------------------

parser = argparse.ArgumentParser(
    prog='detect',
    parents=[option_parser],
    description='Detect faces in an image.'
)

parser.add_argument(
    '--photo',
    type=str,
    help='path or URL of a photo where faces will be detected')

args = parser.parse_args()

# ----------------------------------------------------------------------
# Setup
# ----------------------------------------------------------------------

face_attrs = ['age', 'gender', 'glasses', 'emotion', 'occlusion']

key, endpoint = setup_key_endpoint(args.key, args.endpoint, args.key_file)

# Get the photo

if not args.photo:
    msg = "\nPlease give the URL or path of a photo to detect faces:"
    img_url = ask_for_input(msg)
else:
    img_url = args.photo


# ----------------------------------------------------------------------
# Call face API to detect and describe faces
# ----------------------------------------------------------------------

# Setup Azure face API client

client = FaceClient(endpoint, CognitiveServicesCredentials(key))

# Query Azure face API to detect faces

msg = "\nDetecting faces in photo:\n  {}\nPlease close each image window (Ctrl-w) to proceed.\n"
if is_url(img_url):  # Photo from URL

    print(msg.format(img_url))
    faces = azface_detect(client, img_url, return_face_attributes=face_attrs)
    show_detection_results(img_url, faces)

else:  # Photo from file

    img_url = get_abspath(img_url)
    if os.path.isdir(img_url):
        for path in list_files(img_url):
            print(msg.format(path))
            faces = azface_detect(client, path, return_face_attributes=face_attrs)
            show_detection_results(path, faces)
    else:
        print(msg.format(img_url))
        faces = azface_detect(client, img_url, return_face_attributes=face_attrs)
        show_detection_results(img_url, faces)
