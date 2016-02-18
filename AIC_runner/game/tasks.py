import os
import json

from celery import shared_task
from django.core.files import File
from docker_sandboxer.sandboxer import Parser
from docker_sandboxer.scheduler import CPUScheduler
from pip._vendor.distlib._backport import shutil
from AIC_runner.settings import GAMES_ROOT
from django.conf import settings

from game.models import Game, GameTeamSubmit
from game.utils import make_dir, generate_random_token


@shared_task(bind=True, queue='game_queue')
def run_game(self, game_id):
    game = Game.objects.get(id=game_id)

    competition_dir = os.path.join(GAMES_ROOT, 'competitions', str(game.competition.id))
    game_dir = os.path.join(competition_dir, str(game.id))
    log_dir = os.path.join(game_dir, 'logs')

    # yml context
    print('preparing yml context')
    context = {
        'server': {
            'image_id': game.competition.server.get_image_id(),
            'sandboxer': game.competition.server.get_sandboxer(),
        },
        'logger': {
            'image_id': game.competition.logger.get_image_id(),
            'sandboxer': game.competition.logger.get_sandboxer(),
            'token': generate_random_token(),
            'log_root': log_dir,
            'log_file': os.path.join(log_dir, 'game.log'),
            'scores_file': os.path.join(log_dir, 'game.scr')
        },
        'clients': [
            {
                'image_id': submit.lang.execute_container.get_image_id(),
                'sandboxer': submit.lang.execute_container.get_sandboxer(),
                'name': submit.team.name,
                'token': generate_random_token(),
                'root': os.path.join(game_dir, 'clients', str(i)),
                'code': os.path.join(game_dir, 'clients', str(i), 'code.zip'),
                'submit': submit,
            }
            for i, submit in enumerate(game.players.all())
        ],
        'additional_containers': [
            {
                'image_id': container.get_image_id(),
                'sandboxer': container.get_sandboxer(),
                'tag': container.tag,
                'token': generate_random_token(),
            }
            for container in game.competition.additional_containers.all()
        ],
    }

    # prepare game files
    print('preparing game files')
    make_dir(game_dir)
    try:
        for client in context['clients']:
            code = client['submit'].compiled_code
            code.open()
            code.close()
            make_dir(client['root'])
            shutil.copyfile(code.path, client['code'])
    except IOError:
        raise self.retry(countdown=settings.FILE_SYNC_DELAY_SECONDS,
                         max_retries=settings.FILE_SYNC_DELAY_MAX_RETRIES)

    # run!
    print('creating cpu scheduler & parser')
    cpu_scheduler = CPUScheduler(db=settings.CPU_MANAGER_REDIS_GAME_RUNNER_DB)
    parser = Parser(cpu_scheduler, settings.GAME_DOCKER_COMPOSE_YML_ROOT, settings.GAME_DOCKER_COMPOSE_YML_LOG_ROOT)

    try:
        print('running')
        game.status = 2
        game.save()
        parser.create_yml_and_run(str(game.id), "run_game.yml", context, timeout=game.competition.execution_time_limit)
        print('game finished, saving the results')
    except TimeoutError:
        print('game timeout exceeded')

    try:
        with open(context['logger']['log_file']) as log_file:
            game.log_file.save('games/logs/game_%d.log' % game.id, File(log_file), save=True)
    except IOError:
        print('game log file does not exists.')

    try:
        with open(context['logger']['scores_file']) as scores_file:
            scores = json.load(scores_file)
            for i, client in enumerate(context['clients']):
                gts = GameTeamSubmit.objects.get(game=game, submit=client['submit'])
                gts.score = scores[i]
                gts.save()
    except IOError:
        print('game score file does not exists.')

    game.status = 3
    game.save()
    print('saving completed')
