import argparse
import timeago

def args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', type=str, help='Config file path')
    parser.add_argument('-n', '--nAlarm', type=int, help='Number of Alarms to generate')

    opts = parser.parse_args()

    return {
        'config_file': opts.config,
        'number_alarms' : opts.nAlarm
    }
