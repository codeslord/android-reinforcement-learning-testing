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
from qlearning.agent import Agent

from utils import *
import pprint
pp = pprint.PrettyPrinter(indent=4)
logging.basicConfig(filename='all.log', level=logging.DEBUG)
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


APP = {"any": {"current_package": "org.liberty.android.fantastischmemo",
               "recorda_file": "any_recorda.json"},
       "wei": {"current_package": "es.senselesssolutions.gpl.weightchart",
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
    logger.info('backtoapp')
    check_output(['adb', 'shell', 'am', 'instrument',
                 '-e', 'coverage', 'true',
                  '{}/{}.EmmaInstrument.EmmaInstrumentation'.format(package, package)])


def jump_to_activity(activity):
    output = check_output(['adb', 'shell', 'am', 'start', '-n', '{}/.{}'.format(package, activity)])
    print (output)
    return output


def epsilon_greedy_strategy(device, package, step, episode, epsilon=epsilon_default ,recorda_input_path=None, recorda_output_path=None):
    logger.info(datetime.datetime.now().isoformat())
    if recorda_input_path and recorda_output_path:
        dp = DataProcessor(recorda_output_path)
        with open(recorda_input_path, 'r') as data_file:
            events = json.load(data_file)
        dp.process_all_events(events)
        agent = Agent(alpha, gamma, recorda_path=recorda_output_path)
    else:
        agent = Agent(alpha, gamma)
    observer = GuiObserver(device)
    executor = Executor(device)
    for j in tqdm(range(episode)):
        logger.info("------------Episode {}---------------".format(j))
        for i in tqdm(range(step)):
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
                agent.set_current_state(activity, clickable_list)

                if len(agent.get_available_action()) > 0:
                    r = random.uniform(0.0, 1.0)
                    if r < epsilon:
                        agent.current_action = random.choice(agent.get_available_action().keys())
                        logger.info('Select randomly')
                    else:
                        max_q_key = max(agent.current_state.q_value.iteritems(), key=operator.itemgetter(1))[0]
                        if agent.current_state.q_value[max_q_key] != 0:
                            hash_action = max_q_key.split("||")[1]
                            agent.current_action = hash_action
                        logger.info("Select action with highest q value = {}".format(agent.current_state.q_value[max_q_key]))
                if not agent.current_action or agent.current_action == 'None':
                    x = randint(0, 540)
                    y = randint(0, 540)
                    executor.perform_random_click(x, y)
                else:
                    executor.perform_action(agent.actions[agent.current_action][1])
                time.sleep(0.2)
                observer.dump_gui()
                if not is_launcher(observer.get_current_activity(package)):
                    agent.set_next_state(observer.get_current_activity(package), observer.get_all_actionable_events())
                    agent.add_reward(agent.current_state, agent.next_state)
                    agent.add_reward_unvisited_action()
                    agent.update_q()
                else:
                    back_to_app()
                    continue
            agent.reset()
        """ 
        End of and episode, start from a random state from the list of states that have been explored
        """
        for i in range(len(agent.states)):
            random_state = agent.get_random_state()
            output = jump_to_activity(random_state.activity)
            if 'Error' not in output:
                break
    """ LOGGING """
    logger.info("#############STATE###########")
    for s in agent.states.values():
        logger.info(str(s))
    logger.info("#############Q value##########")
    logger.info(agent.q_value)

    logger.info(datetime.datetime.now().isoformat())


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
    parser.add_argument('step', help='Length of an episode')
    parser.add_argument('episode', help='Number of episode', type=int)
    args = parser.parse_args()
    if not is_device_available(args.device):
        logger.error('Please connect device', args.device)
        sys.exit()

    d = Device(args.device)

    if args.app not in APP:
        logger.error('Please choose an app and number of step and episode', args.device)
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

    epsilon_greedy_strategy(d, package, int(args.step), args.episode, recorda_input_path=recorda_input_path, recorda_output_path=recorda_output_path)

    logger.info('----DONE----')