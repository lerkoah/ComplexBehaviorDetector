import argparse
import timeago

def args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', type=str, help='Config file path')

    opts = parser.parse_args()

    return {
        'from': from_time,
        'to': to_time,
        'query': opts.query,
        'config_file': opts.config,
    }
