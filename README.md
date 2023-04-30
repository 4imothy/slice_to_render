## Project to Convert Collection of Images to a File and Render the File

#### Use:
**(Recommended) Create Virtual Environment:**
```
python3 -m venv env
```
**Install Dependencies:**
```
pip install -r requirements.txt
```
```
python src/main.py
```
**Example:**
```
python src/main.py -rc --slices=slices/mri --output=output.ply
```

#### Arguments:
**-r, --render:** Use render mode
**-c, --convert:** Use convert mode
**-s, --slices:** The directory to be read containing the slices
**-i, --input:** The file to be rendered
**-o, --output:** The file that is written with the information in the tif images

#### Packages Used:
* [taichi](https://github.com/taichi-dev/taichi)
* [plyfile](https://github.com/dranjan/python-plyfile)
* [opencv](https://github.com/opencv/opencv-python)

### Todo
* [ ] Add support for tif files with multiple images
* [ ] Make it work with resolutions $\neq$ $(100, 100)$
* [ ] Implement rendering directly from tif directory
* [ ] Ignore the background
* [ ] read other image filetypes
