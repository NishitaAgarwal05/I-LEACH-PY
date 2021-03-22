
from src.LEACH_create_basics import *


def zeros(row, column):
    re_list = []
    for x in range(row):
        temp_list = [0 for _ in range(column)]
        if row == 1:
            re_list.extend(temp_list)
        else:
            re_list.append(temp_list)

    return re_list


def start(Sensors: list[Sensor], myModel, round_number: int):
    CH = []
    countCHs= 0 # no use
    n = myModel.n

    # numRx = myModel.numRx
    # dr = myModel.dr
    # CH_selected_arr = zeros(numRx, numRx)

    # sink can't be a CH
    for i in range(0,len(Sensors)):

        # # % these are the circle (x,y) for this node
        # row_circle_of_node = -1
        # col_circle_of_node = -1
        # br = 0
        #
        # # % checking in which circle this node lies
        # for row in range(numRx):
        #     for column in range(numRx):
        #         if (sqrt((Sensors[i].xd - circlex[row][column]) ^ 2 +
        #                  (Sensors[i].yd - circley[row][column]) ^ 2) <= dr / 2):
        #             row_circle_of_node = row
        #             col_circle_of_node = column
        #
        #             br = 1
        #             break
        #
        #     if br == 1:
        #         break
        #
        # # % if this node is not in any circle then also skip
        # if br == 0:
        #     continue
        #
        # # % if CH of this circle has already been chosen, then skip
        # if CH_selected_arr[row_circle_of_node][col_circle_of_node] == 1:
        #     continue

        # If current sensor has energy left and has not been CH before And it is not dead
        # todo: keep either 'senser.E > 0' or 'senser.df == 0'
        if Sensors[i].E > 0 :
            # Election of Cluster Heads
            temp_rand = random.uniform(0, 1)
            if Sensors[i].G <= 0:
                value = myModel.p / (1 - myModel.p * (round_number % round(1 / myModel.p)))
                print(f'for {Sensors[i].id}, temprand = {temp_rand}, value = {value}')
                if temp_rand <= value:
                    print(f"Adding {Sensors[i].id} to CH")
                    CH.insert(countCHs,Sensors[i].id)
                    Sensors[i].type = 'C'
                    Sensors[i].G = round(1 / myModel.p) - 1
                    countCHs += 1

                # # mark this cirle now that it has a CH
                # CH_selected_arr(row_circle_of_node, col_circle_of_node) = 1

    return CH
