import requests
import os
from collections import defaultdict
from itertools import count
from dotenv import load_dotenv
from terminaltables import AsciiTable

def get_stat_to_most_popular_language_hh(*languages):
    vacancies_stat = defaultdict(dict)
    for language in languages:
        print(language)
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
        summ_salaries = sum([salary for salary in salaries if salary is not None])
        len_salaries = len([salary for salary in salaries if salary is not None])
        
        mean_salary = int(summ_salaries / len_salaries)

        return mean_salary

def get_vacancies_from_superjob(secret_key, keywords=''):
    url = 'https://api.superjob.ru/2.0/vacancies/'
    vacancies = []
    for page in count(0):
        params = {
            'town': 4,
            'catalogues': 48,
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


def get_stat_to_most_popular_language_superjob(secret_key, *languages):
    vacancies_stat = defaultdict(dict)

    for language in languages:
        keywords = f'Программист {language}'
        response = get_vacancies_from_superjob(secret_key, keywords=keywords)
        salary = predict_rub_salary_for_superjob(response[1])
        vacancies_stat[language]['vacancies_found'] = response[0]
        vacancies_stat[language]['vacancies_processed'] = len(salary)
        vacancies_stat[language]['average_salary'] = mean_predict_salary(salary)
        
    return vacancies_stat

def print_stat_superjob(secret_key):
    title = 'SuperJob Moscow'
    statistics_superjob = get_stat_to_most_popular_language_superjob(secret_key)
    table_data = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    for language in statistics_superjob:
        row = []
        row.append(language)
        row.append(statistics_superjob[language]['vacancies_found'])
        row.append(statistics_superjob[language]['vacancies_processed'])
        row.append(statistics_superjob[language]['average_salary'])
        table_data.append(row)
    
    table = AsciiTable(table_data, title)
    print(table.table)

def print_stat_hh():
    title = 'HeadHunter Moscow'
    statistics_superjob = get_stat_to_most_popular_language_hh()
    table_data = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    for language in statistics_superjob:
        row = []
        row.append(language)
        row.append(statistics_superjob[language]['vacancies_found'])
        row.append(statistics_superjob[language]['vacancies_processed'])
        row.append(statistics_superjob[language]['average_salary'])
        table_data.append(row)
    
    table = AsciiTable(table_data, title)
    print(table.table)
    
    

    

def main():
    load_dotenv()
    secret_key = os.getenv('SUPERJOB_TOKEN')
    languages = 'javascript', 'java', 'python', 'ruby', 'php', 'c++', 'c#', 'go', 'objective-c', 'scala', 'swift'
    print(get_stat_to_most_popular_language_superjob(secret_key, 'java', 'js', 'python'))

if __name__ == "__main__":
    main()