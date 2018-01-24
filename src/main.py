import sys
import os
import argparse
import logging
from tqdm import tqdm  # show progress bar
import json
import time
from random import randint
from uiautomator import Device
from xml.etree import cElementTree as ET
from dataprocessor import DataProcessor
from executor import Executor
from observer.guiobserver import GuiObserver
from modelbuilder import ModelBuilder
from selector import Selector
from subprocess import check_output
from utils import *
from qlearning.environment import Environment
import operator
import random
import datetime

logger = logging.getLogger(__name__)
current_package = "org.liberty.android.fantastischmemo"
# current_package = "com.irahul.worldclock"
# current_package = "net.fercanet.LNM"
output_path = "../output/{}/".format(current_package)
input_path = "../input/{}/".format(current_package)

hierarchy_output_path = "{}{}".format(output_path, 'hierarchy.xml')

recorda_output_path = "{}recorda/".format(output_path)
recorda_input_path = "{}recorda/{}".format(input_path, 'reany.json')

kenlm_input_path = "{}kenlm/{}".format(input_path, 'h_PKDexActzzzzz.arpa')
alpha = 1.
gamma = 0.9
epsilon_greedy = 0.8

def is_out_of_app(activity):
    """Check is out of app."""
    print 'activity: ', activity
    if activity == 'com.android.systemui.recents.RecentsActivity' or (activity == 'com.android.browser') or (activity == 'com.android.browser.BrowserActivity') or ('com.google.android' in activity) or ('com.android' in activity):

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
                  '{}/{}.EmmaInstrument.EmmaInstrumentation'.format(current_package, current_package)])


def jump_to_activity(activity):
    output = check_output(['adb', 'shell', 'am', 'start', '-n', '{}/.{}'.format(current_package, activity)])
    print (output)


def random_test(device, executor, observer, times=1):
    """Test the app randomly."""
    selector = Selector(kenlm_input_path)
    for i in range(times):
        # dump the window hierarchy and save to local file "hierarchy.xml"
        device.dump(hierarchy_output_path)

        clickableList = observer.get_all_actionable_events(hierarchy_output_path)

        # TODO: handle backbutton and nullList.
        c = randint(0, 5)
        if c == 0:
            executor.perform_back()
        else:
            if len(clickableList) == 0:
                x = randint(0, 540)
                y = randint(0, 540)  # TODO why 540 ?
                executor.perform_random_click(x, y)
            else:
                event = selector.get_random_event(clickableList)
                executor.perform_action(event)


