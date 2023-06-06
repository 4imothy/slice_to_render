## Project to Convert Collection of Images to a File and Render the File

Will be used in *RWC* to send smaller images to a web interface.

### *UML* Diagram

[diagram](./uml/diagram.svg)

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

#### Packages Used:
* [taichi](https://github.com/taichi-dev/taichi)
* [plyfile](https://github.com/dranjan/python-plyfile)
* [opencv](https://github.com/opencv/opencv-python)

### Todo
* [ ] Make functions be *ti.kernels* and *ti.func* to speed up
* [ ] Make it work with resolutions $\neq$ $(100, 100)$
* [ ] Add color and custom render options
* [ ] Add the UML outline
