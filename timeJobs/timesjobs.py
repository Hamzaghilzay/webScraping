from bs4 import BeautifulSoup
import requests

print('Put some skills you are unfamiliar with')
unfamiliar_skills = input('>')
print(f'Filtering out {unfamiliar_skills}')

url = 'https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&searchTextSrc=&searchTextText=&txtKeywords=python&txtLocation='
urlopn = requests.get(url).text # text attribute convert the response into a text
soup = BeautifulSoup(urlopn, 'lxml')
jobs = soup.find_all('li', class_='clearfix job-bx wht-shd-bx') # find_all searches for all li tag which contains the job detail

for job in jobs:
    job_title = job.header.h2.a.strong.string+job.header.h2.a.strong.next_sibling # end name is written as next sibling in the strong tag
    exp_req = job.ul.li.i.next_sibling # Experience was written in the next_sibling of i tag
    skills = job.find('span', class_='srp-skills').text.replace(' ', '').strip()
    posted = job.find('span', class_='sim-posted').span.text.strip()
    company_name = job.header.h3.string.strip()  # html child tags are continuously followed
    more_info = job.header.h2.a['href'] # Extracted the href attribute from a tag
    skills = job.find('span', class_='srp-skills').text.replace(' ', '').strip() #spaces inbetween the skills are striped
        
    if unfamiliar_skills in skills: # Filter the unfamilliar skills
        continue

    with open('time_jobs.txt', 'a')as f: # write to a new file
        f.write(f"Job Title: {job_title} \n")
        f.write(f"Experience Required: {exp_req} \n")
        f.write(f"Skills: {skills}\n")
        f.write(f"Published Date: {posted} \n")
        f.write(f"Company Name: {company_name} \n")
        f.write(f"More Info: {more_info}\n")
        f.write("\n") # add the new empty line after each iteration for a job
