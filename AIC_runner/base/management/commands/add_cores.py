from django.core.management.base import BaseCommand


class Command(BaseCommand):

    can_import_settings = True

    def add_arguments(self, parser):
        parser.add_argument("redis_db", type=int)
        parser.add_argument("cores", nargs='*', type=int)

    def handle(self, *args, **options):
        from django.conf import settings
        from docker_sandboxer.scheduler import CPUScheduler
        cpu_scheduler = CPUScheduler(
                settings.CPU_MANAGER_REDIS_HOST,
                settings.CPU_MANAGER_REDIS_PORT,
                options["redis_db"]
        )
        cpu_scheduler.add_ases_available_cpus(options["cores"])