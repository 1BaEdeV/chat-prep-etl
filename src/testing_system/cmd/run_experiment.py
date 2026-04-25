import argparse
import asyncio

from testing_system.internal.adapter.config.yaml_loader import YamlConfigLoader
from testing_system.internal.usecase.ExperimentBuilder import ExperimentBuilder


async def run_experiment(config_path: str):
    config = YamlConfigLoader().load(config_path)
    build = ExperimentBuilder().build(config)
    return await build.runner.run(build.experiment)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run testing system experiment")
    parser.add_argument("config", help="Path to experiment YAML config")
    args = parser.parse_args()

    experiment = asyncio.run(run_experiment(args.config))

    print(f"Experiment: {experiment.id}")
    print(f"Answers: {len(experiment.answers)}")
    print(f"Metrics: {len(experiment.metrics)}")

    for answer in experiment.answers:
        print(f"\n[{answer.id}] {answer.text}")

    for metric in experiment.metrics:
        print(f"{metric.type.value}: {metric.value}")


if __name__ == "__main__":
    main()
