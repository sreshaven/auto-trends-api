import jobs
import redis
import matplotlib.pyplot as plt
import numpy as np

@jobs.q.worker
def execute_job(jid):
    """
      Retrieve a job id from the task queue and execute the job.
      Monitors the job to completion and updates the database accordingly.
    """
    jobs.update_job_status(jid, 'in progress')
    # start the analysis
    if len(jobs.rd.keys()) == 0:
        return 'Auto Trends data not loaded in Redis yet\n'
    else:
        years = []
        co2 = {}
        cars_list = []
        start = int(jobs.get_job_start(jid))
        end = int(jobs.get_job_end(jid))
        for key in jobs.rd.keys():
            if jobs.rd.hget(key, 'Manufacturer') == 'All':
                cars_list.append(jobs.rd.hgetall(key))
        for car in cars_list:
            if car['Vehicle Type'] not in co2:
                co2[car['Vehicle Type']] = []
            if car['Model Year'].isdigit() and start <= int(car['Model Year']) <= end:
                if int(car['Model Year']) not in years:
                    years.append(int(car['Model Year']))
                co2[car['Vehicle Type']].append(float(car['Real-World CO2 (g/mi)']))
        for key in co2:
            plt.plot(years, co2[key], label = key)
        plt.title('CO2 Emissions by Vehicle Type from '+str(start)+'-'+str(end))
        plt.ylabel('Real-World CO2 (g/mi)')
        plt.xlabel('Year')
        plt.legend()
        plt.savefig('./output_img2.png')
        file_bytes = open('./output_img2.png', 'rb').read()
        # set the file bytes as a key in Redis
        jobs.rd2.set('plotimage2', file_bytes)
        jobs.update_job_image(jid, file_bytes)
    jobs.update_job_status(jid, 'complete')

if __name__ == '__main__':
    execute_job()
