from celery import shared_task
from .models import Submit
from docker_sandboxer.sandboxer import Parser, Sandbox
from docker_sandboxer.scheduler import CPUScheduler
from django.core.files import File

from django.conf import settings
import os
import json


@shared_task(bind=True, queue='compile_queue')
def compile_code(self, submit_id):
    submit = Submit.objects.get(pk=submit_id)
    submit.status = 1
    submit.save()

    container = submit.lang.compile_container
    cpu_scheduler = CPUScheduler(db=settings.CPU_MANAGER_REDIS_CODE_COMPILER_DB)
    parser = Parser(cpu_scheduler, settings.COMPILE_DOCKER_YML_ROOT, settings.COMPILE_DOCKER_YML_LOG_ROOT)
    
    # make sure submitted code is synced
    try:
        submit.code.open()
    except IOError as exc:
        raise self.retry(countdown=settings.FILE_SYNC_DELAY_SECONDS,
                         max_retries=settings.FILE_SYNC_DELAY_MAX_RETRIES)
    submit_code = os.path.join(settings.MEDIA_ROOT, str(submit.code))
    submit.code.close()

    compile_context = {
        'code_image': container.get_image_id(),
        'code_zip': submit_code,
        'code_log': submit_code + '_log',
        'code_compile': submit_code + '_compiled',
        'sandboxer': container.get_sandboxer(),
    }

    def set_submit_compiling():
        submit.status = 2
        submit.save()

    try:
        parser.create_yml_and_run(str(submit_id), "compile.yml", compile_context, timeout=submit.team.competition.compile_time_limit, callback_before_run=set_submit_compiling)

        with open(compile_context['code_log'] + '/status.log') as data_file:
            data = json.load(data_file)

        print('errors: %s' % str(data['errors']))
        submit.status = 4 if data['errors'] else 3
        if data['errors']:
            error = 'Error at stage %d of compile:\n' % data['stage']
            error += '\n'.join([str(err) for err in data['errors']])
        else:
            error = 'OK'
            compile_code_name = submit_code + '_compiled' + '/compiled.zip'
            submit.team.final_submission = submit
            submit.team.save()
            with open(compile_code_name, 'rb') as compile_code_file:
                submit.compiled_code.save(str(submit.id) + '_compiled.zip', File(compile_code_file), save=True)
            print(submit.compiled_code)
        submit.compile_log_file = error[:1000]
    except TimeoutError:
        submit.status = 4
        submit.compile_log_file = 'Compile time limit exceeded.'
        data = 'Compile time limit exceeded.'

    submit.save()
    print("Compile end %s" % data)

