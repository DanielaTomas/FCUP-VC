# Rubik's Cube Solver

We develop a Rubik’s cube solver that uses computer vision techniques to detect and analyze the colors on each face of the cube and then generate a sequence of moves to solve it. 

## Installation

[Python 3](https://www.python.org/) must be installed and the following libraries are required:
* [NumPy](https://numpy.org/)
* [OpenCv](https://opencv.org/get-started/)
* [Kociemba](https://pypi.org/project/kociemba/)

## How to run

```
python3 main.py
```

## How to use

* Run the script, and it will initialize the camera to capture the Rubik's cube.

* Hold the Rubik's cube in front of the camera, ensuring that each face is detected and highlighted in the requested order.

* Once all six faces are detected, the solution will be displayed and the steps to solve the Rubik's cube will be shown in real time.

## Troubleshooting

* If the camera is not detected or the script encounters any issues, check the camera connection and make sure the required libraries are installed.

* If the cube is not beig detected and highlighted, you will probably need to change the HSV color ranges in [main.py](main.py).