target = 4901740154402535512
# https://stackoverflow.com/questions/2590677/how-do-i-combine-hash-values-in-c0x
'''
template <class T>
inline void hash_combine(std::size_t& seed, const T& v)
{
    std::hash<T> hasher;
    seed ^= hasher(v) + 0x9e3779b9 + (seed<<6) + (seed>>2);
}
'''
'''
result = 0 ^ (915 + 0x9e3779b9 + (0 << 6) + (0 >> 2)) == 2654436684 
result = 2654436684  ^ (second + 0x9e3779b9  + (2654436684  << 6) + (2654436684  >> 2))
'''
confirmed_cards = {
    "Legacy": "Ancient Mage",
    "Goblins vs Gnomes": "Jeeves",
    "League of Explorers": "Murloc Tinyfin",
    "Whispers of the Old Gods": "Faceless Behemoth",
    "Journey to Un'Goro": "Emerald Reaver",
    "Knights of the Frozen Throne": "Doomed Apprentice",
    "Kobolds and Catacombs": "Boisterous Bard",
    "The Witchwood": "Wyrmguard",
    "The Boomsday Project": "Arcane Dynamo",
    "Rise of Shadows": "Arcane Servant",
    "Descent of Dragons": "Evasive Wyrm",
    "Galakrond's Awakening": "Frenzied Felwing",
    "Ashes of Outland": "Starscryer",
    "Scholomance Academy": "Steward of Scrolls",
    "Forged in the Barrens": "Sunwell Initiate",
    "Deadmines": "Golakka Glutton",
    "Fractured in Alterac Valley": "Gankster",
    "Murder at Castle Nathria": "Prince Renathal",
    "Maw and Disorder": "Afterlife Attendant",
    "March of the Lich King": "Sunfury Clergy",
    "Festival of Legends": "E.T.C., Band Manager",
    "Audiopocalypse": "Speaker Stomper",
    "TITANS": "Starlight Whelp",
    "Caverns of Time": "Future Emissary",
    "Showdown in the Badlands": "Sunspot Dragon",
    "Delve into Deepholm": "Stone Drake",
    "Event": "Harth Stonebrew"
}

likely_cards = {
    "Rastakhan's Rumble": "Regeneratin' Thug",
    "Saviors of Uldum": "Vilefiend",
    "Darkmoon Races": "Crabrider",
    "Wailing Caverns": "Devouring Ectoplasm",
    "Onyxia's Lair": "Gear Grubber",
    "Throne of the Tides": ["Submerged Spacerock", "Snapdragon", "Bubbler"],
    "Return to Naxxramas": "Lost Exarch",
    "Fall of Ulduar": "Tainted Remnant",
}

unsolved_sets = {
    "Curse of Naxxramas",
    "Blackrock Mountain",
    "The Grand Tournament",
    "One Night in Karazhan",
    "Mean Streets of Gadgetzan"
}


def hash_combine(numbers):
    total = 0
    for number in numbers:
        total += hash_not_combine(total, number)
    return total

def hash_not_combine(total, dbf_id):
    return total ^ (dbf_id + 0x9e3779b9 + (total << 6) + (total >> 2))


result = 0 ^ (915 + 0x9e3779b9 + (0 << 6) + (0 >> 2))
print(result)
