import numpy as np
import pandas as pd
from tabulate import tabulate
from time import sleep

def user_bot_x_o_choise():
    '''
    Выбор пользователем х или о
    '''
    while True:
        print()
        user = input('Игрок, введите "x" для игры крестиками или "o" для игры ноликами: ')
        if user not in ['x', 'o']:
            print('Неверный ввод, необходимо ввести или "x" или "o"')
            continue
        user_message = f'Игрок играет {"крестиками" if user=="x" else "ноликами"}'
        x_o_list = ["x", "o"]
        x_o_list.remove(user)
        bot = x_o_list[0]
        bot_message = f'Бот играет {"крестиками" if bot=="x" else "ноликами"}'
        print('-'*max(len(user_message), len(bot_message)), user_message, bot_message, '-'*max(len(user_message), len(bot_message)), sep='\n')
        break
    return user, bot

def user_input():
    '''
    Функция ввода координат хода игроком с выполнением проверок на допустимость входных данных
    '''
    while True:
        user_move = input('Ход игрока, введите две координаты через пробел: ').split()
        if len(user_move) != 2:
            print('Неверный ввод, координаты должны быть двумя числами, введеными через пробел. Повторите ввод.')
            continue
        elif not user_move[0].isdigit or not user_move[1].isdigit():
            print('Неверный ввод, координаты должны быть двумя числами, введеными через пробел. Повторите ввод.')
            continue
        elif not 0 <= int(user_move[0]) <= 2 or not 0 <= int(user_move[1]) <= 2:
            print(
                'Неверный ввод, координаты должны быть двумя целыми числами в диапазоне от 0 до 2. Повторите ввод.')
            continue
        elif x_o_table[int(user_move[0])][int(user_move[1])] != '-':
            print(
                f'Неверный ввод, данный ход уже был выполнен {"вами" if x_o_table[int(user_move[0])][int(user_move[1])] == user else "вашим соперником"}. Повторите ввод.')
            continue
        user_move = list(map(int, user_move))
        break
    return user_move

def user_move(user):
    user_move = user_input()
    x_o_table[user_move[0]][user_move[1]] = user
    print(tabulate(x_o_table, headers=x_o_table.columns, tablefmt='presto', stralign='center'))
    print()

