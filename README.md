<div align="center" markdown>
<img src="https://i.imgur.com/ok6t92G.png"/>



# Ilastik Pixel Classification

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-To-Run">How To Run</a> •
  <a href="#How-To-Use">How To Use</a>
</p>

  
[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervise.ly/apps/ilastik-pixel-classification)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/ilastik-pixel-classification)
[![views](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/ilastik-pixel-classification&counter=views&label=views)](https://supervise.ly)
[![used by teams](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/ilastik-pixel-classification&counter=downloads&label=used%20by%20teams)](https://supervise.ly)
[![runs](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/ilastik-pixel-classification&counter=runs&label=runs&123)](https://supervise.ly)

</div>

## Overview

[ilastik](https://www.ilastik.org/) - the interactive learning and segmentation toolkit.

App uses ilastik machine learning algorithms to easily segment and classify your cells or other experimental data.
Most operations are interactive, even on large datasets: you just draw the labels and immediately see the result.

**ilastik** version used for app - **ilastik-1.4.0b14-Linux**

No machine learning expertise required.

When creating a new ilastik project you must select at least 2 target classes, all target classes must be bitmaps. 
All predicted labels are tagged with `ilastik_prediction` tag.

**Buttons functionality:**
**train tab:**
add to train set
train model

**predict tab**
remove 
predict

**settings**
save mode



## How To Run 
**Step 1**: Add app to your team from [Ecosystem](https://ecosystem.supervise.ly/apps/ilastik-pixel-classification) if it is not there.

**Step 2**: Open context images project click on `Apps` tab and  -> `ilastik pixel classification` 

<img src="https://i.imgur.com/4mqzfp8.png"/>

**Step 3**: Modal window

**1.** In the modal window select whether you want to use previously saved project or create a new one.

**2.** Depending on the selected mode select classes that you want to segment (at least 2 classes must be selected) or paste a path from Team Files to your previously saved project.

<img src="https://i.imgur.com/B4RUqnj.png" width="600px"/>

## How to use

Watch video guide for more details:

<a data-key="sly-embeded-video-link" href="https://youtu.be/z31-K7NAAbU" data-video-code="z31-K7NAAbU">
    <img src="https://i.imgur.com/Jf54wuS.png" alt="SLY_EMBEDED_VIDEO_LINK"  style="max-width:500px;">
</a>
