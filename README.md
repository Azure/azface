# azface #

Azure face API MLHub model

## Prerequisites ##

To use the
[Azure face API](https://azure.microsoft.com/en-us/services/cognitive-services/face/),
you need to have an Azure subscription.  You can get a 7-days free
subscription account at
[Try Cognitive Services](https://azure.microsoft.com/en-us/try/cognitive-services/?api=face-api).


## Usage ##

* To install:

  ```console
  $ pip3 install mlhub
  $ ml install simonzhaoms/azface
  $ ml configure azface
  ```

* To detect faces in a photo:

  ```console
  $ ml detect azface
  ```
  
  It will ask for your Azure face API key, endpoint, as well as a URL
  or path of a photo to detect faces.  You also can provide these by
  command line options:
  
  ```console
  $ ml detect azface --key 'xxx' --endpoint 'https://yyy' --photo 'https://raw.githubusercontent.com/Microsoft/Cognitive-Face-Windows/master/Data/detection1.jpg'
  ```

  Key and endpoint can also be stored in a file such as `key.txt`:
  
  ```
  key = 'xxx'
  endpoint = 'https://yyy'
  ```

  And they can be read by:
  
  ```console
  $ ml detect azface --key-file key.txt --photo 'https://raw.githubusercontent.com/Microsoft/Cognitive-Face-Windows/master/Data/detection1.jpg'
  ```


## Reference ##

* [Quickstart: Create a Python script to detect and frame faces in an image](https://docs.microsoft.com/en-us/azure/cognitive-services/Face/Tutorials/FaceAPIinPythonTutorial)
* [Microsoft Face API: Python SDK & Sample](https://github.com/Microsoft/Cognitive-Face-Python)

