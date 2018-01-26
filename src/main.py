import argparse
import datetime
import logging
import operator
import os
import random
import sys
import time
from random import randint
from subprocess import check_output

from tqdm import tqdm  # show progress bar
from uiautomator import Device

from dataprocessor import DataProcessor
from executor import Executor
from observer.guiobserver import GuiObserver
from qlearning.environment import Environment

from utils import *
import pprint
pp = pprint.PrettyPrinter(indent=4)
logger = logging.getLogger(__name__)

APP = {"any": {"current_package": "org.liberty.android.fantastischmemo",
               "recorda_file": "any_recorda.json"},
       "wei": {"current_package": "oes.senselesssolutions.gpl.weightchart",
               "recorda_file": "wei_recorda.json"},
       "note": {"current_package": "net.fercanet.LNM",
               "recorda_file": "any_recorda.json"},
       "clock": {"current_package": "com.irahul.worldclock",
               "recorda_file": "clock_recorda.json"},
       }

alpha = 1.
gamma = 0.9
epsilon_default = 0.8


def is_out_of_app(activity):
    """Check is out of app."""
    if ('com.google.android' in activity) or ('com.android' in activity) or 'mCurrentFocus=null' in activity:

        append_string_to_file("LEAVE APP!")
        return True
    else:
        return False


def is_launcher(activity):
    """Check is out of app."""
    # print 'activity: ', activity
    if activity == 'com.android.launcher2.Launcher' or activity == "com.jiubang.golauncher.GOLauncher" or activity == 'com.android.launcher3.Launcher':
        append_string_to_file("LEAVE APP LAUNCHER!")
        return True
    else:
        return False


def back_to_app():
    """Go back."""
    print 'backtoapp'
    check_output(['adb', 'shell', 'am', 'instrument',
                 '-e', 'coverage', 'true',
                  '{}/{}.EmmaInstrument.EmmaInstrumentation'.format(package, package)])


def jump_to_activity(activity):
    output = check_output(['adb', 'shell', 'am', 'start', '-n', '{}/.{}'.format(package, activity)])
    print (output)
    return output


def random_strategy(device, step=5, episode=10):
    env = Environment(alpha, gamma)
    observer = GuiObserver(device)
    executor = Executor(device)
    for j in tqdm(range(episode)):
        print("------------Episode {}---------------".format(j))
        for i in tqdm(range(step)):
            time.sleep(0.5)
            observer.dump_gui(hierarchy_output_path)
            activity = observer.get_current_activity(package)
            clickable_list = observer.get_all_actionable_events(hierarchy_output_path)

            if is_launcher(activity) or 'Application Error' in activity:
                back_to_app()
                continue
            elif is_out_of_app(activity):
                executor.perform_back()
                continue
            else:

                env.set_current_state(activity, clickable_list)
                if len(env.get_available_action()):
                    env.current_action = random.choice(env.get_available_action())

                if not env.current_action:
                    x = randint(0, 540)
                    y = randint(0, 540)
                    executor.perform_random_click(x, y)
                else:
                    # print("Perform {}".format(env.current_action.attrib))
                    executor.perform_action(env.current_action)

                time.sleep(0.5)
                env.set_next_state(observer.get_current_activity(package),
                                   observer.get_all_actionable_events(hierarchy_output_path))
                print("{} ------> {}".format(env.current_state.activity, env.next_state.activity))
                env.add_reward(env.current_state, env.next_state)
                env.update_q()
        """ 
        End of and episode, start from a random state from the list of states that have been explored
        """
        random_state = env.get_random_state()
        jump_to_activity(random_state.activity)
    print("#############STATE###########")
    print(env.states)
    print("QQQQQQQQQQQQQQQQQQQQQQQQQ")
    print(env.q_value)


