import swf.models
import swf.querysets

from .workflow import Workflow
from .step import make as make_step
from .step import GroupStepDefinition
from .signal import Signal


__all__ = ['from_config']


class ExtractionError(Exception):
    pass


def extract_model(data, using=None, create_if_missing=False):
    """Extracts a swf.model instance from json data
    using an instantiated swf Queryset object.

    :param  data: representation of the model as json
    :type   data: dict

    :param  using: Queryset instance to use in order to get or
                   get_or_create the remote model matching the provided
                   json description.
    :type   qs: swf Queryset

    :param  create_if_missing: defines if .get or .get_or_create
                               method should be used when retrieving
                               target model instance
    :type   create_if_missing: bool

    :param  arguments: let's you restrain the json representation field
                       you'd wanna use for the model extraction
    :type   arguments: list

    :rtype: swf.models.BaseModel subclass
    :returns: extracted model instance
    """
    extraction_method = using.get_or_create if create_if_missing else using.get

    try:
        return extraction_method(**data)
    except TypeError:
        raise ExtractionError(
            "Missing argument when instanciating '{}'".format(using))


STEP_TYPE_TO_QUERYSET = {
    'activity': swf.querysets.ActivityTypeQuerySet,
    'workflow': swf.querysets.WorkflowTypeQuerySet,
}

STEP_TYPE_TO_MODEL = {
    'activity': swf.models.ActivityType,
    'workflow': swf.models.WorkflowType,
}

PATTERNS = {
    'group': GroupStepDefinition,
}


def step_from_raw(domain, workflow, raw_step, logger_name=None):
    try:
        model_class = STEP_TYPE_TO_MODEL[raw_step['type']]
    except KeyError:
        ValueError('invalid step type: {}'.format(
                   raw_step['type']))

    model = model_class(domain, **raw_step['description'])
    inputs = raw_step.get('input', None)
    outputs = raw_step.get('output', None)
    retry = raw_step.get('retry', 0)

    step = make_step(model, inputs, outputs, retry)

    pattern = PATTERNS.get(raw_step.get('pattern'))
    if pattern is not None:
        step = pattern(raw_step['key'], step)

    main_task_list = workflow.get('task_list')
    this_task_list = raw_step['description'].get('task_list')
    if this_task_list:
        step.task_list = this_task_list
    elif main_task_list:
        step.task_list = main_task_list

    logging.getLogger(logger_name).debug(
        '{} will be scheduled on task_list {}'.format(step, step.task_list)
    )

    return step


def extract_step(domain, workflow, raw_step):
    """Extracts a model from a raw step content (json)

    :param  domain: domain the step is attached to
    :type   domain: swf.models.domain.Domain

    :param  raw_step: raw step content
    :type   raw_step: dict

    :returns: extracted step, step inputs, step outputs
    :rtype: swf.models.Model, list(string), list(string)
    """
    return step_from_raw(domain, workflow, raw_step)


def get_default_signal_target(domain, raw_signal, default_version):
    activity_name = raw_signal['description']['name']
    activity_type = swf.querysets.ActivityTypeQuerySet(domain)
    activities = activity_type.filter(name=activity_name)
    if not activities:
        target = swf.models.ActivityType(domain,
                                         name=activity_name,
                                         version=default_version)
        target.save()
    else:
        target = activities[-1]

    return make_step(target)


def extract_signal(domain, workflow, raw_signal, default_version=None):
    description = raw_signal['description']
    raw_target = raw_signal['description'].get('target')
    target = (extract_step(domain, workflow, raw_target) if
              raw_target else
              get_default_signal_target(domain, raw_signal,
                                        default_version))

    signal = Signal(description['name'],
                    target=target,
                    input=description.get('input'))
    return signal


def get_function(name):
    module_name, function_name = name.rsplit('.', 1)
    module = __import__(module_name, fromlist=['*'])
    return getattr(module, function_name)


def extract_steps(domain, workflow):
    for number, raw_step in enumerate(workflow['steps']):
        step = extract_step(domain, workflow, raw_step)
        step.number = number

        yield step


def extract_signals(domain, workflow):
    main_task_list = workflow.get('task_list')

    for raw_signal in workflow.get('signals', []):
        signal = extract_signal(domain, workflow, raw_signal)
        name = raw_signal['description']['name']
        this_task_list = (raw_signal['description']
                          .get('target', {})
                          .get('description', {})
                          .get('task_list'))
        if this_task_list:
            signal.target.task_list = this_task_list
        elif main_task_list:
            signal.target.task_list = main_task_list

        yield name, signal


def from_config(config):
    """
    Generate a decider coordination logic from a workflow configuration.

    :param  data: representation of the model as json
    :type   data: dict

    :returns: a Workflow instance representing the configuration
    :rtype: .Workflow
    """
    from . import domain as Domain
    domain = swf.querysets.DomainQuerySet().get_or_create(
        Domain.get_name(), Domain.get_version())

    workflow = config['workflow']

    steps = list(extract_steps(domain, workflow))
    signals = {name: signal for name, signal in
               extract_signals(domain, workflow)}

    for number, signal in enumerate(signals.itervalues(), len(steps)):
        signal.target.number = number

    setup = config.get('setup')
    if setup:
        setup = get_function(setup)

    teardown = config.get('teardown')
    if teardown:
        teardown = get_function(teardown)

    return Workflow(workflow['name'],
                    workflow['version'],
                    domain,
                    workflow['task_list'],
                    workflow.get('output', []),
                    steps,
                    signals,
                    setup,
                    teardown)
