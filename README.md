# N-Plot
Plots Nginx URL hits by on a graph parsing an access log file.

![cli](/doc/output_2.png)
![server](/doc/output_1.png)

# Instructions
- Clone the repository
```
git clone https://github.com/OpeOnikute/n-plot.git
```
- Install virtualenv if you haven't
```
sudo pip install virtualenv
```
- Set up your virtual environment
```sh
virtualenv ./.venv
source ./.venv/bin/activate
pip3 install -r requirements.txt
```
- Run the program. It requires Python 3.
```
./main.py or 
python3 main.py
```