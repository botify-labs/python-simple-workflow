import unittest

import swf.models
import swf.models.decision
import swf.actors


class TestDecider(unittest.TestCase):
    def setUp(self):
        self.domain = swf.models.Domain("TestDomain")
        self.task_list = 'test'
        self.execution = None

    def tearDown(self):
        if self.execution is not None:
            self.execution.terminate()

    def test_poll(self):
        """
        Checks :meth:`Decider.poll` retrieve all the history's pages.

        """
        domain = self.domain
        task_list = self.task_list
        workflow_name = 'TestDeciderPoll'

        decider = swf.actors.Decider(domain, task_list)
        worker = swf.actors.ActivityWorker(domain, task_list)

        activity = swf.models.ActivityType(domain=domain,
                                           name='task',
                                           version='test')

        workflow = swf.models.WorkflowType(name=workflow_name,
                                           domain=domain,
                                           version='test')
        self.execution = workflow.start_execution(workflow_name, task_list)

        for i in xrange(30):
            token, history = decider.poll()
            self.assertEqual(len(history), 3 + i * 6)
            decision = swf.models.decision.task.ActivityTaskDecision(
                'schedule',
                'task',
                activity,
                task_list=task_list,
                task_timeout='600',
                duration_timeout='600',
                schedule_timeout='600',
                heartbeat_timeout='600')
            decider.complete(token, [decision])

            token, task = worker.poll()
            worker.complete(token)
