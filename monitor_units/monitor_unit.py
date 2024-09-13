from abc import ABC, abstractmethod

class MonitorUnit(ABC):
    @abstractmethod
    def get_contents(self):
        """Retrieve the current contents of the monitored unit."""
        pass

    @abstractmethod
    def process(self):
        """Process and return the output based on the values provided to the class."""
        pass      

    @abstractmethod
    def close_file(self):
        """Close any resources associated with the monitored unit."""
        pass
