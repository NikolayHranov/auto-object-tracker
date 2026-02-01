# auto-object-tracker
Unattended, color-based object tracking for batch video processing.


## Features:
- Color-based object detection and tracking
- Fully automatic batch processing of videos
- Recursive configuration with partial overrides
- Multiprocessing support

## Installation

```bash
git clone https://github.com/NikolayHranov/auto-object-tracker.git
```

## Quick Start

```python
from src.tracking import Track

Track("path/to/setup/track.json", processes=5)
```


### Configuration files

The tracking information is given in the form of JSON files with the following fields:

```json
{
    "subdirs": [],
    "dirs": [],
    "settings": {}
}
```

#### `"settings"`

Processing and tracking parameters

```json
"settings": {
    "c_hsv": ...,
    "c_hsv_range": ...,

    "failed_frames_limit": ...,

    "size_ratio": ...,
    "fps": ...
}
```

Required fields:
- `"c_hsv"` - target object color in HSV format

Fields with default values:
- `"c_hsv_range"` - maximum allowed deviation from `"c_hsv"`
- `"failed_frames_limit"` - number of consecutive failed frames before tracking stops

_Default values are defined in `src/default-settings.json`._
  
Optional fields:
- `"size_ratio"` - spatial scale [m/pixel] for the video
- `"fps"` - video frame rate


#### `"dirs"`
A list of directories (relative or absolute paths) containing videos to be tracked.

#### `"subdirs"`
A list of other setup JSON files to be executed recursively.
- Settings from the parent file are inherited
- Child files override only the fields they define


### `settings.json`

Inside the directory of the processed videos you can add a file named `settings.json`. Before the processing starts the program will check for this file and if it exists it will modify the settings for the specific directory.

In this file (and only this file) you can choose the videos from the directory to be ignored in the processing (not be processed).

`settings.json`
```json
{
    "ignore": ["ignored_video_1.mp4", "ignored_video_2.mp4"],
    "settings": {

    }
}
```


### Example

`track.json`
```json
{
    "subdirs": ["path/to/track-green.json", "path/to/track-blue.json"],
    "settings": {
        "failed_frames_limit": 5,
        "c_hsv_range": [20, 50, 50]
    }
}
```

`track-green.json`
```json
{
    "dirs": ["path/to/folder/experiments-green"]
    "settings": {
        "c_hsv": [50, 127, 195]
    }
}
```

`track-blue.json`
```json
{
    "dirs": ["path/to/folder/experiments-blue"]
    "settings": {
        "c_hsv": [115, 190, 190],
        "failed_frames_limit": 7
    }
}
```

In our case we have `track.json` that points to `track-green.json` and `track-blue.json`.

For the green tracking settings we will have `track.json` | `track-green.json`:
```json
"settings": {
    "c_hsv": [50, 127, 195],
    "c_hsv_range": [20, 50, 50],
    "failed_frames_limit": 5
}
```

For the blue tracking settings we will have `track.json` | `track-blue.json`:
```json
"settings": {
    "c_hsv": [115, 190, 190],
    "c_hsv_range": [20, 50, 50],
    "failed_frames_limit": 7
}
```

As you can see, the child file modifies the mentioned fields of the settings.

For the processing to happen the settings have only one required field - `"c_hsv"`, the other fields are optional and if not mentioned `default-settings.json` will be used for them.