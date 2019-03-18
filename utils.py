import argparse
import cv2 as cv
import getpass
import glob
import hashlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import os
import re
import readline  # Don't remove !! For prompt of input() to take effect
import sys
import toolz
import urllib.error
import urllib.parse
import urllib.request
import uuid

from mlhub import utils as mlutils

# ----------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------

MARK_COLOR = (0, 255, 0)  # Green.  This color has no difference in RGB (matplotlib) and BGR (OpenCV)
MARK_WIDTH = 4
TEXT_COLOR = MARK_COLOR
LINE_WIDTH = 2
TEXT_FONT = cv.FONT_HERSHEY_SIMPLEX
TEXT_SIZE = 1


# ----------------------------------------------------------------------
# Command line argument parser
# ----------------------------------------------------------------------

option_parser = argparse.ArgumentParser(add_help=False)

option_parser.add_argument(
    '--key',
    type=str,
    help='Azure face API subscription key')

option_parser.add_argument(
    '--key-file',
    type=str,
    help='file that stores Azure face API subscription key')

option_parser.add_argument(
    '--endpoint',
    type=str,
    help='endpoint of Azure face API service')


# ----------------------------------------------------------------------
# File, folder, and I/O
# ----------------------------------------------------------------------

def get_abspath(path):
    """Return the absolute path of <path>.

    Because the working directory of MLHUB model is ~/.mlhub/<model>,
    when user run 'ml score facematch <image-path>', the <image-path> may be a
    path relative to the path where 'ml score facematch' is typed, to cope with
    this scenario, mlhub provides mlhub.utils.get_cmd_cwd() to obtain this path.
    """

    path = os.path.expanduser(path)
    if not os.path.isabs(path):
        path = os.path.join(mlutils.get_cmd_cwd(), path)

    return os.path.abspath(path)


def list_files(path, depth=0):
    """List all files in <path> at level <depth>.  If depth < 0, list all files under <path>."""

    path = os.path.join(path, '')
    start = len(path)
    for (root, dirs, files) in os.walk(path):
        if depth < 0:
            for file in files:
                yield os.path.join(root, file)
        else:
            segs = root[start:].split(os.path.sep)
            if (depth == 0 and segs[0] == '') or len(segs) == depth:
                for file in files:
                    yield os.path.join(root, file)


def load_key(path):
    """Load subscription key and endpoint from file."""

    key = None
    endpoint = None
    markchar = "'\" \t"
    with open(path, 'r') as file:
        for line in file:
            line = line.strip('\n')
            pair = line.split('=')
            if len(pair) == 2:
                k = pair[0].strip(markchar).lower()
                v = pair[1].strip(markchar)
                if k == 'key':
                    key = v
                elif k == 'endpoint':
                    endpoint = v
            elif not line.startswith('#'):
                line = line.strip(markchar)
                if line.startswith('http'):
                    endpoint = line
                else:
                    key = line

    return key, endpoint


def save_key(key, endpoint, path):
    """Save subscription key and endpoint into file."""

    with open(path, 'w') as file:
        file.write("key = {}\nendpoint = {}\n".format(key, endpoint))


def download_img(url, folder, prefix):
    """Download image from <url> into <folder> with name as <prefix>_<md5>."""

    # Download image from <url> into a unique file path with <prefix>

    path = os.path.join(folder, get_unique_name(prefix))
    urllib.request.urlretrieve(url, path)

    return replace_uuid_with_digest(path)


def get_hexdigest(path):
    with open(path, 'rb') as file:
        digest = hashlib.md5(file.read()).hexdigest()

    return digest


def get_unique_name(prefix):
    """Return a unique name as prefix_uuid."""

    prefix = '_'.join(prefix.split()) if prefix is not None else 'temp'
    number = str(uuid.uuid4().hex)
    return prefix + '_' + number


def change_name_hash(name, digest):
    """Change name from prefix_uuid to prefix_digest."""

    name = name.split('_')
    name[-1] = digest
    return '_'.join(name)


def get_name_hash(name):
    return name.split('_')[-1]


def replace_uuid_with_digest(path):
    """Replace uuid in path name with md5 digest"""

    digest = get_hexdigest(path)
    new_path = change_name_hash(path, digest)
    os.rename(path, new_path)
    return new_path, digest


def make_name_dir(path, name):
    """Createa dir under <path> for person <name> where <name> may contain spaces."""

    name_dir = '_'.join(name.split())
    name_dir_path = os.path.join(path, name_dir)
    os.makedirs(name_dir_path, exist_ok=True)
    return name_dir_path


def ask_for_input(msg, hide=False):
    print(msg)
    msg = "> "
    prompt = getpass.getpass if hide else input
    if prompt == input:  # Setup input path completion
        readline.set_completer_delims('\t')
        readline.parse_and_bind("tab: complete")
        readline.set_completer(tab_complete_path)

    res = prompt(msg)
    while res.strip() == '':
        res = prompt("> ")
    return res


