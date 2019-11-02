# Face Recognition Service #

This [MLHub](https://mlhub.ai) package provides a quick introduction
to the pre-built Azure Face models. This service identifies faces
within a photo. This package is part of the [Azure on
MLHub](https://github.com/Azure/mlhub) repository.

In addition to the *demo* commed this package provides a collection of
commands that turn the service into useful *command line
tools* for detecting faces in supplied photos together with age,
gender, expression, and other observations about the face, and
identifying faces similar to a given face in a photo.

A free Azure subscription allowing up to 30,000 transactions per month
is available from https://azure.microsoft.com/free/.  After
subscribing visit https://ms.portal.azure.com and Create a resource
under AI and Machine Learning called Face.  Once created you can
access the web API subscription key from the portal.  This will be
prompted for in the demo.

Please note that these Azure models, unlike the MLHub models in
general, use *closed source services* which have no guarantee of
ongoing availability and do not come with the freedom to modify and
share.

Visit the github repository for more details:
https://github.com/azure/azface

The Python code is based on the [Microsoft Azure Face API
Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/Face/).

## Usage

* To install mlhub (e.g., Ubuntu 18.04 LTS)

```console
$ pip3 install mlhub
```

* To install and configure the pre-built model:

```console
$ ml install azface
$ ml configure azface
```

## Command Line Tools

In addition to the *demo* presented below, the *azface* package
provides a number of useful command line tools. Below we demonstrate a
number of these. Most commands take an image as a parameter which may
be a url or a path to a local file.  Commands include *detect* and
*similar* and being pipeline oriented means the output will be
CSV-like text that makes them easily incorporated into a command line
pipeline.

**detect**

To detect faces in a photo:

```console
$ ml detect azface ~/.mlhub/azface/photo/identification/identification1.jpg
302 202 302 315 415 315 415 202,31.0,male,no glasses,happiness,no occlusion
398 238 398 329 489 329 489 238,30.0,female,no glasses,happiness,no occlusion
495 238 495 320 577 320 577 238,4.0,female,no glasses,happiness,no occlusion
211 162 211 243 292 243 292 162,6.0,male,no glasses,happiness,no occlusion
```
  
  It will ask for your Azure face API key and endpoint the first time
  you use this command, then it will detect faces in the photo you
  provide.  The photo can be a path or URL to an image.  You also can
  provide the key and endpoint by command line options:
  
```console
$ ml detect azface --key 'xxx' --endpoint 'https://yyy' ~/.mlhub/azface/photo/identification/identification1.jpg
```

  Key and endpoint can also be stored in a file such as `key.txt`:
  
```
key = 'xxx'
endpoint = 'https://yyy'
```

  And they can be read by:
  
```console
$ ml detect azface --key-file key.txt ~/.mlhub/azface/photo/identification/identification1.jpg
```

**similar**

To find similar faces between two photos:

```console
$ ml similar azface xxx.jpg yyy.jpg
```
  
  Thus all faces in `yyy.jpg` that are similar to the faces in
  `xxx.jpg` will be found.

  **Examples**:

```console
$ ml similar azface ~/.mlhub/azface/photo/PersonGroup/Family1-Dad-Bill/Family1-Dad1.jpg ~/.mlhub/azface/photo/identification/identification1.jpg
14 59 14 205 160 205 160 59,302 202 302 315 415 315 415 202,0.7665841
,398 238 398 329 489 329 489 238,
,495 238 495 320 577 320 577 238,
,211 162 211 243 292 243 292 162,
```

## Pipeline ##

* To see how many faces in a photo (for example,
  `~/.mlhub/azface/photo/identification/identification1.jpg`)
  ![](photo/identification/identification1.jpg?raw=true)

```console
$ ml detect azface ~/.mlhub/azface/photo/identification/identification1.jpg | wc -l
4
```

* To tally the number of males and females in the photo:

```console
$ ml detect azface ~/.mlhub/azface/photo/identification/identification1.jpg | 
  cut -d ',' -f 3 | 
  sort | 
  uniq -c
2 female
2 male
```

* To find the youngest face in a photo:

```console
$ ml detect azface ~/.mlhub/azface/photo/identification/identification1.jpg |
  sort -t ',' -k 2 -n |
  head -1 |
  cut -d ',' -f 1 |
  xargs printf "-draw \'polygon %s,%s %s,%s %s,%s %s,%s\' " |
  awk '{print "~/.mlhub/azface/photo/identification/identification1.jpg -fill none -stroke red -strokewidth 5 " $0 "result.png"}' |
  xargs -I@ bash -c 'convert @'
$ xdg-open result.png
```
  ![](result/azface08.png?raw=true)

* To see how many faces in a photo
  (`~/.mlhub/azface/photo/identification/identification1.jpg`)
  ![](photo/identification/identification1.jpg?raw=true)
  
  similar to that in another photo
  (`~/.mlhub/azface/photo/PersonGroup/Family1-Dad-Bill/Family1-Dad1.jpg`):
  ![](photo/PersonGroup/Family1-Dad-Bill/Family1-Dad1.jpg?raw=true)

```console
$ ml similar azface ~/.mlhub/azface/photo/PersonGroup/Family1-Dad-Bill/Family1-Dad1.jpg ~/.mlhub/azface/photo/identification/identification1.jpg | 
  awk -F ',' '$1 != "" && $2 != "" {print $0}' | 
  wc -l
1
```
  
* To mark the faces similar between the photos
  `~/.mlhub/azface/photo/PersonGroup/Family1-Dad-Bill/Family1-Dad1.jpg`
  and `~/.mlhub/azface/photo/identification/identification1.jpg`, put
  the following script into a file called `result.sh`:

```bash
TARGET=$1
CANDIDATE=$2

ml similar azface ${TARGET} ${CANDIDATE} > result.txt

for line in "$(cat result.txt | awk -F ',' '$1 != "" && $2 != "" {print $0}')"; do
  echo "${line}" |
    awk -F ',' '{print $1}' |
    xargs printf "-draw \'polygon %s,%s %s,%s %s,%s %s,%s\' " |
    awk -v TARGET="${TARGET}" '{print TARGET " -fill none -stroke red -strokewidth 5 " $0 "result1.png"}' |
	xargs -I@ bash -c 'convert @'
  echo "${line}" |
    awk -F ',' '{print $2}' |
    xargs printf "-draw \'polygon %s,%s %s,%s %s,%s %s,%s\' " |
    awk -v CANDIDATE="${CANDIDATE}" '{print CANDIDATE " -fill none -stroke red -strokewidth 5 " $0 "result2.png"}' |
    xargs -I@ bash -c 'convert @'
  montage -background '#336699' -geometry +4+4 result1.png result2.png result.png
  xdg-open result.png
done
```
  
  then run the following command:
  
```console
$ bash result.sh ~/.mlhub/azface/photo/PersonGroup/Family1-Dad-Bill/Family1-Dad1.jpg ~/.mlhub/azface/photo/identification/identification1.jpg
```
  ![](result/azface09.png?raw=true)

* To count the number of faces in a crowd (for example, 
  `http://www.allwhitebackground.com/images/3/3818.jpg`)
  ![](http://www.allwhitebackground.com/images/3/3818.jpg)
  
```console
$ ml detect azface  http://www.allwhitebackground.com/images/3/3818.jpg | wc -l
35
```
* Males and Females:

```console
$ ml detect azface  http://www.allwhitebackground.com/images/3/3818.jpg | 
  cut -d ',' -f 3 | 
  sort | 
  uniq -c
     20 female
     15 male
```

* Bounding boxes:

```console
$ wget http://www.allwhitebackground.com/images/3/3818.jpg

$ ml detect azface  3818.jpg | 
  cut -d ',' -f 1 | 
  xargs printf "-draw \'polygon %s,%s %s,%s %s,%s %s,%s\' " |
  awk '{print "3818.jpg -fill none -stroke red -strokewidth 5 " $0 "3818bb.png"}' |
  xargs -I@ bash -c 'convert @'

$ eog result.png 
```

![](photo/3818bb.png?raw=true)

* How many might be wearing a cap (have their forehead occluded):

```console
$ ml detect azface http://www.allwhitebackground.com/images/3/3818.jpg | 
  grep forehead_occluded |
  wc -l
4
```

But there looks like just 3 are wearing caps. So let's check who:

```console
$ ml detect azface 3818.jpg |
  grep forehead_occluded |
  cut -d ',' -f 1 | 
  xargs printf "-draw \'polygon %s,%s %s,%s %s,%s %s,%s\' " |
  awk '{print "3818.jpg -fill none -stroke red -strokewidth 5 " $0 "3818cap.png"}' |
  xargs -I@ bash -c 'convert @'

$ eog 3818cap.png
```
![](photo/3818cap.png?raw=true)


## Demonstration

```console
$ ml demo azface
=============
Face Services
=============

Welcome to a demo of the pre-built models for Face provided through Azure's 
Cognitive Services. This cloud service accepts images and can perform 
various analyses of the images, returning the results locally.

An Azure resource is required to access this service (and to run this
demo). See the README for details of a free subscription. Then you can
provide the key and the endpoint information here.

Please paste your Face API subscription key []: ********************************
Please paste your endpoint []: https://australiaeast.api.cognitive.microsoft.com/face/v1.0

The Azure Face API subscription key and endpoint have been saved to:

  /home/gjw/.mlhub/azface/key.txt

Detecting faces in photo:
  photo/detection/detection2.jpg
Please close each image window (Ctrl-w) to proceed.
```
![](result/azface01.png?raw=true)
```console
Detecting faces in photo:
  photo/detection/detection3.jpg
Please close each image window (Ctrl-w) to proceed.
```
![](result/azface02.png?raw=true)
```console
Detecting faces in photo:
  photo/detection/detection6.jpg
Please close each image window (Ctrl-w) to proceed.
```
![](result/azface03.png?raw=true)
```console
Detecting faces in photo:
  photo/detection/detection1.jpg
Please close each image window (Ctrl-w) to proceed.
```
![](result/azface04.png?raw=true)
```console
Detecting faces in photo:
  photo/detection/detection5.jpg
Please close each image window (Ctrl-w) to proceed.
```
![](result/azface05.png?raw=true)
```console
Detecting faces in photo:
  photo/detection/detection4.jpg
Please close each image window (Ctrl-w) to proceed.
```
![](result/azface06.png?raw=true)
```console
Detecting faces in the target photo:
  photo/PersonGroup/Family1-Dad-Bill/Family1-Dad1.jpg

Detecting faces in the candidate photo:
  photo/identification/identification1.jpg

Matching the face No. 0 ...

Please close each image window (Ctrl-w) to proceed.
```
![](result/azface07.png?raw=true)
```console
To detect faces in provided photos:

  $ ml detect azface
```

## Contributing ##

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Legal Notices ##

Microsoft and any contributors grant you a license to the Microsoft documentation and other content
in this repository under the [Creative Commons Attribution 4.0 International Public License](https://creativecommons.org/licenses/by/4.0/legalcode),
see the [LICENSE](LICENSE) file, and grant you a license to any code in the repository under the [MIT License](https://opensource.org/licenses/MIT), see the
[LICENSE-CODE](LICENSE-CODE) file.

Microsoft, Windows, Microsoft Azure and/or other Microsoft products and services referenced in the documentation
may be either trademarks or registered trademarks of Microsoft in the United States and/or other countries.
The licenses for this project do not grant you rights to use any Microsoft names, logos, or trademarks.
Microsoft's general trademark guidelines can be found at http://go.microsoft.com/fwlink/?LinkID=254653.

Privacy information can be found at https://privacy.microsoft.com/en-us/

Microsoft and any contributors reserve all other rights, whether under their respective copyrights, patents,
or trademarks, whether by implication, estoppel or otherwise.


## Reference ##

* [Quickstart: Create a Python script to detect and frame faces in an image](https://docs.microsoft.com/en-us/azure/cognitive-services/Face/Tutorials/FaceAPIinPythonTutorial)
* [Microsoft Face API: Python SDK & Sample](https://github.com/Microsoft/Cognitive-Face-Python)

