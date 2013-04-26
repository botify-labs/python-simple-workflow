#! -*- coding:utf-8 -*-

# Copyright (c) 2013, Theo Crevon
# Copyright (c) 2013, Greg Leclercq
#
# See the file LICENSE for copying permission.

from swf.utils import enum


EVENT_TYPE = enum(
	'ACTIVITY',
	'DECISION',
	'CHILD_WORKFLOW',
	'WORKFLOW',
	'SIGNAL_RECEIVED',
	'SIGNAL_SENT',
	'TIMER_RECEIVED',
	'TIMER_SET',
	'WORKFLOW_SIGNALED',
	'NOT_IMPLEMENTED',
)


EVENT_STATUS = enum(
	'START_REQUESTED',
	'START_FAILED',
	'STARTED',
	'CANCEL_REQUESTED',
	'CANCEL_FAILED',
	'CANCELED',
	'OK',
	'FAILED',
	'TIMEOUT',
	'SIGNALED',
	'UNKNOWN',
)


EVENT_NAMES = [
    'WorkflowExecutionStarted',
    'WorkflowExecutionCompleted',
    'WorkflowExecutionFailed',
    'WorkflowExecutionTimedOut',
    'WorkflowExecutionCanceled',
    'WorkflowExecutionTerminated',
    'WorkflowExecutionContinuedAsNew',
    'WorkflowExecutionCancelRequested',
    'DecisionTaskScheduled',
    'DecisionTaskStarted',
    'DecisionTaskCompleted',
    'DecisionTaskTimedOut',
    'ActivityTaskScheduled',
    'ScheduleActivityTaskFailed',
    'ActivityTaskStarted',
    'ActivityTaskCompleted',
    'ActivityTaskFailed',
    'ActivityTaskTimedOut',
    'ActivityTaskCanceled',
    'ActivityTaskCancelRequested',
    'RequestCancelActivityTaskFailed',
    'WorkflowExecutionSignaled',
    'MarkerRecorded',
    'TimerStarted',
    'StartTimerFailed',
    'TimerFired',
    'TimerCanceled',
    'CancelTimerFailed',
    'StartChildWorkflowExecutionInitiated',
    'StartChildWorkflowExecutionFailed',
    'ChildWorkflowExecutionStarted',
    'ChildWorkflowExecutionCompleted',
    'ChildWorkflowExecutionFailed',
    'ChildWorkflowExecutionTimedOut',
    'ChildWorkflowExecutionCanceled',
    'ChildWorkflowExecutionTerminated',
    'SignalExternalWorkflowExecutionInitiated',
    'ExternalWorkflowExecutionSignaled',
    'SignalExternalWorkflowExecutionFailed',
    'RequestCancelExternalWorkflowExecutionInitiated',
    'ExternalWorkflowExecutionCancelRequested',
    'RequestCancelExternalWorkflowExecutionFailed',
]