import json
import math

CATALOG_FILENAME = 'catalog.json' 
RARITIES_FILENAME = 'rarities.json'
CALCULATED_FILENAME = 'calculated.json'

ORDERED_TIERS = ['Godly', 'Mythic', 'Legendary', 'Epic', 'Rare', 'Uncommon', 'Common']

def get_num_cards(packs):

    reformated = {}

    for pack in packs:

        reformated[pack['collectionName']] = {}

        for tier in ORDERED_TIERS:

            reformated[pack['collectionName']][tier] = pack['cards']['rarities'][tier]['num']

    return reformated

def get_prices(packs):

    reformated = {}

    for pack in packs:

        reformated[pack['collectionName']] = pack['price']

    return reformated

def calculate_chances_no_reselling(cards, num_cards, prices):

    for i in range(len(cards)):
    
        collections = {}

        for collection in cards[i]['collections']:

            tier = cards[i]['tierLabel']
            collections[collection] = {}

            chance_per_card = RARITIES[tier] * (1 / num_cards[collection][tier])
            collections[collection]['chancePerCard'] = chance_per_card
            foil_chance_per_card = chance_per_card * FOIL_CHANCE
            collections[collection]['foilChancePerCard'] = foil_chance_per_card

            chance_per_pack = 1 - ((1 - chance_per_card)**5)
            collections[collection]['chancePerPack'] = chance_per_pack
            foil_chance_per_pack = 1 - ((1 - foil_chance_per_card)**5)
            collections[collection]['foilChancePerPack'] = foil_chance_per_pack

            expected_packs = math.ceil(1 / chance_per_pack)
            collections[collection]['expectedPacks'] = expected_packs
            foil_expected_packs = math.ceil(1 / foil_chance_per_pack)
            collections[collection]['foilExpectedPacks'] = foil_expected_packs

            expected_cost = expected_packs * prices[collection]
            collections[collection]['expectedCost'] = expected_cost
            foil_expected_cost = foil_expected_packs * prices[collection]
            collections[collection]['foilExpectedCost'] = foil_expected_cost

        cards[i]['collections'] = collections

def calculate_expected_pack_resale_value(packs, cards):

    for i in range(len(packs)):
        packs[i]['expectedResaleCredits'] = 0

    for card in cards:

        for collection in card['collections'].keys():

            pass

if __name__ == '__main__':

    with open(RARITIES_FILENAME, 'r') as chances_file:
        chances = json.load(chances_file)

    FOIL_CHANCE = chances['Foil']

    RARITIES = chances['rarities']

    print('Chances:')
    print(f'{'Foil:':15} {FOIL_CHANCE*100}%')
    for tier in ORDERED_TIERS:
        print(f'{tier + ':':15} {RARITIES[tier]*100}%')

    with open(CATALOG_FILENAME, 'r') as catalog_file:
        catalog = json.load(catalog_file)

    cards = catalog['cards']

    packs = catalog['packs']

    num_cards = get_num_cards(catalog['packs'])
    print(num_cards)

    prices = get_prices(packs)
    print(prices)

    calculate_chances_no_reselling(cards, num_cards, prices)

    calculate_expected_pack_resale_value(packs, cards)

    catalog = {'cards': cards, 'packs': packs}

    with open(CALCULATED_FILENAME, 'w') as calculated_file:
        json.dump(catalog, calculated_file)
