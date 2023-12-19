from utility_functions import (
    get_job_list,
    txt_to_json
)


if __name__ == "__main__":
    job_list, job_dir = get_job_list()
    for i in range(len(job_list)):
        txt_to_json(job_dir, job_list[i], i)
