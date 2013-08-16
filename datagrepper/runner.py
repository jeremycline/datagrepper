import fedmsg
import fedmsg.consumers
from lockfile import LockFile

from datagrepper.app import app, db
from datagrepper.dataquery import DataQuery
import datagrepper.models as dgrepm
from datagrepper.models import Job


class DatagrepperRunnerConsumer(fedmsg.consumers.FedmsgConsumer):
    topic = 'org.fedoraproject.dev.datagrepper.job.new'
    config_key = 'fedmsg.consumers.datagrepper-runner.enabled'

    def __init__(self, *args, **kwargs):
        super(DatagrepperRunnerConsumer, self).__init__(*args, **kwargs)

    def consume(self, msg):
        print "****** STARTING CONSUME"
        # ignore the message, we do what we want
        lock = LockFile(app.config['RUNNER_LOCKFILE'])
        with lock:
            # get list of open jobs
            while True:
                jobs = Job.query.filter_by(status=dgrepm.STATUS_FREE)
                if jobs.count() == 0:
                    break
                for job in jobs:
                    # run query on jobs
                    dq = DataQuery.from_database(job)
                    job.set_status(dgrepm.STATUS_OPEN)
                    job.filename = dq.run_query(
                        'datagrepper_{0}'.format(job.id))
                    job.set_status(dgrepm.STATUS_DONE)
        print "****** FINISHING CONSUME"
