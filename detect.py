print("Loading the required Python modules ...\n")
import argparse

from azure.cognitiveservices.vision.face.face_client import FaceClient  # The main interface to access Azure face API
from msrest.authentication import CognitiveServicesCredentials  # To hold the subscription key

from utils import (
    ask_for_input,
    get_abspath,
    get_key,
    is_url,
    list_files,
    option_parser,
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
args = parser.parse_args()

# ----------------------------------------------------------------------
# Setup
# ----------------------------------------------------------------------

face_attrs = ['age', 'gender', 'glasses', 'emotion', 'occlusion']

key, endpoint = get_key(args.key, args.endpoint, args.key_file)

# **Note**:
# 1. The endpoint URL varies depending on the region of your service and can be found at Overview page of your service.
#    See 'https://westus.dev.cognitive.microsoft.com/docs/services/563879b61984550e40cbbe8d/operations/563879b61984550f30395236'
# 1. For Azure face API for Python, endpoint should omit the trailing part of
#    'https://southeastasia.api.cognitive.microsoft.com/face/v1.0'

endpoint = '/'.join(endpoint.split('/')[:3])  # Remove any trailing path


# ----------------------------------------------------------------------
# Call face API to detect and describe faces
# ----------------------------------------------------------------------

client = FaceClient(endpoint, CognitiveServicesCredentials(key))

if not args.photo:
    msg = "Please give the URL or path of a photo to detect faces:"
    img_url = ask_for_input(msg)
else:
    img_url = args.photo

if is_url(img_url):  # Photo from URL
    # For return_face_attributes, it can be a FaceAttributeType, or a list of string
    print("Detecting faces in photo:\n{}".format(img_url))
    faces = client.face.detect_with_url(img_url, return_face_attributes=face_attrs)
    show_detection_results(img_url, faces)

else:  # Photo from file
    img_url = get_abspath(img_url)
    for path in list_files(img_url):
        print("Detecting faces in photo:\n{}".format(path))
        with open(path, 'rb') as file:
            # For face attributes, it can be a FaceAttributeType, or a list of string
            faces = client.face.detect_with_stream(file, return_face_attributes=face_attrs)

        show_detection_results(path, faces)










