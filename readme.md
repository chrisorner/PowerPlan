# PowerPlan

*Help house owners to increase their understanding of complex photovoltaic solutions*

## How it works

**Individual load profiles** The first step is to create a detailed load profile of the household’s energy consumption. Instead of using standard load profiles like other software, PowerPlan uses a special algorithm to create load profiles based on high level statistics and stochastic processes. These profiles not only consider the consumption of various devices but also their flexibility. Controlling these flexible loads is the most cost-efficient way to utilize solar energy. 

**Determining system components** In the second step the size of the energy system is determined. Most critical component thereby is the battery. The size of the battery highly depends on the behaviour and living conditions of the inhabitants which makes the creation of an individual load profile so important. If flexible loads such as electric vehicles, air condition, electric heating, etc. can be controlled to be active whenever the sun shines the most, the size of the battery can be reduced or perhaps completely avoided. Since the battery is the most expensive component in the energy system, this will highly impact the return of investment of the energy system. The app simulates and optimizes the energy consumption of the household by shifting the available flexible loads into times with high solar radiation. It then calculates the ROI of the optimum system and gives a recommendation to the house owner.


## Getting Started
Inside this directory, type the following commands in the command prompt

**Create new virtual environment**
```
python -m venv .venv
```
**Activate virtual environment**
```
.venv\Scripts\activate.bat
```
**Install packages**
```
pip install -r requirements.txt
```
**run application**
```
python run.py
```
To use the application you first need to sign up.
