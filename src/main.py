import argparse
import cProfile
import logging
import sys
import datetime
from subprocess import check_output

from tqdm import tqdm  # show progress bar
from uiautomator import Device

from env.env import Environment
from qlearning.agent import Agent

log_file = "mytool.log"
# pp = pprint.PrettyPrinter(indent=4)
logging.basicConfig(filename=log_file, level=logging.DEBUG)
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
epsilon_default = [1.0, 0.6] # epsilon decrease from 1
epsilon_step = 100

def epsilon_greedy_strategy(device, package, step, episode, epsilon=epsilon_default, recorda=False):
    env = Environment(device, package, recorda)
    agent = Agent(alpha, gamma, epsilon)
    start = datetime.datetime.now()
    logger.info("Epsilon decrease from {} to {} with step {}".format(epsilon_default[0], epsilon_default[1], epsilon_step))
    logger.info("Step = {}, Ep = {}, Alpha = {}, Gamma = {}, Recorda = {}".format(step, episode, alpha, gamma, recorda))

    for j in range(episode):
        logger.info("Number of visited states: " + str(len(env.visited_states)))
        logger.info("------------Episode {}---------------".format(j))
        e = epsilon[0] - j*(epsilon[0]-epsilon[1])/float(epsilon_step)
        logger.info("Epsilon: {}".format(e))
        try:
            for i in range(step):
                if not env.current_state:
                    env.set_current_state()
                action = agent.select_next_action(env.current_state, e)
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
            random_state = env.get_random_state()
            env.jump_to_activity(random_state)
            # env.back_to_app()
        except Exception as e:
            print(str(e))

        if datetime.datetime.now() - start > datetime.timedelta(hours=1, minutes=5):
            logger.info("TIMEOUT 1h 5m")
            break

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
    # clear log
    with open(log_file, 'w'):
        pass

    if not is_device_available(args.device):
        print('Please connect device' + str(args.device))
        sys.exit()
    d = Device(args.device)
    package = args.package
    recorda = args.recorda



    print("USE RECORDA {}".format(recorda))
    epsilon_greedy_strategy(d, package, int(args.step), args.episode, recorda=recorda)
    # cProfile.run('epsilon_greedy_strategy(d, package, int(args.step), args.episode, recorda=recorda)', 'profile.tmp')

    logger.info('----DONE----')