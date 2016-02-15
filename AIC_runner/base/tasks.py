from celery import shared_task
from .models import Submit
from docker_sandboxer.sandboxer import Parser, Sandbox
from docker_sandboxer.scheduler import CPUScheduler
from django.conf import settings
import os
import json


@shared_task(bind=True, queue='compile_queue')
def compile_code(self, submit_id):
    submit = Submit.objects.get(pk=submit_id)
    submit.status = 1
    submit.save()

    container = submit.lang.compile_container

    sandbox = Sandbox()
    sandbox.update_limits(
        cpu=[int(core) for core in container.cores.split(',')],
        memory=container.memory,
        swap=container.swap,
    )

    cpu_scheduler = CPUScheduler(db=settings.CPU_MANAGER_REDIS_CODE_COMPILER_DB)
    parser = Parser(cpu_scheduler, settings.COMPILE_DOCKER_YML_ROOT, settings.COMPILE_DOCKER_YML_LOG_ROOT)

    submit_code = os.path.join(settings.MEDIA_ROOT, str(submit.code))
    compile_context = {
        'code_image': submit.lang.compile_container.get_image_id(),
        'code_zip': submit_code,
        'code_log': submit_code + '_log',
        'code_compile': submit_code + '_compiled',
    }

    parser.create_yml_and_run(str(submit_id), "compile.yml", compile_context)

    with open(compile_context['code_log'] + '/status.log') as data_file:
        data = json.load(data_file)

    submit.status = 2 if data['compile_success'] else 3
    submit.compile_log_file = '' if 'compile_error' not in data else data['compile_error']
    submit.compiled_code = compile_context['code_compile'] + '/compiled.zip'
    submit.save()
    print("Compile end %s" % data)

