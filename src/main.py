import argparse
import cProfile
import logging
import pprint
import sys
from subprocess import check_output

from tqdm import tqdm  # show progress bar
from uiautomator import Device

from env.env import Environment
from qlearning.agent import Agent

# pp = pprint.PrettyPrinter(indent=4)
logging.basicConfig(filename='all.log', level=logging.DEBUG)
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


APP = {"any": "org.liberty.android.fantastischmemo",
       "wei": "es.senselesssolutions.gpl.weightchart",
       "note": "net.fercanet.LNM",
       "clock": "com.irahul.worldclock",
       "bat": "net.sf.andbatdog.batterydog",
       "stuff": "de.freewarepoint.whohasmystuff",
       "munch": "info.bpace.munchlife",
       }

alpha = 1.
gamma = 0.9
epsilon_default = 0.8

def epsilon_greedy_strategy(device, package, step, episode, epsilon=epsilon_default, recorda=False):
    env = Environment(device, package, recorda)
    agent = Agent(alpha, gamma, epsilon)

    for j in tqdm(range(episode)):
        logger.info("------------Episode {}---------------".format(j))
        try:
            for i in tqdm(range(step)):
                if not env.current_state:
                    env.set_current_state()
                action = agent.select_next_action(env.current_state)
                if env.transition_to_next_state(action):
                    # If next state is in the app
                    reward = env.get_reward(action)
                    agent.update_q(env.current_state, action, reward, env.next_state)
                    env.finish_transition()
                else:
                    agent.update_q(env.current_state, action, 0, None)

            """ 
            End of and episode, start from a random state from the list of states that have been explored
            """
            # random_state = env.get_random_state()
            # env.jump_to_activity(random_state[0])
            env.back_to_app()
        except Exception as e:
            print(str(e))

    """ LOGGING """
    logger.info("#############STATE###########")
    for s in env.visited_states:
        logger.info(str(s))
    logger.info("#############Q value##########")
    logger.info(agent.q_value)


def is_device_available(device_num):
    """Check whether device is available in adb devices."""
    output = check_output(['adb', 'devices'])
    if device_num in output:
        return True
    else:
        return False


if __name__ == "__main__":
    """Main program."""

    parser = argparse.ArgumentParser()
    parser.add_argument('device', help='device name')
    parser.add_argument('package', help='package name')
    parser.add_argument('step', help='Length of an episode')
    parser.add_argument('episode', help='Number of episode', type=int)
    parser.add_argument('--recorda', action='store_true', default=False)
    args = parser.parse_args()
    if not is_device_available(args.device):
        logger.error('Please connect device' + str(args.device))
        sys.exit()
    d = Device(args.device)
    package = args.package
    recorda = args.recorda

    # clear log
    with open('all.log', 'w'):
        pass

    print("USE RECORDA {}".format(recorda))
    epsilon_greedy_strategy(d, package, int(args.step), args.episode, recorda=recorda)
    # cProfile.run('epsilon_greedy_strategy(d, package, int(args.step), args.episode, recorda_input_path=recorda_input_path, recorda_output_path=recorda_output_path)', 'profile.tmp')

    logger.info('----DONE----')