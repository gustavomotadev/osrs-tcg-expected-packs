import json

INDEXEDDB_FILENAME = 'indexeddb.json' 

def clean_cards(cards, cards_are_npcs, collections):

    IMPORTANT_SUBKEYS = {'tcg': ['score', 'foilScore', 'tierLabel']}
    KEYS_TO_POP = ['id', 'examine', 'wiki', 'imagePath', 'tcg', 'regions']

    for i in range(len(cards)):

        # print(f'Cleaning item {i+1} of {len(items)}. Name: {items[i]['name']}')

        if cards_are_npcs:
            cards[i]['type'] = 'npc'
        else:
            cards[i]['type'] = 'item'

        cards[i]['collections'] = []

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
    return unique_keys

def filter_large_packs(packs):
    return list(filter(lambda p: not (p['id'].endswith('large') or 
            p['name'].endswith('x10')), packs))

def get_collections_from_packs(packs):
    collections = set()
    for pack in packs:
        collections = collections | set(pack['category'])
    return collections

def get_collections_from_cards(cards):
    collections = set()
    for card in cards:
        collections = collections | set(card['collections'])
    return collections

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

    pack_collections = get_collections_from_packs(packs)

    print(f'Found {len(pack_collections)} collections in packs: {sorted(list(pack_collections))}.')

    clean_cards(items, False, pack_collections)
    print(f'Unique keys in items after cleanup: {sorted(list(get_unique_keys(items)))}.')

    clean_cards(npcs, True, pack_collections)
    print(f'Unique keys in npcs after cleanup: {sorted(list(get_unique_keys(items)))}.')

    card_collections = get_collections_from_cards(items + npcs)

    print(f'Found {len(card_collections)} collections in cards: {sorted(list(card_collections))}.')