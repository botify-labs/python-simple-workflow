import inspect


class InvalidWorkflowConfigError(Exception):
    pass


def split_step_name(step_name):
    step_module = None
    step_method = None

    if '.' in step_name:
        step_module, step_method = step_name.split(".")
    else:
        step_method = step_name

    return step_module, step_method


def is_valid_workflow_step_input(obj, step):
    """Validates that the workflow *step* input matches *obj* method arguments.

    :param obj: instance exposing the step method
    :type  obj: object

    :param workflow: workflow definition
    :type  workflow: botify.saas.backend.workflow.declarative.workflow.Workflow

    """
    _, step_method = split_step_name(step.name)

    method = getattr(obj, step_method, None)
    if method is None or not callable(method):
        return False

    # arguments and inputs might be in a different order.
    method_args = set(inspect.getargspec(method).args[1:])
    step_input_args = set(str(i.split("=")[0]) for i in step.input)

    return method_args == step_input_args
