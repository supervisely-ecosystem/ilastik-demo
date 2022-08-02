<div align="center" markdown>
<img src="https://user-images.githubusercontent.com/48245050/182394465-02065ae9-b8a9-4073-93cd-94b74d0aa3a1.png"/>



# Ilastik Pixel Classification

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-To-Run">How To Run</a> •
  <a href="#How-To-Use">How To Use</a>
</p>

  
[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervise.ly/apps/ilastik-pixel-classification)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/ilastik-pixel-classification)
[![views](https://app.supervise.ly/img/badges/views/supervisely-ecosystem/ilastik-pixel-classification)](https://supervise.ly)
[![used by teams](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/ilastik-pixel-classification&counter=downloads&label=used%20by%20teams)](https://supervise.ly)
[![runs](https://app.supervise.ly/img/badges/runs/supervisely-ecosystem/ilastik-pixel-classification)](https://supervise.ly)

</div>

## Overview

[ilastik](https://www.ilastik.org/) - the interactive learning and segmentation toolkit.
(**ilastik** version used for app - **ilastik-1.4.0b14-Linux**)

App uses ilastik machine learning algorithms to easily segment and classify your cells or other experimental data.
Most operations are interactive, even on large datasets: you just draw the labels and immediately see the result.
No machine learning expertise is required.

## How To Run 
**Step 1**: Add app to your team from [Ecosystem](https://ecosystem.supervise.ly/apps/ilastik-pixel-classification) if it is not there.

**Step 2**: Open images project click on `Apps` tab and run `ilastik pixel classification` app.

<img src="https://i.imgur.com/4mqzfp8.png"/>

**Step 3**: Modal window

**1.** In the modal window select whether you want to use a previously saved project with a trained classifier or create a new one.

**2.** Depending on the selected mode select classes that you want to segment (at least 2 classes must be selected) or paste a path from Team Files to your previously saved project.

<img src="https://i.imgur.com/B4RUqnj.png" width="600px"/>

## How to use

* When creating a new ilastik project you must select **at least 2 target classes**, all target classes must have **bitmap** shape.

* When loading the existing project all target classes from the saved project and `ilastik_prediction` tag will be added to the target project meta automatically. If you want to edit the target classes, you will have to create a new project via the app with desired classes. The existing project is ready to build predictions as it already contains the images in the train set and trained classifier.

**Note:** You can add images to the training set from different projects and workspaces within one Team.

**App buttons functionality**

**1. - info tab -**

* <img src="https://i.imgur.com/YQ5GEyJ.png"/>

**-** Synchronize target classes and prediction tag with current project. Helpful when you add images to the training set from different projects.

**2. - train tab -**

* <img src="https://i.imgur.com/E8DGTid.png"/> 

  **-** Add image to the training set. Training image name is image id in supervisely server.

* <img src="https://i.imgur.com/lFrPX8a.png"/> 

  **-** Remove image from train set. Click **✕** to remove image.

* <img src="https://i.imgur.com/wlhkmrZ.png"/> 

  **-** Train classifier with images from current training set.

**3. - predict tab -**

* <img src="https://i.imgur.com/ZbDABZB.png"/> 

  **-** Remove all labels with `ilastik_prediction` tag from current image.

* <img src="https://i.imgur.com/mKKw7bP.png"/> 

  **-** Build predictions for current image. All predicted labels are tagged with `ilastik_prediction` tag. 
        The tag will be created automatically on the app launch.

**4. - settings tab -**

* <img src="https://i.imgur.com/9SOehlM.png"/> 

  **-** Save ilastik project to ilastik folder in Team Files. Disabled by default, requires project name input. Trained `.ilp` classifier can be found inside saved project folder.


Watch video guide for more details:

<a data-key="sly-embeded-video-link" href="https://youtu.be/3Nf73GIju5w" data-video-code="3Nf73GIju5w">
    <img src="https://i.imgur.com/Jf54wuS.png" alt="SLY_EMBEDED_VIDEO_LINK"  style="max-width:500px;">
</a>
