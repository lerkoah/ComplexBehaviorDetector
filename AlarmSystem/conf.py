import json

def get_conf(file_path):
    conf = {
        'elasticsearch': {
            'hosts': ['localhost:9200']
        },
        'rabbitmq': {
            'hosts': ['localhost:5672']
        },
        'logstash': {
            'hosts': ['localhost:5003']
        }
    }

    if file_path is None:
        return conf

    with open(file_path) as f:
        raw = json.load(f)

        if 'elasticsearch' not in raw:
            raise ValueError('Config file must contain an elasticsearch field')

        if 'hosts' not in raw['elasticsearch']:
            raise ValueError('Config file must contain an elasticsearch.hosts field')

        if 'rabbitmq' not in raw:
            raise ValueError('Config file must contain an rabbitmq field')

        if 'hosts' not in raw['rabbitmq']:
            raise ValueError('Config file must contain an rabbitmq.hosts field')

        if 'logstash' not in raw:
            raise ValueError('Config file must contain an logstash field')

        if 'hosts' not in raw['logstash']:
            raise ValueError('Config file must contain an logstash.hosts field')

        conf['elasticsearch']['hosts'] = raw['elasticsearch']['hosts']
        conf['rabbitmq']['hosts'] = raw['rabbitmq']['hosts']
        conf['logstash']['hosts'] = raw['logstash']['hosts']


    return conf
