import json

INDEXEDDB_FILENAME = 'indexeddb.json' 

ORDERED_TIERS = ['Godly', 'Mythic', 'Legendary', 'Epic', 'Rare', 'Uncommon', 'Common']

def clean_packs(packs):

    KEYS_TO_POP = ['id', 'thumbnail', 'image', 'category', 'name']

    for i in range(len(packs)):

        for key in KEYS_TO_POP:
            # KeyError means nothing in this step
            packs[i].pop(key, None)

        if not packs[i]['collectionName']:
            packs[i]['collectionName'] = 'Standard'

def clean_cards(cards, cards_are_npcs, collections):

    IMPORTANT_SUBKEYS = {'tcg': ['score', 'foilScore', 'tierLabel']}
    KEYS_TO_POP = ['examine', 'wiki', 'imagePath', 'tcg', 'regions']

    for i in range(len(cards)):

        # print(f'Cleaning item {i+1} of {len(items)}. Name: {items[i]['name']}')

        if cards_are_npcs:
            cards[i]['type'] = 'npc'
        else:
            cards[i]['type'] = 'item'

        cards[i]['collections'] = ['Standard']

        regions = cards[i].get('regions', [])
        labels = cards[i].get('tcg', {}).get('tags', {}).get('labels', [])

        for collection in regions + labels:
            if collection in collections:
                cards[i]['collections'].append(collection)

        for key in IMPORTANT_SUBKEYS.keys():
            for subkey in IMPORTANT_SUBKEYS[key]:
                cards[i][subkey] = cards[i][key][subkey]

        for key in KEYS_TO_POP:
            # KeyError means nothing in this step
            cards[i].pop(key, None)

def get_unique_keys(data):
    unique_keys = set()
    for d in data:
        unique_keys = unique_keys | set(d.keys())
    return sorted(list(unique_keys))

def filter_large_packs(packs):
    # packs[:] to mutate original list
    packs[:] = list(filter(lambda p: not (p['id'].endswith('large') or 
            p['name'].endswith('x10')), packs))

def get_collections_from_packs(packs):
    collections = set()
    for pack in packs:
        if not pack['collectionName'] is None:
            collections.add(pack['collectionName'])
    return sorted(list(collections))

def get_collections_from_cards(cards):
    collections = set()
    for card in cards:
        collections = collections | set(card['collections'])
    return sorted(list(collections))

def get_tiers_from_cards(cards):
    tiers = set()
    for card in cards:
        tiers.add(card['tierLabel'])
    return sorted(list(tiers))

def add_cards_to_packs(packs, cards, tiers):

    for p in range(len(packs)):

        packs[p]['cards'] = {'num': 0, 'rarities': {}}
        for tier in tiers:
            packs[p]['cards']['rarities'][tier] = {'num': 0, 'list': []}

        for c in range(len(cards)):

            if packs[p]['collectionName'] in cards[c]['collections']:

                packs[p]['cards']['rarities'][cards[c]['tierLabel']]['list'].append(cards[c]['id'])
                packs[p]['cards']['rarities'][cards[c]['tierLabel']]['num'] += 1
                packs[p]['cards']['num'] += 1

if __name__ == '__main__':

    with open(INDEXEDDB_FILENAME, 'r') as indexeddb_file:

        indexeddb = json.load(indexeddb_file)

    items = indexeddb['liveJson']['items']
    npcs = indexeddb['liveJson']['npcs']

    packs = indexeddb['packsPayload']['packs']

    filter_large_packs(packs)

    print(f'Found: {len(items)} items.')
    print(f'Found: {len(npcs)} NPCs.')
    print(f'Found: {len(packs)} packs.')
    print(f'Total number of cards: {len(items) + len(npcs)}.')

    clean_packs(packs)
    print(f'Unique keys in packs after cleanup: {get_unique_keys(packs)}.')

    pack_collections = get_collections_from_packs(packs)

    clean_cards(items, False, pack_collections)

    clean_cards(npcs, True, pack_collections)

    if get_unique_keys(items) == get_unique_keys(npcs):
        print(f'Unique keys in cards match: {get_unique_keys(items)}')
    else:
        print('[WARNING] Card unique keys mismatch:')
        print(f'Unique keys in items after cleanup: {get_unique_keys(items)}.')
        print(f'Unique keys in npcs after cleanup: {get_unique_keys(npcs)}.')

    cards = items + npcs

    card_collections = get_collections_from_cards(cards)

    if pack_collections == card_collections:
        print(f'Card collections in packs and cards match: {pack_collections}')
    else:
        print('[WARNING] Card collections mismatch:')
        print(f'Found {len(pack_collections)} collections in packs: {pack_collections}.')
        print(f'Found {len(card_collections)} collections in cards: {card_collections}.')

    tiers = get_tiers_from_cards(cards)
    if set(tiers) == set(ORDERED_TIERS):
        print(f'Tiers from cards match: {ORDERED_TIERS}')
    else:
        print('[WARNING] Card tiers mismatch:')
        print(f'Found {len(tiers)} tiers in cards: {tiers}.')
        print(f'Correct tiers: {ORDERED_TIERS}.')

    add_cards_to_packs(packs, cards, ORDERED_TIERS)

    for pack in packs:
        print(f'{pack['collectionName']} Pack has {pack['cards']['num']} cards', end='')
        for tier in ORDERED_TIERS:
            print(f', {pack['cards']['rarities'][tier]['num']} {tier}', end='')
        print('.')

    catalog = {'cards': items+npcs, 'packs': packs}

    with open('catalog.json', 'w') as catalog_file:
        json.dump(catalog, catalog_file)