import logger
import executable
from abc import ABC


class Stage(executable.Executable, ABC):
    """
    Base class for all testing stages.


    ...

    Methods
    -------
    log(message)
        write a message to the specific log file using a parent module name
    get_logger()
        return associated logger
    """

    def __init__(self, parent_module_name, interrupt_if_fail, log_file_path, stage_name, is_logging,
                 pre_script_path, main_script_path, post_script_path, only_fail_notification):
        """
        Parameters
        ----------
        log_file_path : str
            an absolute path to directory for the log file
        stage_name : str
            stage name
        is_logging : bool
            write messages to the log file or not
        interrupt_if_fail : bool
            interrupt the execution of the all stages if an error has occurred
        parent_module_name: str
            a parent module name
        pre_script_path : str
            script for pre_exec()
        main_script_path : str
            script for exec()
        post_script_path : str
            script for post_exec()
        only_fail_notification : bool
            notification condition
        """
        executable.Executable.__init__(self, interrupt_if_fail, pre_script_path, main_script_path, post_script_path)
        self._logger = logger.Logger(log_file_path, parent_module_name + '.' + stage_name, is_logging,
                                     only_fail_notification)
        self._parent_module_name = parent_module_name
        self._stage_name = stage_name

    def log(self, message):
        """
        Write a message to the specific log file using a parent module name.

        Parameters
        ----------
        message : str
           a message for writing to the log file
        """
        self._logger.log(self._parent_module_name + '.' + self._stage_name + ': ' + message)

    def get_logger(self):
        """
        Return associated logger.
        """
        return self._logger