def stop(msg, status=0):
    print(msg)
    sys.exit(status)


# ----------------------------------------------------------------------
# Image
# ----------------------------------------------------------------------

def read_cv_image_from(url):
    """Read an image from url or file as grayscale opencv image.

    **Note**: OpenCV return the image as numpy array, which can also directly
    be used by other Python image libraries.  However, the color space in
    OpenCV is BGR instead of the popular RGB.
    """

    return toolz.pipe(
        url,
        urllib.request.urlopen if is_url(url) else lambda x: open(x, 'rb'),
        lambda x: x.read(),
        bytearray,
        lambda x: np.asarray(x, dtype="uint8"),
        lambda x: cv.imdecode(x, cv.IMREAD_COLOR))


def convert_cv2matplot(*images):
    """Convert color space between OpenCV and Matplotlib.

    Because OpenCV and Matplotlib use different color spaces.
    """

    if len(images) > 0:
        res = []
        for image in images:
            image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
            res.append(image)

        return res[0] if len(res) == 1 else tuple(res)
    else:
        return None


def _plot_image(ax, img, cmap=None, label=''):
    """Plot <img> in <ax>."""

    ax.imshow(img, cmap)
    ax.tick_params(
        axis='both',
        which='both',
        # bottom='off',  # 'off', 'on' is deprecated in matplotlib > 2.2
        bottom=False,
        # top='off',
        top=False,
        # left='off',
        left=False,
        # right='off',
        right=False,
        # labelleft='off',
        labelleft=False,
        # labelbottom='off')
        labelbottom=False)
    ax.set_xlabel(label)


def plot_side_by_side_comparison(
        leftimg,
        rightimg,
        leftlabel='Original Image',
        rightlabel='Result',
        leftcmap=None,
        rightcmap=None):
    """Plot two images side by side."""

    # Setup canvas

    gs = gridspec.GridSpec(6, 13)
    gs.update(hspace=0.1, wspace=0.001)
    fig = plt.figure(figsize=(7, 3))

    # Plot Left image

    ax = fig.add_subplot(gs[:, 0:6])
    _plot_image(ax, leftimg, cmap=leftcmap, label=leftlabel)

    # Plot right image

    ax = fig.add_subplot(gs[:, 7:13])
    _plot_image(ax, rightimg, cmap=rightcmap, label=rightlabel)

    # Show all of them

    plt.show()


def show_image(url, show=True):
    """Read image from <url> and display."""

    img = read_cv_image_from(url)
    img = convert_cv2matplot(img)
    if show:
        display(img)
    return img


def display(img, frombgr=False):
    """Display <img> array."""

    if frombgr:
        img = convert_cv2matplot(img)
    plt.axis('off')
    plt.imshow(img)
    plt.show()


# ----------------------------------------------------------------------
# Face
# ----------------------------------------------------------------------

def getbox(face):
    """Convert width and height in face to a point in a rectangle"""

    rect = face.face_rectangle
    left = rect.left
    top = rect.top
    right = left + rect.width
    bottom = top + rect.height
    return top, right, bottom, left


def mark_face(image, face, text=None):
    """Mark the <faces> in <image>.

    Args:
        image: An OpenCV BGR image.
        face: A face cooridinate tuple (top, right, bottom, left).
        text: Text would be displayed above the face box.
    """

    # Draw a rectangle around the faces

    (textwidth, textheight), baseline = cv.getTextSize(text, TEXT_FONT, TEXT_SIZE, LINE_WIDTH)
    top, right, bottom, left = face
    cv.rectangle(image, (left, top), (right, bottom), MARK_COLOR, MARK_WIDTH)

    if text:
        imgheight, imgwidth, _ = image.shape

        y = top - baseline
        if y < textheight:
            y = bottom + textheight
            if y + baseline > imgheight:
                y = top + textheight

        x = int(left + (right - left - textwidth)/2)
        if x < 0:
            x = 0
        elif x + textwidth > imgwidth:
            x = imgwidth - textwidth

        cv.putText(image, text, (x, y), TEXT_FONT, TEXT_SIZE, TEXT_COLOR, LINE_WIDTH)


