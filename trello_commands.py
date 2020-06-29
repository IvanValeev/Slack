import requests
import trello
import unittest
import os
from trello import TrelloClient
from trello.lists import Lists
from trello.cards import Cards
from trello.boards import Boards
from trello.board import Board



key = os.environ['TRELLO_KEY']
token = os.environ['TRELLO_TOKEN']

def connection(url, key, token, filter=None):

    params_key_and_token = {'key':key,'token':token, 'filter':filter}
    arguments = {'fields': 'name', 'lists': 'open'}

    return requests.get(url, params=params_key_and_token, data=arguments)


def my_get_boards(key, token):

    dict_of_boards_ids = {}

    url = 'https://api.trello.com/1/members/me/boards'  
    response_array_of_dict = connection(url, key, token).json()

    for board in response_array_of_dict:
        dict_of_boards_ids[board['name']] = board['id']

    return dict_of_boards_ids


def my_get_columns(board_id, key, token):

    result={}

    url = f"https://api.trello.com/1/boards/{board_id}/lists"  
    answer = connection(url, key, token).json()

    for list in answer:
        result[list['name']] = list['id']

    return result

def my_get_cards(list_id, key, token):

    dict_of_cards_ids = {}    

    url = f"https://api.trello.com/1/lists/{list_id}/cards"
    response = connection(url, key, token).json()

    for card in response:
        dict_of_cards_ids[card['name']] = card['id']

    return dict_of_cards_ids


def my_get_label(key,token, card_id):

    labels = {}

    url = f"https://api.trello.com/1/cards/{card_id}"
    response = connection(url, key, token).json()

    for label in response['labels']:
        labels[label['color']] = label['id']

    return labels


def my_get_members(key, token, board_id):
    """
    Return dictionary of board member's ({'username':'id'})
    """

    members = {}

    client = Boards(key, token)
    list_of_members = client.get_member(board_id)

    for member in list_of_members:
        members[member['username']] = member['id']

    return members


def create_new_board(key,token, name_of_board):

    client = TrelloClient(key, token)
    client.add_board(name_of_board)


def add_list_to_board(key,token, board_id, name_of_list):

    client = Lists(key, token)
    client.new(name_of_list, board_id)


def add_card_to_list(key, token, list_id, name_of_card):

    client = Cards(key, token)
    client.new(name_of_card, list_id)


def add_label_to_card(key, token, card_id, color, name=None):

    client = Cards(key, token)
    client.new_label(card_id, color, name)

def is_legend_absent(board_id, key, token):

    '''
    This method checks if there is a legend column in the table, if it is absent, it creates it with a list of board members.
    '''
    members = my_get_members(key, token, board_id)

    if 'Legend' not in my_get_columns(board_id, key, token):
        add_list_to_board(key,token, board_id, 'Legend')
        for member in members.keys():
            add_card_to_list(key, token, my_get_columns(board_id, key, token)['Legend'], member)
 
    elif 'Legend' in my_get_columns(board_id, key, token) and my_get_cards(my_get_columns(board_id, key, token)['Legend'], key, token).keys() != my_get_members(key, token, board_id).keys():

        id = my_get_columns(board_id, key, token)['Legend']
        params_key_and_token = {'key':key,'token':token}
        url = f"https://api.trello.com/1/lists/{id}/archiveAllCards"

        response = requests.request(
        "POST",
        url,
        params = params_key_and_token
        )
    
        for member in members.keys():
            add_card_to_list(key, token, my_get_columns(board_id, key, token)['Legend'], member)


def unique_legend_labels(key, token, board_id):
    """
    Adds unique labels for all cards in Legend
    """
    colors = ['green', 'orange', 'purple', 'blue', 'lime', 'pink', 'sky', 'black']
    legend_id = my_get_columns(board_id, key, token)['Legend']
    members = my_get_cards(legend_id, key, token)
    members_names = list(members.keys())

    for i in range(len(members_names)):
        if i < len(colors):
            j = i
            add_label_to_card(key, token, members[members_names[i]], colors[j], name=members_names[i])
        elif i >= len(colors):
            j = i - len(colors)
            add_label_to_card(key, token, members[members_names[i]], colors[j], name=members_names[i])


def labels_according_to_legend(key, token, board_id):
    """
    Coloring of existed cards according to legend
    """

    client = TrelloClient(key, token)
    board = Board(client= client, board_id=board_id)
    list_of_lists = board.list_lists(list_filter='open')
    creators = my_get_members(key, token, board_id)
    legend_id =''
    legend_labels = {}
    list_of_cards = []

    for list in range(len(list_of_lists)):

        if list_of_lists[list].name == 'Legend':
            legend_id = list_of_lists[list].id
            list_of_lists.pop(list)
            break
    
    get_cards = my_get_cards(legend_id, key, token)

    for card in get_cards.keys():
        for label in my_get_label(key,token, get_cards[card]):
            legend_labels[creators[card]] = my_get_label(key,token, get_cards[card])[label]

    for list in list_of_lists:
        for card in list.list_cards():
            list_of_cards.append(card)

    for card in list_of_cards:
        id = card.id
        url = f"https://api.trello.com/1/cards/{id}/actions"
        response = connection(url, key, token, filter=['updateCard', 'createCard'])
        client = Cards(key,token)

        try:
            client.new_idLabel(id, legend_labels[response.json()[0]['idMemberCreator']])
        except:
            pass

def unlim_labeling(key, token, board_id):

    while True:
        print('Working...')
        labels_according_to_legend(key, token, board_id)
