# %% Standard Leach in MATLAB Developed by Amin Nazari
# %   aminnazari91@gmail.com
# %   0918 546 2272
# %% Improved Leach Developed by Hritwik Singhal and Nishita Agarwal
# However this Python code is Created entirely by Hritwik and Nishita

from src import LEACH

if __name__ == '__main__':
    myLeach = LEACH.LEACHSimulation(n=5)
    myLeach.start()