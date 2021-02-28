from math import *
from LEACH_setParameters import *


def start(Sensors, Model: Model, Sender, PacketType, Receiver, srp, rrp, sdp, rdp):
    # global srp, rrp, sdp, rdp

    sap = 0  # Send a packet
    rap = 0  # Receive a packet
    if PacketType == 'Hello':
        PacketSize = Model.HpacketLen
    else:
        PacketSize = Model.DpacketLen

    # Energy dissipated from Sensors for S a packet
    for i in range(len(Sender)):
        for j in range(len(Receiver)):
            distance = sqrt((Sensors[Sender[i]].xd - Sensors[Receiver[j]].xd) ^ 2 +
                            (Sensors[Sender[i]].yd - Sensors[Receiver[j]].yd) ^ 2)

            if distance > Model.do:
                Sensors[Sender[i]].E = Sensors[Sender[i]].E - (
                        Model.ETX * PacketSize + Model.Emp * PacketSize * (distance ^ 4))

                # % Sent a packet
                if Sensors[Sender[i]].E > 0:
                    sap = sap + 1
            else:
                Sensors[Sender[i]].E = Sensors[Sender[i]].E - (
                        Model.ETX * PacketSize + Model.Efs * PacketSize * (distance ^ 2))

                # % Sent a packet
                if Sensors[Sender[i]].E > 0:
                    sap += 1

    # %Energy dissipated from sensors for Receive a packet
    for j in range(len(Receiver)):
        Sensors[Receiver[j]].E = Sensors[Receiver[j]].E - ((Model.ERX + Model.EDA) * PacketSize)

    for i in range(len(Sender)):
        for j in range(len(Receiver)):

            # Received a Packet
            if (Sensors[Sender[i]]).E > 0 and Sensors[Receiver[j]].E > 0:
                rap += 1

    if PacketType == 'Hello':
        srp += sap
        rrp += rap
    else:
        sdp += sap
        rdp += rap


'''

%     else %To Cluster Head
%         
%         for i=1:length( Sender)
%        
%            distance=sqrt((Sensors(Sender(i)).xd-Sensors(Sender(i).MCH).xd)^2 + ...
%                (Sensors(Sender(i)).yd-Sensors(Sender(i).MCH).yd)^2 );   
%        
%            send a packet
%            sap=sap+1;
%            
%            Energy dissipated from Normal sensor
%            if (distance>Model.do)
%            
%                 Sensors(Sender(i)).E=Sensors(Sender(i)).E- ...
%                     (Model.ETX*PacketSize + Model.Emp*PacketSize*(distance^4));
% 
%                 if(Sensors(Sender(i)).E>0)
%                     rap=rap+1;                 
%                 end
%             
%            else
%                 Sensors(Sender(i)).E=Sensors(Sender(i)).E- ...
%                     (Model.ETX*PacketSize + Model.Emp*PacketSize*(distance^2));
% 
%                 if(Sensors(Sender(i)).E>0)
%                     rap=rap+1;                 
%                 end
%             
%            end 
%        end
  


'''