def random_strategy(device, step=5, episode=10):
    env = Environment(alpha, gamma)
    observer = GuiObserver(device)
    executor = Executor(device)
    for j in tqdm(range(episode)):
        print("------------Episode {}---------------".format(j))
        for i in tqdm(range(step)):
            time.sleep(0.5)
            observer.dump_gui(hierarchy_output_path)
            activity = observer.get_current_activity(current_package)
            clickable_list = observer.get_all_actionable_events(hierarchy_output_path)

            if is_launcher(activity):
                back_to_app()
                continue
            elif is_out_of_app(activity):
                executor.perform_back()
                continue

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
            env.set_next_state(observer.get_current_activity(current_package),
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


def epsilon_greedy_strategy(device, epsilon, step=5, episode=1000):

    print(datetime.datetime.now().isoformat())

    env = Environment(alpha, gamma)
    observer = GuiObserver(device)
    executor = Executor(device)
    for j in tqdm(range(episode)):
        print("------------Episode {}---------------".format(j))
        for i in tqdm(range(step)):
            time.sleep(0.5)
            observer.dump_gui(hierarchy_output_path)
            activity = observer.get_current_activity(current_package)
            clickable_list = observer.get_all_actionable_events(hierarchy_output_path)

            if is_launcher(activity):
                back_to_app()
                continue
            elif is_out_of_app(activity):
                executor.perform_back()
                continue
            else:
                env.set_current_state(activity, clickable_list)

                if len(env.get_available_action()):
                    r = random.uniform(0.0, 1.0)
                    if r > epsilon:
                        env.current_action = random.choice(env.get_available_action().keys())
                    else:
                        max_q_key = max(env.q_value.iteritems(), key=operator.itemgetter(1))[0]
                        hash_action = max_q_key.split("||")[1]
                        env.current_action = hash_action

                if not env.current_action:
                    x = randint(0, 540)
                    y = randint(0, 540)
                    executor.perform_random_click(x, y)
                else:
                    # print("Perform {}".format(env.current_action.attrib))
                    executor.perform_action(env.actions[env.current_action][1])

                env.set_next_state(observer.get_current_activity(current_package),
                                   observer.get_all_actionable_events(hierarchy_output_path))
                # print("{} ------> {}".format(env.current_state.activity, env.next_state.activity))
                env.add_reward(env.current_state, env.next_state)
                env.update_q()
        """ 
        End of and episode, start from a random state from the list of states that have been explored
        """
        random_state = env.get_random_state()
        jump_to_activity(random_state.activity)
    print("#############STATE###########")
    for s in env.states.values():
        print s
    print("QQQQQQQQQQQQQQQQQQQQQQQQQ")
    print(env.q_value.values())

    print(datetime.datetime.now().isoformat())



def random_test_with_model(device, times=1):
    """Random test with model."""

    """ 
    Step 1: Process usage logs from Recorda 
    Squash all scroll event then group by activity then save to file.
    Each file has all the events of one activity
    """
    dp = DataProcessor(recorda_output_path)
    print(recorda_output_path)
    with open(recorda_input_path, 'r') as data_file:
        events = json.load(data_file)
    dp.process_all_events(events)

    prev_events_str = ""

    observer = GuiObserver(device)
    executor = Executor(device)

    for i in tqdm(range(times)):
        time.sleep(0.5)
        """
        Step 2: Observe the current activities and dump GUI tree to xml file
        Then get the list of all actionable events, get current activity
        """
        # TODO Does not need to write to a file to process this. Store as local variable
        observer.dump_gui(hierarchy_output_path)
        # print '----gui dumped----'

        clickable_list = observer.get_all_actionable_events(hierarchy_output_path)

        current_activity = observer.get_current_activity(current_package)
        print ('current_activity:', current_activity)

        if is_launcher(current_activity):
            back_to_app()
            continue
        elif is_out_of_app(current_activity):
            executor.perform_back()
            continue

        """
        Step 3: Get activity logs from Recorda or previous model builder and build a new model upon it
        """

        if os.path.isfile(recorda_input_path + current_package + '.' + current_activity + '.json'):
            with open(recorda_input_path + current_package + '.' + current_activity + '.json') as df:
                main_events = json.load(df)
            mb = ModelBuilder(main_events)
            if not os.path.isfile(output_path + current_activity + ".arpa"):
                mb.create_klm_model_from_events(main_events, current_activity)
            try:
                selector = Selector(output_path + current_activity + ".arpa")
            except Exception as e:
                print (e)
                random_test(device, executor, observer)
                continue
            onegram_hash_events = mb.h_events

            # Hashed event and event.
            h_selected_event, selected_event = selector.get_random_event_with_prob(
                clickable_list, onegram_hash_events, prev_events_str)

            print 'SELECT', selected_event
            if type(selected_event) != dict:
                continue
            if selected_event['resource-id'] == 'typeback':
                executor.perform_back()
                append_string_to_file('BACK')
                continue
            # Find event from gui
            selected = observer.find_gui_from_event(
                hierarchy_output_path, selector.hash_events[h_selected_event])

            print 'select this one', selected.attrib, selector.hash_events[h_selected_event]
            if selected is not None:
                executor.perform_action_with_hash(selected, selector.hash_events[h_selected_event])
                prev_events_str += ' ' + h_selected_event
                prev_events_str = prev_events_str.strip()
                xmlstr = ET.tostring(selected, encoding='utf8', method='xml')
                append_string_to_file(xmlstr)
            # print '1g hash', onegram_hash_events, h_selected_event
        else:
            random_test(device, executor, observer)

    print 'FINISHED'


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
    args = parser.parse_args()
    if not is_device_available(args.device):
        logger.error('Please connect device', args.device)
        sys.exit()

    d = Device(args.device)
    if not os.path.isdir(output_path):
        os.mkdir(output_path)
    if not os.path.isdir(input_path):
        os.mkdir(input_path)
    # random_strategy(d)
    epsilon_greedy_strategy(d, epsilon_greedy)
    # random_test(d, executor, 10)
    # random_test_with_model(d, times=50)
    logger.info('----DONE----')