"""
Penguin Training Pipeline
"""
from kfp import dsl
from kfp.v2 import compiler
from components.train import train_tabular_model
from components.deploy import conditional_deploy

@dsl.pipeline(
    name="penguin-training-pipeline",
    description="Train and deploy penguin classifier"
)
def penguin_pipeline(
    project: str,
    region: str,
    bq_table: str,
):
    # Train
    train_op = train_tabular_model(
        project=project,
        bq_table=bq_table
    )

    # Deploy (Conditional)
    conditional_deploy(
        model=train_op.outputs["model"],
        project=project,
        region=region,
        accuracy=train_op.outputs["metrics"].output_value_picker("accuracy")
    )

if __name__ == "__main__":
    compiler.Compiler().compile(
        pipeline_func=penguin_pipeline,
        package_path="penguin_pipeline.json"
    )
