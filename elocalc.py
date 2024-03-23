import gspread
import math
from copy import deepcopy

# Function to scrape data from Google Sheet
def scrape_google_sheet_data(sheet_url, credentials_file):
    gc = gspread.service_account(filename=credentials_file)
    sheet = gc.open_by_url(sheet_url)
    worksheet = sheet.get_worksheet(1)
    data = worksheet.get_all_values()
    return data


def dataToGames(data):
    games = [[name for name in row[1:] if (name != 'DNP' and name != '')] for row in data]
    return [game for game in games if game]


def calcElos(games, start = 1000):
    namesToElo = {}
    for game in games:
        for player in game:
            namesToElo[player] = start
    for game in games:
        namesToEloCopy = deepcopy(namesToElo)
        for i in range(len(game)):
            player = game[i]
            playerELO = namesToElo[player]
            playersWonAgainst = game[i+1:]

            k = calculate_k_factor(len(game))

            for oppPlayer in playersWonAgainst:
                oppPlayerELO = namesToElo[oppPlayer]
                elo_change_winner, elo_change_loser = compute_elo_rating_change(playerELO, oppPlayerELO, k)
                namesToEloCopy[player] += elo_change_winner/(len(game)-1)
                namesToEloCopy[oppPlayer] += elo_change_loser/(len(game)-1)

        namesToElo = namesToEloCopy
    
    return namesToElo

def calculate_k_factor(num_players):
    return 52.5*(0.992**(28.33*num_players))#70*(1/num_players**1.04)
    #32*((2/3)**(num_players-2))
    

def compute_elo_rating_change(winner_elo, loser_elo, k_factor=32):
    expected_win = 1 / (1 + math.pow(10, (loser_elo - winner_elo)/100))
    elo_change_winner = k_factor * (1 - expected_win)
    elo_change_loser = -k_factor * (1 - expected_win)
    return elo_change_winner, elo_change_loser


# Main function
def main():
    # Specify Google Sheet URL and credentials file
    sheet_url = 'https://docs.google.com/spreadsheets/d/1V8f2uFsXb6UI-8Hbv_WQse4SjzMpSg_hxjHGoRfVqWc/edit#gid=533055230'
    # credentials_file = 'ai4u-auth-8f39a889acde.json'
    
    # Scrape data from Google Sheet
    data = scrape_google_sheet_data(sheet_url, credentials_file)
    print('First game considered: ', data[79][:9])
    games = dataToGames(data[79:])
    print('Last game considered: ', games[-1])
    Elos = calcElos(games)
    players_sorted = sorted(Elos.items(), key=lambda x: x[1], reverse=True)

    # Display the sorted elements one by one
    for i, (player, elo) in enumerate(players_sorted, start=1):
        print(f'{i}. {player}: \t{round(elo)}')
    print('\n\n\n\n\n\n\n\n\n\n')
if __name__ == "__main__":
    main()
