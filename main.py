import requests
import os
from collections import defaultdict
from itertools import count
from dotenv import load_dotenv

load_dotenv()
secret_key = os.getenv('SUPERJOB_TOKEN')

def vacancies_found(query):
    url = 'https://api.hh.ru/vacancies'
    params = {
            'area': 1,
            'text': query,
            'date_from': '2021-12-01',
            'date_to': '2021-12-12',
        }
    request = requests.get(url, params=params)
    vacancies_found = request.json()['found']
    return vacancies_found

def get_stat_to_most_popular_language():
    most_popular_language = ['javascript', 'java', 'python', 'ruby', 'php', 'c++', 'c#', 'go', 'objective-c', 'scala', 'swift']
    vacancies_stat = defaultdict(dict)

    for language in most_popular_language:
        query = f'Программист {language}'
        response = get_vacancies_from_hh(query)
        salaries = get_salary_from_hh(response)
        vacancies_stat[language]['vacancies_found'] = vacancies_found(query)
        vacancies_stat[language]['vacancies_processed'] = len(salaries)
        vacancies_stat[language]['average_salary'] = mean_predict_salary(predict_rub_salary(salaries))
    
    return vacancies_stat

def get_vacancies_from_hh(text):
    url = 'https://api.hh.ru/vacancies'
    vacancies = []
    for page in count(0):
        params = {
            'area': 1,
            'text': text,
            'page': page,
            'date_from': '2021-12-01',
            'date_to': '2021-12-12',
        }

        request = requests.get(url, params=params)
        responce = request.json()
        for vacancie in responce['items']:
            vacancies.append(vacancie)
    
        last_page = responce['pages']
        ### выдавало ошибку bad request, мол я не могу получать более 2000 объектов
        if page >= last_page or page == 99:
            break
    
    return vacancies


def get_salary_from_hh(vacancies):
    salaries = []

    for vacancie in vacancies:
        salary = vacancie['salary']
        if salary is not None:
            salaries.append(salary)
        
    return salaries


def predict_rub_salary(salaries):
    predict_salaries = []
    for salary in salaries:
        if salary['currency'] != 'RUR':
            predict_salary = None

        elif salary['from'] is not None and salary['to'] is not None:
            predict_salary = (salary['from'] + salary['to']) / 2

        elif salary['from'] is not None:
            predict_salary = salary['from'] * 1.2
        
        elif salary['to'] is not None:
            predict_salary = salary['to'] * 0.8
        
        predict_salaries.append(predict_salary)
    
    return predict_salaries
    

def mean_predict_salary(salaries):
    if salaries:
        summ_salaries = sum([salary for salary in salaries if salary is not None])
        len_salaries = len([salary for salary in salaries if salary is not None])
        
        mean_salary = int(summ_salaries / len_salaries)

        return mean_salary

def get_vacancies_from_superJob(secret_key, keywords=''):
    url = 'https://api.superjob.ru/2.0/vacancies/'
    vacancies = []
    for page in range(4):
        params = {
            'town': 4,
            'catalogues': 48,
            'page': page,
            'count': 100,
            'keywords': ['keys', keywords]
        }
        data = {
            'X-Api-App-Id': secret_key,
        }
        response = requests.get(url, params=params, headers=data)
        response = response.json()['objects']
        vacancies.append(response)
        
    return vacancies
    # for profession in response:
    #     print(profession['profession'], profession['town']['title'], predict_rub_salary_for_superJob(profession), sep=', ')

def predict_rub_salary_for_superJob(vacancies):
    predict_salary = 0

    if vacancies['payment_from'] == 0 and vacancies['payment_to'] == 0:
        predict_salary = None
    elif vacancies['payment_from'] != 0 and vacancies['payment_to'] != 0:
        predict_salary = (vacancies['payment_from'] + vacancies['payment_to']) / 2
    elif vacancies['payment_from'] != 0:
        predict_salary = vacancies['payment_from'] * 1.2    
    elif vacancies['payment_to'] != 0:
        predict_salary = vacancies['payment_to'] * 0.8
    else:
        predict_salary = None

    return predict_salary


def get_stat_to_most_popular_language_superJob():
    most_popular_language = ['javascript', 'java', 'python', 'ruby', 'php', 'c++', 'c#', 'go', 'objective-c', 'scala', 'swift']
    vacancies_stat = defaultdict(dict)

    for language in most_popular_language:
        keywords = f'Программист {language}'
        response = get_vacancies_from_superJob(secret_key, keywords=keywords)
        salaries = []
        vacancies_stat[language]['vacancies_found'] = 0
        for item in response:
            for profession in item:
                salary = predict_rub_salary_for_superJob(profession)
                if salary is not None:
                    salaries.append(salary)
                vacancies_stat[language]['vacancies_found'] = len(item)
                vacancies_stat[language]['vacancies_processed'] = len(salaries)
                vacancies_stat[language]['average_salary'] = mean_predict_salary(salaries)
        
    return vacancies_stat

def main():
    print(get_stat_to_most_popular_language_superJob())

if __name__ == "__main__":
    main()