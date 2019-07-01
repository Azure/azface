import argparse

from packaging import version
import azure.cognitiveservices.vision.face as faceAPI
if version.parse(faceAPI.__version__) <= version.parse('0.3.0'):
    from azure.cognitiveservices.vision.face.face_client import FaceClient  # The main interface to access Azure face API
else:
    from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials  # To hold the subscription key

from mlhub.pkg import (
    azkey,
    is_url,
)

from utils import (
    SERVICE,
    azface_detect,
    get_abspath,
    get_face_api_key_endpoint,
    option_parser,
    print_detection_results,
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
    'path',
    type=str,
    help='path or URL of a photo where faces will be detected')

args = parser.parse_args()

# ----------------------------------------------------------------------
# Setup
# ----------------------------------------------------------------------

img_url = args.path if is_url(args.path) else get_abspath(args.path)
face_attrs = ['age', 'gender', 'glasses', 'emotion', 'occlusion']
subscription_key, endpoint = args.key, args.endpoint


# ----------------------------------------------------------------------
# Call face API to detect and describe faces
# ----------------------------------------------------------------------

if not subscription_key or not endpoint:  # Request subscription key and endpoint from user.
    subscription_key, endpoint = get_face_api_key_endpoint(*azkey(args.key_file, SERVICE, verbose=False))

credentials = CognitiveServicesCredentials(subscription_key)  # Set credentials
client = FaceClient(endpoint, credentials)  # Setup Azure face API client
faces = azface_detect(client, img_url, return_face_attributes=face_attrs)
print_detection_results(faces)
