from .monitor_unit import MonitorUnit
import os
import atexit

class ProcStatMU(MonitorUnit):
    cpu_metric_map = {
        'user': 0, 'nice': 1, 'system': 2, 'idle': 3,
        'iowait': 4, 'irq': 5, 'softirq': 6, 'steal': 7
    }

    def __init__(self, metrics=None):
        """
        Initialize the ProcStatMU with an optional list of metrics to track.
        If no metrics are provided, it defaults to tracking all available metrics.
        """
        self.filename = '/proc/stat'
        self.file = open(self.filename, 'r')
        self.metrics = metrics if metrics else ['user', 'system', 'idle'] 
        self.metric_indices = [ProcStatMU.cpu_metric_map[metric] for metric in self.metrics]
        self.cpus = ['cpu'] + [f'cpu{i}' for i in range(os.cpu_count())]
        self.prev_cpu_metrics = self.get_cpu_metrics(self.get_contents())
        atexit.register(self.close_file)

    def get_contents(self):
        """Retrieve the current contents of the monitored unit."""
        self.file.seek(0)
        lines = {}
        for line in self.file.readlines():
            parts = line.strip().split()
            key = parts[0]
            values = [int(i) for i in parts[1:]]
            lines[key] = values
        return lines

    def get_cpu_metrics(self, contents):
        """Retrieve the current state of cpus"""
        cpu_metrics = {}
        for cpu in self.cpus:
            cpu_metrics[cpu] = contents[cpu]
        return cpu_metrics

    def process_cpus(self, contents):
        curr_state = self.get_cpu_metrics(contents)
        
        # Compute delta state
        cpu_values = {}
        for cpu in self.cpus: 
            key_name = f'perf.stat.proc.{cpu}'
            prev_metrics = self.prev_cpu_metrics[cpu]
            curr_metrics = curr_state[cpu]
            cpu_values[key_name] = [curr - prev for prev, curr in zip(prev_metrics, curr_metrics)]

            row_sum = max(sum(cpu_values[key_name]), 1)
            cpu_values[key_name] = [round(i/row_sum * 100) for i in cpu_values[key_name]]
            cpu_values[key_name] = [cpu_values[key_name][i] for i in self.metric_indices]
            cpu_values[key_name] = dict(zip(self.metrics, cpu_values[key_name]))

        # Update previous cpu state
        self.prev_cpu_metrics = curr_state
        return cpu_values

    def process(self):
        contents = self.get_contents()
        cpu_values = self.process_cpus(contents)

        results = {}
        results.update(cpu_values)
        return results

    def close_file(self):
        """Close the /proc/stat file."""
        if not self.file.closed:
            self.file.close()
