def job_runner(job_queue):
    while 1:
        try:
            job = job_queue.recv()
            
            print("Running job: %s" % job)

        except:
            print("An error occured while running a job.")