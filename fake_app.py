import argparse
import time
import logging
import monitor_units
from waggle.plugin import Plugin

class SystemMonitor:
    def __init__(self, monitoring_units=None):
        self.monitoring_units = monitoring_units or []

    def collect_metrics(self):
        metrics = {}
        for unit in self.monitoring_units:
            metrics.update(unit.process())
        return metrics

    def publish_metrics(self, plugin, metrics):
        for key, value in metrics.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    logging.info(f"Publishing: {key}.{sub_key}: {sub_value}")
            else:
                logging.info(f"Publishing: {key}: {value}")

    def run(self, plugin, interval, max_samples, debug=False):
        samples_published = 0

        while max_samples == 0 or samples_published < max_samples:
            if interval > 0:
                time.sleep(interval)
            metrics = self.collect_metrics()
            if debug:
                self.debug_publish(metrics)
            else:
                self.publish_metrics(plugin, metrics)
            samples_published += 1

    def debug_publish(self, metrics):
        logging.debug("=" * 30)
        for key, value in metrics.items():
            logging.debug(f"{key}: {value}")

def main():
    parser = argparse.ArgumentParser(description="System Performance Monitor")
    parser.add_argument("--debug", action="store_true", help="Enable debug logs")
    parser.add_argument("--interval", type=float, default=1.0, help="Interval between data publishes (in seconds)")
    parser.add_argument("--samples", type=int, default=60, help="Number of samples to publish (0 for infinite)")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S"
    )

    # Load monitoring units
    monitoring_units = [monitor_units.ProcStatMU(), monitor_units.ProcMeminfoMU(), monitor_units.SysBusI2CMU()]

    with Plugin() as plugin:
        monitor = SystemMonitor(monitoring_units)
        monitor.run(plugin, interval=args.interval, max_samples=args.samples, debug=args.debug)

if __name__ == "__main__":
    main()