def epsilon_greedy_strategy(device, package, step, episode, epsilon=epsilon_default ,recorda_input_path=None, recorda_output_path=None):

    print(datetime.datetime.now().isoformat())
    if recorda_input_path and recorda_output_path:
        dp = DataProcessor(recorda_output_path)
        with open(recorda_input_path, 'r') as data_file:
            events = json.load(data_file)
        dp.process_all_events(events)
        env = Environment(alpha, gamma, recorda_path=recorda_output_path)
    else:
        env = Environment(alpha, gamma)
    observer = GuiObserver(device)
    executor = Executor(device)
    for j in tqdm(range(episode)):
        print("------------Episode {}---------------".format(j))
        for i in range(step):
            observer.dump_gui()
            activity = observer.get_current_activity(package)
            clickable_list = observer.get_all_actionable_events()

            if is_launcher(activity) or 'Application Error' in activity:
                back_to_app()
                continue
            elif is_out_of_app(activity):
                executor.perform_back()
                continue
            else:
                env.set_current_state(activity, clickable_list)

                if len(env.get_available_action()) > 0:
                    r = random.uniform(0.0, 1.0)
                    if r < epsilon:
                        env.current_action = random.choice(env.get_available_action().keys())
                        print("< epsilon Select randomly from available action")
                    else:
                        max_q_key = max(env.current_state.q_value.iteritems(), key=operator.itemgetter(1))[0]
                        if env.current_state.q_value[max_q_key] != 0:
                            hash_action = max_q_key.split("||")[1]
                            env.current_action = hash_action
                        print("> epsilon Select action with highest q value = {}".format(env.current_state.q_value[max_q_key]))
                if not env.current_action or env.current_action == 'None':
                    x = randint(0, 540)
                    y = randint(0, 540)
                    executor.perform_random_click(x, y)
                else:
                    executor.perform_action(env.actions[env.current_action][1])
                time.sleep(0.5)
                observer.dump_gui()
                if not is_launcher(observer.get_current_activity(package)):
                    env.set_next_state(observer.get_current_activity(package), observer.get_all_actionable_events())
                    env.add_reward(env.current_state, env.next_state)
                    env.update_q()
                else:
                    back_to_app()
                    continue
            env.reset()
        """ 
        End of and episode, start from a random state from the list of states that have been explored
        """
        for i in range(len(env.states)):
            random_state = env.get_random_state()
            output = jump_to_activity(random_state.activity)
            if 'Error' not in output:
                break
    print("#############STATE###########")
    for s in env.states.values():
        pp.pprint(s)
    print("#############Q value##########")
    pp.pprint(env.q_value)

    print(datetime.datetime.now().isoformat())


def is_device_available(device_num):
    """Check whether device is available in adb devices."""
    output = check_output(['adb', 'devices'])
    if device_num in output:
        return True
    else:
        return False


if __name__ == "__main__":
    """Main program."""
    # d = Device('08ee2d08')  # nexus tablet
    # device_number_str = 'emulator-5554'  # nexus api19
    # device_number_str = 'emulator-5554'
    # device_number_str = 'BH904F6J5P'  # xperia

    parser = argparse.ArgumentParser()
    parser.add_argument('device', help='device name')
    parser.add_argument('app', help='choose app name among : note, any, clock, wei')
    args = parser.parse_args()
    if not is_device_available(args.device):
        logger.error('Please connect device', args.device)
        sys.exit()

    d = Device(args.device)

    if args.app not in APP:
        logger.error('Please choose an app', args.device)
        sys.exit()

    package = APP[args.app]['current_package']

    output_path = "../output/{}/".format(package)
    input_path = "../input/{}/".format(package)

    recorda_output_path = "{}recorda/".format(output_path)
    recorda_input_path = "{}recorda/{}".format(input_path, APP[args.app]['recorda_file'])

    if not os.path.isdir(output_path):
        os.mkdir(output_path)
    if not os.path.isdir(input_path):
        os.mkdir(input_path)

    epsilon_greedy_strategy(d, package, 100, 30, recorda_input_path=recorda_input_path, recorda_output_path=recorda_output_path)

    logger.info('----DONE----')