def get_key(key, endpoint, key_file):
    default_key_file = 'key.txt'
    key_from_file = None
    endpoint_from_file = None
    if not key or not endpoint:

        # Check if there is a key file

        if key_file:
            key_file = get_abspath(key_file)
        else:
            if not os.path.exists(default_key_file):
                msg = """
    To use Microsoft Azure face service:

        https://azure.microsoft.com/en-us/services/cognitive-services/face/

    a Azure face API subscription key is needed.

    A 7-days free trial Azure account can be created at:

        https://azure.microsoft.com/en-us/try/cognitive-services/?api=face-api

    You can try it and get the key as well as the endpoint.
    """
                print(msg)
            else:
                yes = mlutils.yes_or_no("A subscription key is found locally! Would you like to use it", yes=True)
                if yes:  # Load Bing search API key if available
                    key_file = default_key_file

        if key_file:
            key_from_file, endpoint_from_file = load_key(key_file)

    key = key if key else key_from_file
    endpoint = endpoint if endpoint else endpoint_from_file

    if not key:
        msg = "\nPlease paste the key below (Your key will be kept in\n'{}'):".format(default_key_file)
        key = ask_for_input(msg, hide=True)

    if not endpoint:
        msg = "\nAnd the endpoint:".format(default_key_file)
        endpoint = ask_for_input(msg)

    save_key(key, endpoint, default_key_file)

    return key, endpoint


def interpret_glasses(glasses):
    if glasses != 'noGlasses':
        return "Glasses: {}".format(glasses)
    else:
        return "No glasses"


def interpret_emotion(emotion):
    emotion = max(vars(emotion), key=lambda attr: getattr(emotion, attr) if getattr(emotion, attr) else 0)
    return "Emotion: {}".format(emotion)


def interpret_occlusion(occlusion):
    res = []
    for k, v in vars(occlusion).items():
        if v:
            res.append(k)
    if res:
        return "Occlusion: {}".format(', '.join(res))
    else:
        return "No occlusion"


def show_detection_results(img_url, faces):
    bgr = read_cv_image_from(img_url)
    if faces:
        labels = {face.face_id: str(i) for i, face in enumerate(faces)}
        for face in faces:
            mark_face(bgr, getbox(face), text=labels[face.face_id])
            attrs = face.face_attributes
            print("    Face No. {}:".format(labels[face.face_id]))
            print("        Age: {}".format(attrs.age))
            print("        Gender: {}".format(attrs.gender))
            print("        {}".format(interpret_glasses(attrs.glasses)))
            print("        {}".format(interpret_emotion(attrs.emotion)))
            print("        {}".format(interpret_occlusion(attrs.occlusion)))
    else:
        print("    No faces found!")

    # Display the image in the users default image browser.

    display(bgr, frombgr=True)


def azface_detect(client, img_url, **kwargs):
    """Detect faces using Azure face API."""

    if is_url(img_url):  # Photo from URL
        # For return_face_attributes, it can be a FaceAttributeType, or a list of string
        faces = client.face.detect_with_url(img_url, **kwargs)
    else:  # Photo from a file
        with open(img_url, 'rb') as file:
            # For face attributes, it can be a FaceAttributeType, or a list of string
            faces = client.face.detect_with_stream(file, **kwargs)

    return faces


def azface_similar(client, target_url, target_faces, candidate_url, candidate_faces):
    if candidate_faces:
        matches = {}
        candidate_ids = [x.face_id for x in candidate_faces]
        labels = {face.face_id: str(i) for i, face in enumerate(target_faces)}

        msg = "\nMatching the face No. {} ..."
        for query_face in target_faces:
            print(msg.format(labels[query_face.face_id]))

            # Call Azure face API to find matches

            similar_faces = client.face.find_similar(query_face.face_id, face_ids=candidate_ids)

            # Update the best matched face

            if similar_faces:
                best_match = max(similar_faces, key=lambda face: face.confidence)
                match_face = next(x for x in candidate_faces if x.face_id == best_match.face_id)
                if match_face.face_id not in matches or matches[match_face.face_id][1] < best_match.confidence:
                    matches[match_face.face_id] = (query_face, best_match.confidence)

        # Mark matched faces

        target_bgr = read_cv_image_from(target_url)
        candidate_bgr = read_cv_image_from(candidate_url)

        for face in target_faces:
            mark_face(target_bgr, getbox(face), text=labels[face.face_id])

        for face in candidate_faces:
            if face.face_id in matches:
                mark_face(candidate_bgr, getbox(face), text=labels[matches[face.face_id][0].face_id])
            else:
                mark_face(candidate_bgr, getbox(face), text='?')

        # Plot results

        print("\nPlease close each image window (Ctrl-w) to proceed.")
        plot_side_by_side_comparison(
            *convert_cv2matplot(target_bgr, candidate_bgr),
            leftlabel='Target faces',
            rightlabel='Matched faces')

    else:
        print("No faces found in {}".format(candidate_url))


# ----------------------------------------------------------------------
# URL
# ----------------------------------------------------------------------

def is_url(url):
    """Check if url is a valid URL."""

    urlregex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if re.match(urlregex, url) is not None:
        return True
    else:
        return False


# ----------------------------------------------------------------------
# readline
# ----------------------------------------------------------------------

def tab_complete_path(text, state):
    if '~' in text:
        text = os.path.expanduser('~')

    if os.path.isdir(text):
        text += '/'

    return [x for x in glob.glob(text + '*')][state]
