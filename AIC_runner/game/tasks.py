import os
import random
import shutil
import zipfile
from string import ascii_lowercase as lowers

from django.core.files.base import ContentFile

from docker import Client

from celery import shared_task

from game.models import Game


@shared_task(bind=True, queue='game_queue')
def run_game(self, game_id):
    game = Game.objects.get(id=game_id)

    competition_dir = '/competitions/' + game.competition.id
    game_dir = competition_dir + '/' + game.id

    # prepare yaml context
    game_clients = [
        {
            'id': submit.id,
            'name': submit.team.name,
            'lang': submit.pl,
            'token': generate_random_token(),
            'root': game_dir + '/clients/' + submit.id,
            'compile_result': submit.compile_result,
            'container': get_image_id(submit.lang.execute_container),
        }
        for submit in game.players.all()
    ]
    game_ui = {
        'port': 7000,
        'token': generate_random_token(),
    }
    game_server = {
        'client_port': 7099,
        'root': game_dir + '/server' + game.competition.server_version,
        'compiled_code': game.competition.server.compiled_code,
        'container': game.competition.server.execute_container,
    }
    game_additional_containers = {
        container.tag: get_image_id(container) for container in game.competition.additional_containers.all()
    }
    game_context = {
        'server': game_server,
        'clients': game_clients,
        'ui': game_ui,
        'additional_containers': game_additional_containers,
    }

    # prepare game files
    make_dir(game_dir)

    # extract server (check if server exists)
    if not os.path.exists(game_server['root']):
        extract_zip(game_server['code'], game_server['root'])

    # extract compile result
    for client in game_clients:
        extract_zip(client['code'], client['root'])


def generate_random_token(length=32):
    return ''.join([lowers[random.randrange(0, len(lowers))] for i in range(length)])


def make_dir(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)


def extract_zip(file_field, dst):
    make_dir(dst)
    with file_field.open('r') as fs:
        zf = zipfile.ZipFile(fs)
        zf.extractall(dst)


def get_image_id(container):
    image_name = 'container-%d:v%d' % (container.id, container.version)

    # create a client to communicate with docker
    client = Client(base_url='unix://var/run/docker.sock')

    # check if already built
    images = client.images(name=image_name)
    if images:
        return images[0]['Id']

    # build the docker file
    with container.dockerfile.open('rb') as fs:
        response = client.build(fileobj=fs, rm=True, tag=image_name)
        container.build_log.save('%s-build.log' % image_name, ContentFile(response))

    images = client.images(name=image_name)
    if images:
        return images[0]['Id']
    else:
        return None  # todo: game could not be started, should restart
