from .monitor_unit import MonitorUnit
import time
import atexit

class ProcMeminfoMU(MonitorUnit):

    # Available metrics:

    # memtotal, memfree, memavailable, buffers, cached, swapcached, active,
    # inactive, active(anon), inactive(anon), active(file), inactive(file),
    # unevictable, mlocked, swaptotal, swapfree, zswap, zswapped, dirty,
    # writeback, anonpages, mapped, shmem, kreclaimable, slab, sreclaimable,
    # sunreclaim, kernelstack, pagetables, secpagetables, nfs_unstable, bounce,
    # writebacktmp, commitlimit, committed_as, vmalloctotal, vmallocused,
    # vmallocchunk, percpu, anonhugepages, shmemhugepages, shmempmdmapped,
    # filehugepages, filepmdmapped, hugepages_total, hugepages_free,
    # hugepages_rsvd, hugepages_surp, hugepagesize, hugetlb

    def __init__(self, metrics=None):
        """
        Initialize the ProcMeminfoMU with an optional list of metrics to track.
        If no metrics are provided, it defaults to tracking all available metrics.
        """
        self.filename = '/proc/meminfo'
        self.file = open(self.filename, 'r')
        self.metrics = metrics
        atexit.register(self.close_file)

    def get_contents(self):
        """Retrieve the current contents of the monitored unit."""
        self.file.seek(0)
        lines = {}
        for line in self.file.readlines():
            line_split = line.strip().replace(':', '').split()
            key = line_split[0].lower()
            values = int(line_split[1])
            lines[key] = values
        return lines

    def get_activity_metrics(self, contents):
        activity_metrics = {}
        mem_total = contents['memtotal']
        mem_free = contents['memfree']
        if not self.metrics:
           activity_metrics['perf.proc.meminfo.mem_used'] = round((mem_total - mem_free) / mem_total * 100) 

        return activity_metrics

    def process(self):
        """
        Process the memory information and return 
        metrics along with rate of change.
        """
        contents = self.get_contents()
        mem_values = self.get_activity_metrics(contents)

        results = {}
        results.update(mem_values)
        return results

    def close_file(self):
        """Close the /proc/meminfo file."""
        if not self.file.closed:
            self.file.close()
