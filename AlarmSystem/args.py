import argparse

def args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', type=str, help='Config file path')

    opts = parser.parse_args()

    return {
        'config_file': opts.config
    }
