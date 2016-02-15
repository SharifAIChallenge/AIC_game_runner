from celery import shared_task

from game.models import Game
from game.utils import generate_random_token, make_dir, extract_zip


@shared_task(bind=True, queue='game_queue')
def run_game(self, game_id):
    game = Game.objects.get(id=game_id)

    competition_dir = '/competitions/' + str(game.competition.id)
    game_dir = competition_dir + '/' + str(game.id)

    # yml context
    context = {
        container.tag: container.get_image_id()
        for container in game.competition.additional_containers.all()
    }
    context.update({
        'server': game.competition.server.get_image_id(),
        'clients': [
            {
                'id': submit.id,
                'name': submit.team.name,
                'lang': submit.pl,
                'token': generate_random_token(),
                'root': game_dir + '/clients/' + str(submit.id),
                'compile_code': submit.compile_code,
                'container': submit.lang.execute_container.get_image_id(),
            }
            for submit in game.players.all()
        ],
    })

    # prepare game files
    make_dir(game_dir)

    # extract compile result
    for client in context['clients']:
        extract_zip(client['compiled_code'], client['root'])