def bot_move(bot, user):
    '''
    Функция выполнения хода ботом
    '''

    def bot_parse_columns_critical_move(bot, do_not_loose_mode=False, user=None, transposed=False):

        '''
        Функция проверки по колонкам датафрейма и выполнения критических ходов в игре либо чтобы выиграть после сделанного хода либо чтобы предотвратить проигрыш в результате сделанного хода
        '''

        global x_o_table

        if do_not_loose_mode:
            player = user
        else:
            player = bot

        if transposed:
            x_o_table = x_o_table.T # транспонирование датафрейма игры

        move_is_done = False
        for column in x_o_table.columns:
            player_moves_mask = x_o_table[column] == player
            empty_cell_mask = x_o_table[column] == '-'
            if player_moves_mask.sum() == 2 and empty_cell_mask.sum() == 1:
                empty_cell_index = pd.Index(empty_cell_mask).get_loc(True)
                x_o_table[column][empty_cell_index] = bot
                if transposed:
                    print(f'Ход бота: {empty_cell_index} {column}') # при выводе хода бота координаты хода поменяли местами т.к. матрица игры пока транспонированная
                    print(tabulate(x_o_table.T, headers=x_o_table.columns, tablefmt='presto', stralign='center'))
                    print()
                    move_is_done = True
                    break
                else:
                    print(f'Ход бота: {column} {empty_cell_index}')
                    print(tabulate(x_o_table, headers=x_o_table.columns, tablefmt='presto', stralign='center'))
                    print()
                    move_is_done = True
                    break

        if transposed:
            x_o_table = x_o_table.T # обратное транспонирование датафрейма игры в исходный вид, если транспонирование применяется при работе функции

        return move_is_done

    def bot_parse_diagonal_critical_move(bot, do_not_loose_mode=False, user=None, opposite_diagonal=False):

        '''
        Функция проверки по диагоналям датафрейма и выполнения критических ходов в игре либо чтобы выиграть после сделанного хода либо чтобы предотвратить проигрыш в результате сделанного хода
        '''

        global x_o_table

        if do_not_loose_mode:
            player = user
        else:
            player = bot

        if opposite_diagonal:
            diag_values = pd.Series(np.diag(np.fliplr(x_o_table.values))[::-1])
        else:
            diag_values = pd.Series(np.diag(x_o_table.values))

        move_is_done = False
        player_moves_mask = diag_values == player
        empty_cell_mask = diag_values == '-'
        if player_moves_mask.sum() == 2 and empty_cell_mask.sum() == 1:
            empty_cell_index = pd.Index(empty_cell_mask).get_loc(True)
            if opposite_diagonal:
                x_o_table[empty_cell_index][2-empty_cell_index] = bot
                print(f'Ход бота: {empty_cell_index} {2-empty_cell_index}')
                move_is_done = True
            else:
                x_o_table[empty_cell_index][empty_cell_index] = bot
                print(f'Ход бота: {empty_cell_index} {empty_cell_index}')
                move_is_done = True

        if move_is_done:
            print(tabulate(x_o_table, headers=x_o_table.columns, tablefmt='presto', stralign='center'))
            print()

        return move_is_done

    def bot_random_move(bot):

        global x_o_table

        move_is_done = False
        # получаем массивы координат пустых ячеек
        rows, columns = np.where(x_o_table == '-')
        # получаем список кортежей координат пустых ячеек
        empty_cells_coords_list = [(row, column) for row, column in zip(rows, columns)]
        if len(empty_cells_coords_list) != 0:
            random_move_coords = empty_cells_coords_list[np.random.randint(0, len(empty_cells_coords_list))]
            x_o_table[random_move_coords[1]][random_move_coords[0]] = bot
            print(f'Ход бота: {random_move_coords[1]} {random_move_coords[0]}')
            print(tabulate(x_o_table, headers=x_o_table.columns, tablefmt='presto', stralign='center'))
            print()
            move_is_done = True
            return move_is_done
        else:
            return move_is_done


    ###########################
    # Проверка строк и столбцов
    ###########################
    # проверка ботом возможности выигрыша и выполнение выигрышного хода при такой возможности
    move_is_done = bot_parse_columns_critical_move(bot) # проверка по колонкам
    if move_is_done:
        return
    move_is_done = bot_parse_columns_critical_move(bot, transposed=True) # проверка по строкам на транспонированном датафрейме игры
    if move_is_done:
        return

    # проверка ботом возможности проигрыша и выполнение хода, предотвращающего проигрыш при такой возможности
    move_is_done = bot_parse_columns_critical_move(bot, do_not_loose_mode=True, user=user)  # проверка по колонкам
    if move_is_done:
        return
    move_is_done = bot_parse_columns_critical_move(bot, do_not_loose_mode=True, user=user, transposed=True)  # проверка по строкам
    if move_is_done:
        return

    #####################
    # Проверка диагоналей
    #####################
    # проверка ботом возможности выигрыша и выполнение выигрышного хода
    move_is_done = bot_parse_diagonal_critical_move(bot) # проверка по главной диагонали (справа налево)
    if move_is_done:
        return
    move_is_done = bot_parse_diagonal_critical_move(bot, opposite_diagonal=True) # проверка по противоположной диагонали (слева направо)
    if move_is_done:
        return

    # проверка ботом возможности проигрыша и выполнение хода, предотвращающего проигрыш при такой возможности
    move_is_done = bot_parse_diagonal_critical_move(bot, do_not_loose_mode=True, user=user) # проверка по главной диагонали (справа налево)
    if move_is_done:
        return
    move_is_done = bot_parse_diagonal_critical_move(bot, do_not_loose_mode=True, user=user, opposite_diagonal=True) # проверка по противоположной диагонали (слева направо)
    if move_is_done:
        return

    ######################################
    # Ход бота, если все проверки пройдены
    ######################################
    move_is_done = bot_random_move(bot)
    if move_is_done:
        return

def gameplay_check():

    '''
    Функция оценки состояния игры
    '''

    global x_o_table

    game_over = False
    rows = x_o_table.values.tolist()
    columns = x_o_table.T.values.tolist()
    diag_values = np.diag(x_o_table.values).tolist()
    opposit_diag_values = np.diag(np.fliplr(x_o_table.values))[::-1].tolist()
    values_check_list = rows + columns + [diag_values] + [opposit_diag_values]
    # print(values_check_list)
    for values in values_check_list:
        if len(set(values)) == 1:
            # print(len(set(values)))
            if list(set(values))[0] == user:
                win_message = 'Вы победили! Изра завершена.'
                print('*' * len(win_message), win_message, '*' * len(win_message), sep='\n')
                game_over = True
                break
            elif list(set(values))[0] == bot:
                loose_message = 'Вы проиграли. Игра завершена.'
                print('*' * len(loose_message), loose_message, '*' * len(loose_message), sep='\n')
                game_over = True
                break

    if '-' not in x_o_table.values:
        draw_message = 'Игра завершилась ничьей.'
        print('*' * len(draw_message), draw_message, '*' * len(draw_message), sep='\n')
        game_over = True

    return game_over


# Скрипт игры

user, bot = user_bot_x_o_choise()

start_game_message = 'Начинаем игру'
print('', '*' * len(start_game_message), start_game_message, '*' * len(start_game_message), '', sep='\n')

# Создаем двумерный датафрейм таблицы игры
x_o_table = pd.DataFrame([['-' for _ in range(3)] for _ in range(3)])
print(tabulate(x_o_table, headers=x_o_table.columns, tablefmt='presto', stralign='center'))
print()

while True:
    if bot == 'x':
        sleep(1.5)
        bot_move(bot, user)
        game_over = gameplay_check()
        if game_over:
            break
        user_move(user)
        game_over = gameplay_check()
        if game_over:
            break
    else:
        user_move(user)
        game_over = gameplay_check()
        if game_over:
            break
        sleep(1.5)
        bot_move(bot, user)
        game_over = gameplay_check()
        if game_over:
            break




