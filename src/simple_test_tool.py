from build.cmake import Cmake
from build.custom import Custom
from build.make import Make
from module import Module
from notification.mail import Email
from notification.telegram_bot import Telegram
from test import Test
from vcs.commit import Commit
from vcs.git import Git
from vcs.svn import SVN
import xml.etree.ElementTree as ET
import sys
import os


def create_vcs_stage(stage_root, module_name):
    stage_type = stage_root.get('Type')
    paths = []
    for path in stage_root.findall('Path'):
        paths.append(path.get('Path'))
    log_enable = True if stage_root.get('LogEnable') == 'On' else False
    log_path = ''

    if log_enable:
        log_path = stage_root.get('LogPath')

    interrupt_on_fail = True if stage_root.get('InterruptOnFail') == 'On' else False
    only_fail_notification = True if stage_root.get('OnlyFailNotification') == 'On' else False

    if stage_type == 'Git':
        return Git(paths, module_name, interrupt_on_fail, log_enable, log_path, 'Git', only_fail_notification)
    elif stage_type == 'SVN':
        return SVN(paths, module_name, interrupt_on_fail, log_enable, log_path, 'SVN', only_fail_notification)
    else:
        return None


def create_commit_stage(stage_root, module_name):
    stage_type = stage_root.get('Type')
    paths = []
    for path in stage_root.findall('Path'):
        paths.append(path.get('Path'))
    log_enable = True if stage_root.get('LogEnable') == 'On' else False
    auto_commit_and_push = True if stage_root.get('AutoCommitAndPush') == 'On' else False
    log_path = ''

    if log_enable:
        log_path = stage_root.get('LogPath')

    only_fail_notification = True if stage_root.get('OnlyFailNotification') == 'On' else False

    vcs_obj = None
    if stage_type == 'Git':
        vcs_obj = Git(paths, module_name, False, log_enable, log_path, 'Git-Commit', only_fail_notification)
    elif stage_type == 'SVN':
        vcs_obj = SVN(paths, module_name, False, log_enable, log_path, 'SVN-Commit', only_fail_notification)

    return Commit(auto_commit_and_push, module_name, log_enable, log_path, vcs_obj)


def create_build_stage(stage_root, module_name):
    stage_type = stage_root.get('Type')
    stage_path = stage_root.get('Path')
    log_enable = True if stage_root.get('LogEnable') == 'On' else False
    log_path = ''

    if log_enable:
        log_path = stage_root.get('LogPath')

    interrupt_on_fail = True if stage_root.get('InterruptOnFail') == 'On' else False

    targets_list = []
    for target in stage_root.findall('Target'):
        targets_list.append(target.get('Name'))

    pre_script_path = ""
    main_script_path = ""
    post_script_path = ""

    pre_script = stage_root.find("PreScript")
    if pre_script is not None:
        pre_script_path = pre_script.get("Path")
    main_script = stage_root.find("MainScript")
    if main_script is not None:
        main_script_path = main_script.get("Path")
    post_script = stage_root.find("PostScript")
    if post_script is not None:
        post_script_path = post_script.get("Path")

    only_fail_notification = True if stage_root.get('OnlyFailNotification') == 'On' else False

    if stage_type == 'CMake':
        return Cmake(stage_path, module_name, interrupt_on_fail, log_enable, log_path, 'CMake', targets_list,
                     pre_script_path, main_script_path, post_script_path, only_fail_notification)
    elif stage_type == 'Make':
        return Make(stage_path, module_name, interrupt_on_fail, log_enable, log_path, 'Make', targets_list,
                    pre_script_path, main_script_path, post_script_path, only_fail_notification)
    elif stage_type == 'Custom':
        return Custom(stage_path, module_name, interrupt_on_fail, log_enable, log_path, 'Custom', targets_list,
                      pre_script_path, main_script_path, post_script_path, only_fail_notification)
    else:
        return None


