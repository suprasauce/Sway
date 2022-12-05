# Sway

![](https://github.com/suprasauce/Sway/blob/main/demo.gif)

This project titled “Sway” approaches the idea of neuroevolution by using the NEAT algorithm to point towards an optimal solution for the given task. The environment is set up as a virtual simulation in an accelerated time frame and NEAT is performed over generations until a solution is achieved. The task involves determining various dynamic values which help propagate the motion of entities in the virtual simulation towards a favourable direction leading to an optimum.

Dark purple coloured square represents the human playing, while the other light purple coloured squares represent different AI agent's playing.
The task is to hit the red colored square box.

## Installation

### Windows
1. Clone the project on your local machine in your prefered directory by typing the following command in git bash/ Powershell/ CMD (or download the file yourself)

```
git clone https://github.com/suprasauce/Sway.git
```

2. Install [python](https://www.python.org/) for windows if you don't have it (preferably python 3.8+). Activate a virtual environment in Powershell/ CMD by either installing virtualenv and following its instructions to make a virtual environment, or by using the venv package which comes with python by default

```
python -m venv env
```
This will make a folder named env.
Then type 

(Powershell)
```
path_where_env_is_stored\env\Scripts\Activate.ps1
```
(CMD)
```
path_where_env_is_stored\env\Scripts\activate
```

3. Go to the project directory <br />
To install all the dependencies, run
```
pip install -r requirements.txt
```

4. Run the game.py file by typing the following command in CMD/ Powershell (make sure virtual env is activated) in the directory where you cloned the folder

```
python game.py
```

## Reference
https://nn.cs.utexas.edu/downloads/papers/stanley.ec02.pdf
