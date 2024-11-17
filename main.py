import json
import requests
from datetime import datetime
import mysql.connector

headers = {"x-fsign": "SW9D1eZo"}

target_leagues = ["РОССИЯ: КХЛ", "США: НХЛ"]

def delete_game_data(cursor, id_match):
    delete_query = "DELETE FROM `matches_24/25` WHERE id_match = %s"
    cursor.execute(delete_query, (id_match,))

def insert_game_data(cursor, game_data):
    insert_query = """
    INSERT INTO `matches_24/25` (id_match, data, league, team_1, team_2, score_team_1, score_team_2,
    score_team_match_1, score_team_match_2, score_team_bullian_1,
    score_team_bullian_2, status) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (
        game_data['id_match'],
        game_data['date'].strftime('%Y-%m-%d %H:%M:%S'),  # Форматирование даты
        game_data['league'],
        game_data['team_1'],
        game_data['team_2'],
        game_data['score_team_1'],
        game_data['score_team_2'],
        game_data['score_team_match_1'],
        game_data['score_team_match_2'],
        game_data['score_team_bullian_1'],
        game_data['score_team_bullian_2'],
        game_data['status']
    ))

def main():
    # Подключение к базе данных
    db_connection = mysql.connector.connect(
        host="88.218.67.237",
        user="user4",
        password="Z0t1x000123000zxc13)31!",
        database="hockey_base"
    )

    cursor = db_connection.cursor()

    feed = 'f_4_0_3_ru-kz_1'
    url = f'https://46.flashscore.ninja/46/x/feed/{feed}'
    response = requests.get(url=url, headers=headers)

    #response_size = len(response.content)  # Получаем размер ответа в байтах
    #print(f'Размер ответа: {response_size} байт')

    data = response.text.split('¬')

    data_list = [{}]
    current_league = None

    for item in data:
        key = item.split('÷')[0]
        value = item.split('÷')[-1]

        if key.startswith('~ZA'):  # Если это лига
            current_league = value
        elif key.startswith('~AA'):  # Если это матч
            game_data = {key: value}
            game_data['League'] = current_league  # Присваиваем текущую лигу к игре
            data_list.append(game_data)
        else:
            # Обновляем текущую игру с соответствующими данными
            if data_list:
                data_list[-1].update({key: value})

    # Обрабатываем и записываем данные матчей
    for game in data_list:
        if 'AA' in list(game.keys())[0]:
            date = datetime.fromtimestamp(int(game.get("AD")))
            team_1 = game.get("AE", "Неизвестная команда")
            team_2 = game.get("AF", "Неизвестная команда")
            score_team_1 = int(game.get("AG", 0))  # Конвертируем в int
            score_team_2 = int(game.get("AH", 0))  # Конвертируем в int
            score_team_match_1 = int(game.get("AT", 0))  # Конвертируем в int
            score_team_match_2 = int(game.get("AU", 0))  # Конвертируем в int
            score_team_bullian_1 = int(game.get("BJ", 0))  # Конвертируем в int
            score_team_bullian_2 = int(game.get("BI", 0))  # Конвертируем в int
            id_match = game.get("~AA")
            status = int(game.get("AB", 0))  # Конвертируем в int

            league = game.get('League')

            if league in target_leagues:
                game_data = {
                    'id_match': id_match,
                    'date': date,
                    'league': league,
                    'team_1': team_1,
                    'team_2': team_2,
                    'score_team_1': score_team_1,
                    'score_team_2': score_team_2,
                    'score_team_match_1': score_team_match_1,

                    'score_team_match_2': score_team_match_2,
                    'score_team_bullian_1': score_team_bullian_1,
                    'score_team_bullian_2': score_team_bullian_2,
                    'status': status
                }

                # Вывод информации
                print(
                    f'Лига: {league} | Дата: {date} | {team_1} vs {team_2} | Итоговый счет: {score_team_1}:{score_team_2} | Счет в основное время: {score_team_match_1}:{score_team_match_2} | Счет по буллитам: {score_team_bullian_1}:{score_team_bullian_2} | Айди матча: {id_match} | Статус матча: {status} ')

                # Сначала удаляем старые данные, если есть
                try:
                    delete_game_data(cursor, id_match)
                    db_connection.commit()  # Коммитим изменения
                    print(f"Старые данные удалены для матча: {id_match}")
                except mysql.connector.Error as err:
                    print(f"Ошибка при удалении данных: {err}")

                # Теперь вставляем новые данные
                try:
                    insert_game_data(cursor, game_data)
                    db_connection.commit()  # Коммитим изменения
                    print(f"Данные успешно добавлены в базу данных для матча: {id_match}")
                except mysql.connector.Error as err:
                    print(f"Ошибка при вставке данных: {err}")

    cursor.close()  # Закрыть курсор
    db_connection.close()  # Закрыть соединение с базой данных

if __name__ == "__main__":
    main()

