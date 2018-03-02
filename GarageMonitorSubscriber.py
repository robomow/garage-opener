from interface import Interface

class GarageMonitorSubscriber(Interface):

    def vehicleDetected(self, vehicle):
        pass