def create_notification_stage(stage_root, loggers):
    stage_type = stage_root.get('Type')

    if stage_type == 'Email':
        email_to = stage_root.get('EmailTo')
        email_from = stage_root.get('EmailFrom')
        smtp_ip = stage_root.get('SmtpServerAddress')
        smtp_port = stage_root.get('SmtpServerPort')
        password = stage_root.get('Password')

        return Email(loggers, smtp_ip, int(smtp_port), email_from, password, email_to)
    elif stage_type == 'Telegram':
        token = stage_root.get('Token')
        chat_id = stage_root.get('ChatID')

        return Telegram(loggers, token, chat_id)
    else:
        return None


def create_test_stage(stage_root, module_name):
    path = ""
    path_tag = stage_root.find('MainScript')
    if path_tag is not None:
        path = path_tag.get('Path')

    log_enable = True if stage_root.get('LogEnable') == 'On' else False
    log_path = ''

    if log_enable:
        log_path = stage_root.get('LogPath')

    interrupt_on_fail = True if stage_root.get('InterruptOnFail') == 'On' else False
    only_fail_notification = True if stage_root.get('OnlyFailNotification') == 'On' else False

    return Test(path, module_name, interrupt_on_fail, log_enable, log_path, only_fail_notification)


def read_outputs(outputs_root):
    outputs_list = []
    for output in outputs_root.findall('Output'):
        outputs_list.append((output.get('Name'), output.get('Path')))

    return outputs_list


def read_dependencies(dependencies_root):
    dependencies_list = []
    for dependency in dependencies_root.findall('Dependency'):
        dependencies_list.append([dependency.get('Name'), dependency.get('Path'), None])

    return dependencies_list


def create_module(module_root):
    module_name = module_root.get('Name')

    stages = [None] * Module.STAGES_NUM  # array of stages
    loggers = []  # array of the loggers
    stages_root = module_root.find('Stages')
    for stage in stages_root:
        if stage.tag == 'Build':
            stages[Module.BUILD_STAGE] = create_build_stage(stage, module_name)
            i = Module.BUILD_STAGE
            print('Created Build stage for ' + module_name)
        elif stage.tag == 'VCS':
            stages[Module.VCS_STAGE] = create_vcs_stage(stage, module_name)
            i = Module.VCS_STAGE
            print('Created VCS stage for ' + module_name)
        elif stage.tag == 'Test':
            stages[Module.TEST_STAGE] = create_test_stage(stage, module_name)
            i = Module.TEST_STAGE
            print('Created Test stage for ' + module_name)
        elif stage.tag == 'Commit':
            stages[Module.COMMIT_STAGE] = create_commit_stage(stage, module_name)
            i = Module.COMMIT_STAGE
            loggers.append(stages[Module.COMMIT_STAGE].get_vcs_obj().get_logger())
            print('Created Commit stage for ' + module_name)
        elif stage.tag == 'Notification':
            continue
        else:
            print("Unrecognized " + stage.tag + ' stage!')
            continue

        logger = stages[i].get_logger()
        if logger is not None:
            loggers.append(logger)

    notification_stage = stages_root.find('Notification')
    if notification_stage is not None:
        stages[Module.NOTIFICATION_STAGE] = create_notification_stage(notification_stage, loggers)
        print('Created Notification stage for ' + module_name)

    outputs_list = []
    outputs = module_root.find('Outputs')
    if outputs is not None:
        print('Read outputs for ' + module_name)
        outputs_list = read_outputs(outputs)

    dependencies_list = []
    dependencies = module_root.find('Dependencies')
    if dependencies is not None:
        print('Read dependencies for ' + module_name)
        dependencies_list = read_dependencies(dependencies)

    print('\n')

    return Module(module_name, dependencies_list, outputs_list, stages)


def main(input_file):
    modules = []  # array of Module

    tree = ET.parse(input_file)
    root = tree.getroot()

    for module in root.iter('Module'):
        modules.append(create_module(module))

    topological_sorted_modules = Module.topological_sort(modules)
    if topological_sorted_modules is not None:
        for module in topological_sorted_modules:
            if not module.execute_stages():
                print('Error is occurred during stages execution! See log for more information.')
                exit(-1)
        print('Stages have executed successfully.')
    else:
        print("It seems that modules have cycle dependencies! Check the input file.")
        exit(-1)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python3 simple-test-tool.py [path_to_config]')
        exit(-1)
    os.chdir(os.path.dirname(sys.argv[1]))

    main(sys.argv[1])

    exit(0)
