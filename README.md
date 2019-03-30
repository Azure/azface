# azface #

This MLHub package provides a quick introduction to the pre-built Face
models provided through the face API of Microsoft Azure's Cognitive
Services.

A free Azure subscription allowing up to 5,000 transactions per month
is available from https://azure.microsoft.com/free/.  Once set up
visit https://ms.portal.azure.com and Create a resource under AI and
Machine Learning called Face. Once created you can access the web API
subscription key from the portal. This will be prompted for in the
demo.

Please note that this is *closed source software* which limits your
freedoms and has no guarantee of ongoing availability.

Visit the github repository for more details:
https://github.com/gjwgit/azface

The Python code is based on the [Microsoft Azure Face API
Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/Face/).


## Prerequisites ##

To use the
[Azure face API](https://azure.microsoft.com/en-us/services/cognitive-services/face/),
you need to have an Azure subscription.  You can get a 7-days free
subscription account at
[Try Cognitive Services](https://azure.microsoft.com/en-us/try/cognitive-services/?api=face-api).


## Usage ##

* To install mlhub 

  ```console
  $ pip3 install mlhub
  ```

* To install and configure the pre-built model:

  ```console
  $ ml install gjwgit/azface
  $ ml configure azface
  ```

* To see a quick demostration of what this package can do:

  ```console
  $ ml demo azface
  ```

* To detect faces in a photo:

  ```console
  $ ml detect azface
  ```
  
  It will ask for your Azure face API key, endpoint, as well as a URL
  or path of a photo to detect faces.  You also can provide these by
  command line options:
  
  ```console
  $ ml detect azface --key 'xxx' --endpoint 'https://yyy' --photo '~/.mlhub/azface/photo/detection'
  ```

  Key and endpoint can also be stored in a file such as `key.txt`:
  
  ```
  key = 'xxx'
  endpoint = 'https://yyy'
  ```

  And they can be read by:
  
  ```console
  $ ml detect azface --key-file key.txt --photo '~/.mlhub/azface/photo/detection'
  ```

* To find similar faces between two photos:

  ```console
  $ ml similar azface --target xxx.jpg --candidate yyy.jpg --key-file zzz.txt
  ```
  
  Thus all faces in `yyy.jpg` that are similar to the faces in
  `xxx.jpg` will be found.

  **Examples**:

  ```console
  $ ml similar azface --target '~/.mlhub/azface/photo/PersonGroup/Family1-Dad-Bill/Family1-Dad1.jpg' --candidate '~/.mlhub/azface/photo/identification/identification1.jpg'
  $ ml similar azface --target '~/.mlhub/azface/photo/identification/identification1.jpg' --candidate '~/.mlhub/azface/photo/PersonGroup/Family1-Dad-Bill/'
  ```


## Reference ##

* [Quickstart: Create a Python script to detect and frame faces in an image](https://docs.microsoft.com/en-us/azure/cognitive-services/Face/Tutorials/FaceAPIinPythonTutorial)
* [Microsoft Face API: Python SDK & Sample](https://github.com/Microsoft/Cognitive-Face-Python)

