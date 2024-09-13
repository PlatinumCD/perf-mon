import argparse
import time
import logging
import monitor_units
from waggle.plugin import Plugin
from contextlib import contextmanager

@contextmanager
def log_time(name):
    start = time.perf_counter()
    yield
    duration = time.perf_counter() - start
    logging.info(f'Section {name} took {duration}s')

class Monitor:
    def __init__(self, units=None):
        self.units = units

    def collect(self):
        values = {}
        for unit in self.units:
            values.update(unit.process())
        return values

    def publish(self, plugin, values):
        for key, value in values.items():
            plugin.publish(key, value)
        plugin.publish_flush()

    def debug_publish(self, values):
        logging.debug("=" * 30)
        for key, value in values.items():
            logging.debug(f"{key}: {value}")

    def run(self, plugin, interval, samples, debug=False):
        total_published = 0
        next_publish = time.time()
        while True:
            if samples > 0 and total_published >= samples:
                break
            with log_time("collect"):
                values = self.collect()
            now = time.time()
            if now >= next_publish:
                with log_time("publish"):
                    if debug:
                        self.debug_publish(values)
                    else:
                        self.publish(plugin, values)
                next_publish = now + interval
                total_published += 1
            time.sleep(0.01)  # Sleep briefly to prevent tight loop

def main():
    parser = argparse.ArgumentParser(description="System Performance Monitor")
    parser.add_argument("--debug", action="store_true", help="Enable debug logs")
    parser.add_argument("--interval", type=float, default=1.0, help="Interval between data publishes (in seconds)")
    parser.add_argument("--samples", type=int, default=0, help="Number of samples to publish (0 for infinite)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,
                        format="%(asctime)s %(levelname)s: %(message)s",
                        datefmt="%Y/%m/%d %H:%M:%S")

    # Load monitoring units (could be made dynamic based on arguments)
    units = [monitor_units.ProcStatMU(), monitor_units.ProcMeminfoMU()]

    with Plugin() as plugin:
        monitor = Monitor(units)
        monitor.run(plugin, interval=args.interval, samples=args.samples, debug=args.debug)

if __name__ == "__main__":
    main()
