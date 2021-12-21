import requests
import os
from collections import defaultdict
from itertools import count
from dotenv import load_dotenv
from terminaltables import AsciiTable

def get_stat_to_most_popular_language_hh():
    most_popular_language = ['javascript', 'java', 'python', 'ruby', 'php', 'c++', 'c#', 'go', 'objective-c', 'scala', 'swift']
    vacancies_stat = defaultdict(dict)

    for language in most_popular_language:
        query = f'Программист {language}'
        response = get_vacancies_from_hh(query)
        salaries = get_salary_from_hh(response[1])
        vacancies_stat[language]['vacancies_found'] = response[0]
        vacancies_stat[language]['vacancies_processed'] = len(salaries)
        vacancies_stat[language]['average_salary'] = mean_predict_salary(predict_rub_salary_hh(salaries))
    
    return vacancies_stat

def get_vacancies_from_hh(text):
    url = 'https://api.hh.ru/vacancies'
    vacancies = []
    for page in count(0):
        params = {
            'area': 1,
            'text': text,
            'page': page,
            'period': 30,
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        response = response.json()
        vacancies_found = response['found']
        for vacancie in response['items']:
            vacancies.append(vacancie)

        last_page = response['pages'] - 1
        if page == last_page:
            break
    
    return (vacancies_found, vacancies)


def get_salary_from_hh(vacancies):
    salaries = []

    for vacancie in vacancies:
        salary = vacancie['salary']
        if salary is not None:
            salaries.append(salary)
        
    return salaries


def predict_rub_salary_hh(salaries):
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
        response.raise_for_status()
        response = response.json()['objects']
        for vacancie in response: 
            vacancies.append(vacancie)
        
    return vacancies

def predict_rub_salary_for_superJob(vacancies):
    predict_salaries = []

    for vacancie in vacancies:
        if vacancie['payment_from'] == 0 and vacancie['payment_to'] == 0:
            predict_salaries.append(None)
        elif vacancie['payment_from'] != 0 and vacancie['payment_to'] != 0:
            predict_salary = (vacancie['payment_from'] + vacancie['payment_to']) / 2
            predict_salaries.append(predict_salary)
        elif vacancie['payment_from'] != 0:
            predict_salary = vacancie['payment_from'] * 1.2    
            predict_salaries.append(predict_salary)
        elif vacancie['payment_to'] != 0:
            predict_salary = vacancie['payment_to'] * 0.8
            predict_salaries.append(predict_salary)

    return predict_salaries


def vacancies_found_superJob(secret_key, keywords):
    url = 'https://api.superjob.ru/2.0/vacancies/'
    params = {
            'town': 4,
            'catalogues': 48,
            'keywords': ['keys', keywords]
        }
    data = {
            'X-Api-App-Id': secret_key,
        }
    
    request = requests.get(url, params=params, headers=data)
    vacancies_found = request.json()['total']
    return vacancies_found


def get_salary_from_superJob(vacancies):
    salaries = []

    for vacancie in vacancies:
        salary = vacancie['salary']
        if salary is not None:
            salaries.append(salary)
        
    return salaries


def get_stat_to_most_popular_language_superJob(secret_key):
    most_popular_language = ['javascript', 'java', 'python', 'ruby', 'php', 'c++', 'c#', 'go', 'objective-c', 'scala', 'swift']
    vacancies_stat = defaultdict(dict)

    for language in most_popular_language:
        keywords = f'Программист {language}'
        response = get_vacancies_from_superJob(secret_key, keywords=keywords)
        salary = predict_rub_salary_for_superJob(response)
        vacancies_stat[language]['vacancies_found'] = vacancies_found_superJob(keywords)
        vacancies_stat[language]['vacancies_processed'] = len(salary)
        vacancies_stat[language]['average_salary'] = mean_predict_salary(salary)
        
    return vacancies_stat

def print_stat_superJob(secret_key):
    title = 'SuperJob Moscow'
    statistics_superJob = get_stat_to_most_popular_language_superJob(secret_key)
    table_data = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    for language in statistics_superJob:
        row = []
        row.append(language)
        row.append(statistics_superJob[language]['vacancies_found'])
        row.append(statistics_superJob[language]['vacancies_processed'])
        row.append(statistics_superJob[language]['average_salary'])
        table_data.append(row)
    
    table = AsciiTable(table_data, title)
    print(table.table)

def print_stat_hh():
    title = 'HeadHunter Moscow'
    statistics_superJob = get_stat_to_most_popular_language_hh()
    table_data = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    for language in statistics_superJob:
        row = []
        row.append(language)
        row.append(statistics_superJob[language]['vacancies_found'])
        row.append(statistics_superJob[language]['vacancies_processed'])
        row.append(statistics_superJob[language]['average_salary'])
        table_data.append(row)
    
    table = AsciiTable(table_data, title)
    print(table.table)
    
    

    

def main():
    load_dotenv()
    secret_key = os.getenv('SUPERJOB_TOKEN')
    print(get_stat_to_most_popular_language_hh())

if __name__ == "__main__":
    main()