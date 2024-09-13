"""
    1.  VDD_IN: This is the main input voltage rail for the system. It represents the total power being supplied to the system from an external power source.
    2.  VDD_CPU_GPU_CV: This voltage rail supplies power to the CPU, GPU, and possibly other computational cores. It’s critical for the operation of these high-performance components.
    3.  VDD_SOC: This stands for System on Chip (SoC) voltage. It supplies power to the SoC, which includes various integrated components like the CPU, GPU, memory controllers, and other peripherals.
"""
from .monitor_unit import MonitorUnit
import atexit

class SysBusI2CMU(MonitorUnit):
    def __init__(self):
        self.prefix = '/sys/bus/i2c/devices/7-0040/iio_device/'
        self.current_filenames = [f'{self.prefix}in_current{i}_input' for i in range(3)]
        self.voltage_filenames = [f'{self.prefix}in_voltage{i}_input' for i in range(3)]

        self.files = {
            'VDD_IN': self._open_files(0),
            'VDD_CPU_GPU_CV': self._open_files(1),
            'VDD_SOC': self._open_files(2)
        }

    def _open_files(self, index):
        return [open(self.current_filenames[index], 'r'), open(self.voltage_filenames[index], 'r')]

    def get_contents(self):
        """Retrieve the current and voltage contents of the monitored unit."""
        lines = {}
        for key, files in self.files.items():
            current_file, voltage_file = files
            current_file.seek(0)
            voltage_file.seek(0)
            
            current = int(current_file.read().strip())
            voltage = int(voltage_file.read().strip())
            
            lines[key] = [current, voltage]
        return lines

    def calculate_power(self, contents):
        power = {}
        for key, values in contents.items():
            key_name = f'perf.sys.bus.i2c.{key.lower()}'
            current, voltage = values
            # Convert to watts (current * voltage / 1,000,000)
            power[key_name] = (current * voltage) / 1000000
        return power

    def process(self):
        contents = self.get_contents()
        power_values = self.calculate_power(contents) 

        results = {}
        results.update(power_values)
        return results

    def close_file(self):
        for _, files in self.files.items():
            for file in files:
                file.close()
