import pandas as pd
import matplotlib.pyplot as plt
from math import ceil, floor

predict_window = 4  # this is the window to calculate the pedestrians
suggest_interval = 2  # this is the interval between two suggestion about how many and where car to send
busL = 8
busM = 4
busS = 2


def Plot_TravelDemand(csv_name: str):
    df = DF_TravelDemand(csv_name)
    df.plot(x='t0', y='weight')
    plt.show()


def DF_TravelDemand(csv_name: str):
    df = pd.read_csv(csv_name, delimiter=';', header=0)
    return df


def Sort_Pedestrians(pedestrians: list):
    sort_pedes = pedestrians
    getocc = lambda entry: entry.depart
    sort_pedes.sort(key=getocc)
    return sort_pedes


def Calc_Pedestrian_Interval(sorted_pedestrians: list, timestamp: int, predict_window: int, count: int):
    sum = 0
    for pedestrian in sorted_pedestrians[count:]:
        if ceil(pedestrian.depart) <= timestamp:
            pass
        else:
            if ceil(pedestrian.depart) <= (timestamp + predict_window):
                sum += 1
            else:
                if ceil(pedestrian.depart) > (timestamp + predict_window):
                    break
    return sum


def Calc_Pedestrian_List(sorted_pedestrians: list, time_scale: int, predict_window: int, suggest_interval: int):
    List_sum = []
    count = 0
    for i in range(time_scale):
        if i % suggest_interval == 0:
            if (i + suggest_interval) < (time_scale):
                sum = Calc_Pedestrian_Interval(sorted_pedestrians, i, predict_window, count)
                List_sum.append(sum)
                count += sum
            else:
                sum = Calc_Pedestrian_Interval(sorted_pedestrians, i, suggest_interval, count)
                List_sum.append(sum)
                count += sum
        else:
            List_sum.append(0)
    return List_sum


def Bus_Arrange(sum_list: list, time_scale: int, sorted_pedestrians: list):
    List_bus_person = []
    count = 0
    for i in range(time_scale):
        if (i % suggest_interval == 0):
            num_busL = floor(sum_list[i] / busL)
            rest = sum_list[i] % busL
            num_busM = floor(rest / busM)
            rest = rest % busM
            num_busS = ceil(rest / busS)
            List_bus_person.append(([num_busL, num_busM, num_busS], sorted_pedestrians[count:count + int(sum_list[i])]))
            count = count + int(sum_list[i])
        else:
            List_bus_person.append(([0, 0, 0], []))

    return List_bus_person


def Fast(pedestrians: list, timespan: int):
    sort_ped = Sort_Pedestrians(pedestrians)
    sum_list = Calc_Pedestrian_List(sort_ped, timespan, predict_window, suggest_interval)
    List_bus_person = Bus_Arrange(sum_list, timespan, sort_ped)
    return List_bus_person