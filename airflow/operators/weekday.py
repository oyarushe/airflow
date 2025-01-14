#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from typing import Iterable, Union

from airflow.operators.branch import BaseBranchOperator
from airflow.utils import timezone
from airflow.utils.context import Context
from airflow.utils.weekday import WeekDay


class BranchDayOfWeekOperator(BaseBranchOperator):
    """
    Branches into one of two lists of tasks depending on the current day.
    For more information on how to use this operator, take a look at the guide:
    :ref:`howto/operator:BranchDayOfWeekOperator`

    :param follow_task_ids_if_true: task id or task ids to follow if criteria met
    :type follow_task_ids_if_true: str or list[str]
    :param follow_task_ids_if_false: task id or task ids to follow if criteria does not met
    :type follow_task_ids_if_false: str or list[str]
    :param week_day: Day of the week to check (full name). Optionally, a set
        of days can also be provided using a set.
        Example values:

            * ``"MONDAY"``,
            * ``{"Saturday", "Sunday"}``
            * ``{WeekDay.TUESDAY}``
            * ``{WeekDay.SATURDAY, WeekDay.SUNDAY}``

    :type week_day: iterable or airflow.utils.weekday.WeekDay
    :param use_task_execution_day: If ``True``, uses task's execution day to compare
        with is_today. Execution Date is Useful for backfilling.
        If ``False``, uses system's day of the week.
    :type use_task_execution_day: bool
    """

    def __init__(
        self,
        *,
        follow_task_ids_if_true: Union[str, Iterable[str]],
        follow_task_ids_if_false: Union[str, Iterable[str]],
        week_day: Union[str, Iterable[str]],
        use_task_execution_day: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.follow_task_ids_if_true = follow_task_ids_if_true
        self.follow_task_ids_if_false = follow_task_ids_if_false
        self.week_day = week_day
        self.use_task_execution_day = use_task_execution_day
        self._week_day_num = WeekDay.validate_week_day(week_day)

    def choose_branch(self, context: Context) -> Union[str, Iterable[str]]:
        if self.use_task_execution_day:
            now = context["logical_date"]
        else:
            now = timezone.make_naive(timezone.utcnow(), self.dag.timezone)

        if now.isoweekday() in self._week_day_num:
            return self.follow_task_ids_if_true
        return self.follow_task_ids_if_false
