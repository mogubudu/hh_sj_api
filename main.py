import requests
import os
from collections import defaultdict
from itertools import count
from dotenv import load_dotenv
from terminaltables import AsciiTable

def get_stat_to_most_popular_language_hh(languages=[]):
    vacancies_stat = dict()
    for language in languages:
        query = f'Программист {language}'
        response = get_vacancies_from_hh(query)
        salaries = get_salary_from_hh(response[1])
        vacancies_stat[language] = {
            'vacancies_found': response[0],
            'vacancies_processed': len(salaries),
            'average_salary': mean_predict_salary(predict_rub_salary_hh(salaries)),
        }
    
    return vacancies_stat

def get_vacancies_from_hh(text):
    url = 'https://api.hh.ru/vacancies'
    vacancies = []
    moscow_id = 1
    days = 30
    for page in count(0):
        params = {
            'area': moscow_id,
            'text': text,
            'page': page,
            'period': days,
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        response = response.json()
        vacancies_found = response['found']
        vacancies.extend(response['items'])

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

        elif salary['from'] and salary['to']:
            predict_salary = (salary['from'] + salary['to']) / 2

        elif salary['from']:
            predict_salary = salary['from'] * 1.2
        
        elif salary['to']:
            predict_salary = salary['to'] * 0.8
        
        predict_salaries.append(predict_salary)
    
    return predict_salaries
    

def mean_predict_salary(salaries):
    if salaries:
        salaries = [salary for salary in salaries if salary is not None]
        summ_salaries = sum(salaries)
        len_salaries = len(salaries)
        
        mean_salary = int(summ_salaries / len_salaries)

        return mean_salary

def get_vacancies_from_superjob(secret_key, keywords=''):
    url = 'https://api.superjob.ru/2.0/vacancies/'
    vacancies = []
    moscow_id = 4
    it_vacancies_catalog_id = 48
    for page in count(0):
        params = {
            'town': moscow_id,
            'catalogues': it_vacancies_catalog_id,
            'page': page,
            'keywords': ['keys', keywords]
        }
        data = {
            'X-Api-App-Id': secret_key,
        }
        response = requests.get(url, params=params, headers=data)
        response.raise_for_status()
        response = response.json()
        vacancies_found = response['total'] 
        vacancies.extend(response['objects'])
        if not response['more']:
            break
        
    return (vacancies_found, vacancies)

def predict_rub_salary_for_superjob(vacancies):
    predict_salaries = []

    for vacancie in vacancies:
        if not vacancie['payment_from'] and not vacancie['payment_to']:
            predict_salaries.append(None)
        elif vacancie['payment_from'] and vacancie['payment_to']:
            predict_salary = (vacancie['payment_from'] + vacancie['payment_to']) / 2
            predict_salaries.append(predict_salary)
        elif vacancie['payment_from']:
            predict_salary = vacancie['payment_from'] * 1.2    
            predict_salaries.append(predict_salary)
        elif vacancie['payment_to']:
            predict_salary = vacancie['payment_to'] * 0.8
            predict_salaries.append(predict_salary)

    return predict_salaries


def get_salary_from_superjob(vacancies):
    salaries = []

    for vacancie in vacancies:
        salary = vacancie['salary']
        if salary is not None:
            salaries.append(salary)
        
    return salaries


def get_stat_to_most_popular_language_superjob(secret_key, languages=[]):
    vacancies_stat = dict()

    for language in languages:
        keywords = f'Программист {language}'
        response = get_vacancies_from_superjob(secret_key, keywords=keywords)
        salary = predict_rub_salary_for_superjob(response[1])
        vacancies_stat[language] = {
            'vacancies_found': response[0],
            'vacancies_processed': len(salary),
            'average_salary': mean_predict_salary(salary),
        }
        
    return vacancies_stat

def print_stat_to_vacancies(statistics, title=''):
    table_data = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    for language in statistics:
        row = [language,
        statistics[language]['vacancies_found'],
        statistics[language]['vacancies_processed'],
        statistics[language]['average_salary']]
        
        table_data.append(row)
    
    table = AsciiTable(table_data, title)
    print(table.table)

    

def main():
    load_dotenv()
    secret_key = os.getenv('SUPERJOB_TOKEN')
    most_popular_languages = ['javascript', 'java', 'python', 'ruby', 'php', 'c++', 'c#', 'go', 'objective-c', 'scala', 'swift']
    statistics_sj = get_stat_to_most_popular_language_superjob(secret_key, most_popular_languages)
    statistics_hh = get_stat_to_most_popular_language_hh(most_popular_languages)
    print_stat_to_vacancies(statistics_sj, 'SuperJob Moscow')
    print_stat_to_vacancies(statistics_hh, 'HeadHunter Moscow')

if __name__ == "__main__":
    main()