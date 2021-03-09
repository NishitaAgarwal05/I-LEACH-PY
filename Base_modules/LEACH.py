from Base_modules import LEACH_configureSensors
from Base_modules import LEACH_selectCH
from Base_modules import LEACH_setParameters
from Base_modules import createRandomSen
from Base_modules import disToSink
from Base_modules import LEACH_plotter
from Base_modules import findReceiver
from Base_modules import findSender
from Base_modules import joinToNearestCH
from Base_modules import resetSensors
from Base_modules import sendReceivePackets

################################################################
# todo :test
import pprint


def var_pp(stuff):
    pp = pprint.PrettyPrinter(indent=1)
    for x in stuff:
        pp.pprint(vars(x))


def pp(stuff):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(stuff)


################################################################

class LEACH:

    def __init__(self, n=200):
        # After every "AroundClear" rounds, let every sensor be CH again
        self.AroundClear = 1 / self.myModel.p
        self.n = n  # Number of Nodes in the field

    def __zeros(self, row, column):
        re_list = []
        for x in range(row):
            temp_list = [0 for _ in range(column)]
            if row == 1:
                re_list.extend(temp_list)
            else:
                re_list.append(temp_list)

        return re_list

    def start(self):
        print(" ################# Initial Parameters #############")

        # ######################### Initial Parameters #######################
        # Create sensor nodes, Set Parameters and Create Energy self.Model
        self.myArea, self.myModel = LEACH_setParameters.setParameters(self.n)  # Set Parameters self.Sensors and Network

        # todo: test
        print("self.myArea")
        print(vars(self.myArea))
        print("self.myModel")
        print(vars(self.myModel))
        print('----------------------------------------------')

        # ######################### configuration Sensors ####################
        self.__conf_sen()

        # todo: test
        print("Sensors X co-ordinates:")
        pp(self.X)
        print("Sensors Y co-ordinates:")
        pp(self.Y)
        print()
        var_pp(self.Sensors)
        print('----------------------------------------------')

        # todo: Plot sensors Here
        # self.myplot = LEACH_plotter.start(self.Sensors, self.Model, self.deadNum)

        # ############# Parameters initialization #############
        self.__init_param()

        # todo: test
        print("self.initEnergy", self.initEnergy)
        print("self.SRP", self.SRP)
        print("len(self.SRP)", len(self.SRP))
        print("self.RRP", self.RRP)
        print("self.SDP", self.SDP)
        print("self.RDP", self.RDP)
        print("self.Sum_DEAD", self.Sum_DEAD)
        print("self.CLUSTERHS", self.CLUSTERHS)
        print("self.AllSensorEnergy", self.AllSensorEnergy)
        print('----------------------------------------------')

        # ############# Start Simulation ##############
        self.__start_sim(self.n)

        # todo: test
        print("self.Sender", self.sender)
        print("self.receivers ", end='')
        pp(self.receivers)
        var_pp(self.Sensors)
        print('self.srp', self.srp)
        print('self.rrp', self.rrp)
        print('self.sdp', self.sdp)
        print('self.rdp', self.rdp)
        print('----------------------------------------------')

        # ############# Main loop program ##############
        self.__main_loop()

        # todo: test
        print(' ################# END #############')
        print('----------------------XXX----------------------')

    def __conf_sen(self):
        print(" ################# configuration Sensors #############")

        # Create a random scenario & Load sensor Location
        self.X, self.Y = createRandomSen.start(self.myModel, self.myArea)

        # configure sensors
        self.Sensors = LEACH_configureSensors.start(self.myModel, self.n, self.X, self.Y)
        # self.deadNum = 0  # Number of dead nodes

    def __init_param(self):
        print('############# Parameters initialization #############')

        # self.countCHs = 0  # counter for CHs      # Declared in __init__
        self.flag_first_dead = 0  # flag_first_dead
        self.deadNum = 0  # Number of dead nodes

        self.initEnergy = 0  # Initial Energy
        for sensor in self.Sensors:
            self.initEnergy += sensor.E

        # Below will be of length(Max_rounds) so each element will store the total packets in each round
        # the length is rmax + 1 since we take one initialization round also.
        self.SRP = self.__zeros(1, self.myModel.rmax + 1)  # number of sent routing packets
        self.RRP = self.__zeros(1, self.myModel.rmax + 1)  # number of receive routing packets
        self.SDP = self.__zeros(1, self.myModel.rmax + 1)  # number of sent data packets
        self.RDP = self.__zeros(1, self.myModel.rmax + 1)  # number of receive data packets

        # total_energy_dissipated = zeros(1,Model.rmax)
        self.Sum_DEAD = self.__zeros(1, self.myModel.rmax)
        self.CLUSTERHS = self.__zeros(1, self.myModel.rmax)
        self.AllSensorEnergy = self.__zeros(1, self.myModel.rmax)

    def __start_sim(self, n):
        print("############# Start Simulation #############")

        self.srp = 0  # counter of number of sent routing packets
        self.rrp = 0  # counter of number of receive routing packets
        self.sdp = 0  # counter of number of sent data packets
        self.rdp = 0  # counter of number of receive data packets

        # Sink broadcast 'Hello' message to all nodes
        self.sender = [self.n]  # List of senders, for start_sim, sink will send hello packet to all
        self.receivers = [x for x in range(n)]  # List of senders, for start_sim, All nodes will receive from sink

        self.srp, self.rrp, self.sdp, self.rdp = sendReceivePackets.start(
            self.Sensors, self.myModel, self.sender, 'Hello', self.receivers, self.srp, self.rrp, self.sdp, self.rdp
        )

        # All sensors location information to Sink .
        disToSink.start(self.Sensors, self.myModel)

        # Save metrics
        self.SRP[0] = self.srp
        self.RRP[0] = self.rrp
        self.SDP[0] = self.sdp
        self.RDP[0] = self.rdp

        self.x = 0

    def __main_loop(self):
        print(" ################# Main loop program #############")

        for r in range(1, self.myModel.rmax + 1):
            # ####### Initialization #######
            self.__initialization_main_loop(r)

            print('####### plot Sensors #######')
            # ####### plot Sensors #######
            self.deadNum, self.circlex, self.circley = LEACH_plotter.start(self.Sensors, self.myModel)

            # Save the period in which the first node died
            if self.deadNum > 0 and self.flag_first_dead == 0:
                self.first_dead = r
                self.flag_first_dead = 1

            # ####### cluster head election #######
            self.__CH_selection_phase(r)

            # %%%%%%%%%%%%%%%%%%%%%%% plot network status in end of set-up phase
            # %%%%%%%%%%%%%%%%%%%%%%% this will draw lines from every node to its CH

            # %     for i=1:n
            # %
            # %         if (Sensors(i).type=='N' && Sensors(i).dis2ch<Sensors(i).dis2sink && ...
            # %                 Sensors(i).E>0)
            # %
            # %             XL=[Sensors(i).xd ,Sensors(Sensors(i).MCH).xd];
            # %             YL=[Sensors(i).yd ,Sensors(Sensors(i).MCH).yd];
            # %             hold on
            # %             line(XL,YL)

            '''
            What has been done till now:
            All Ch are elected 
            All nodes know which CH they should send to
            '''
            # Todo: done till here
            exit()

            # ######## steady-state phase ######
            self.__steady_state_phase()

            # Todo: STATISTICS

            # Sum_DEAD(r) = deadNum
            #
            # SRP(r) = srp
            # RRP(r) = rrp
            # SDP(r) = sdp
            # RDP(r) = rdp
            #
            # CLUSTERHS(r) = countCHs
            #
            # alive = 0
            # SensorEnergy = 0
            # for i=1:n
            # if self.Sensors(i).E > 0
            #     alive = alive + 1
            #     SensorEnergy = SensorEnergy + self.Sensors(i).E
            #
            # AliveSensors(r) = alive  # #ok
            #
            # SumEnergyAllSensor(r) = SensorEnergy  # #ok
            #
            # AvgEnergyAllSensor(r) = SensorEnergy / alive  # #ok
            #
            # ConsumEnergy(r) = (initEnergy - SumEnergyAllSensor(r)) / n  # #ok
            #
            # En = 0
            # for i=1:n
            # if self.Sensors(i).E > 0
            #     En = En + (Sensors(i).E - AvgEnergyAllSensor(r)) ^ 2
            #
            # Enheraf(r) = En / alive  # #ok
            #
            # title(sprintf('Round=##d,Dead nodes=##d', r, deadNum))
            #
            # # #dead
            # if (n == deadNum)
            #
            #     lastPeriod = r
            #     break

    def __initialization_main_loop(self, r):
        print('####### Initialization #######')

        # This section Operate for each epoch
        # self.member = []  # Member of each cluster in per period      # Not used
        # self.countCHs = 0  # Number of CH in per period               # Not Used
        # #counter for bit transmitted to Bases Station and Cluster Heads
        self.srp = 0  # counter number of sent routing packets
        self.rrp = 0  # counter number of receive routing packets
        self.sdp = 0  # counter number of sent data packets to sink
        self.rdp = 0  # counter number of receive data packets by sink
        # initialization per round
        self.SRP[r] = self.srp
        self.RRP[r] = self.rrp
        self.SDP[r] = self.sdp
        self.RDP[r] = self.rdp
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # self.packets_TO_BS = 0
        resetSensors.start(self.Sensors, self.myModel)
        # allow to sensor to become cluster-head. LEACH Algorithm
        if r % self.AroundClear == 0:
            for sensor in self.Sensors:
                sensor.G = 0

    def __CH_selection_phase(self, r):
        print('####### cluster head election #######')

        # Selection Candidate Cluster Head Based on LEACH Set-up Phase
        # self.list_CH stores the id of all CH in current round
        self.list_CH = LEACH_selectCH.start(self.Sensors, self.myModel, r, self.circlex, self.circley)

        # todo: test
        print('self.list_CH: ', end='')
        pp(self.list_CH)
        print()

        # ####### Broadcasting CHs #######
        self.__broadcast_CH()

        # Sensors join to nearest CH
        joinToNearestCH.start(self.Sensors, self.myModel, self.list_CH)

        # todo: test
        print("\nSensors:")
        var_pp(self.Sensors)
        print()
        print("\nModel:")
        print(vars(self.myModel))
        print()

        # Todo: plot here
        print('####### end of cluster head election phase #######')
        # ####### end of cluster head election phase #######

    def __broadcast_CH(self):
        print('####### Broadcasting CHs to All Sensors that are in Radio Rage CH. #######')
        # Broadcasting CHs to All Sensors that are in Radio Rage CH.
        # each CH will broadcast to all nodes within its range.
        for ch_id in self.list_CH:
            senderRR = self.myModel.RR  # Radio range of sender
            self.receivers: list = findReceiver.start(self.Sensors, self.myModel, ch_id, senderRR)

            # todo: test
            print("sender: ", ch_id)
            print('self.Receivers: ', end='')
            print(self.receivers)

            # we require the sender parameter of sendReceivePackets.start to be a list.
            sendReceivePackets.start(
                self.Sensors, self.myModel, [ch_id], 'Hello', self.receivers, self.srp, self.rrp, self.sdp, self.rdp
            )

    def __steady_state_phase(self):
        print()
        # # Number of Packets sent in steady-state phase
        # self.NumPacket = self.myModel.NumPacket   # Not used
        # # changed from 1 to self.myModel.NumPacket
        for i in range(1):  # NumPacket
            # todo: Plotter
            # [deadNumo, circlex, circley] = LEACH_plotter.start(self.Sensors, self.Model)

            # ######## All sensor send data packet to CH ########
            for j in range(len(self.list_CH)):
                self.receiver = self.list_CH[j]
                self.sender = findSender.start(self.Sensors, self.receiver)
                self.Sensors = sendReceivePackets.start(self.Sensors, self.myModel, self.sender, 'Data',
                                                        self.receiver)
        # ### send Data packet from CH to Sink after Data aggregation ###
        for i in range(len(self.list_CH)):
            self.receivers = self.n  # Sink
            self.sender = self.list_CH[i]  # #CH
            self.Sensors = sendReceivePackets.start(self.Sensors, self.myModel, self.sender, 'Data',
                                                    self.receivers)
        # send Data packet directly from other nodes(that aren't in each cluster) to Sink
        for sensor in self.Sensors:
            if sensor.MCH == self.Sensors[self.n].id:  # if it is sink
                self.receivers = self.n  # #Sink
                self.sender = sensor.id  # Other Nodes
                sendReceivePackets.start(self.Sensors, self.myModel, self.sender, 'Data', self.receivers)
