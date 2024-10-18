import re
lyrics_dict = {}
with open("C:/Users/bkb/Downloads/方大同 - 够不够.lrc", 'r', encoding='utf-8') as f:
    lrc_content = f.read()

    pattern = r'\[(\d{2}):(\d{2})\.(\d{2})\](.*)'
    matches = re.findall(pattern, lrc_content)
    # print(matches)
    for match in matches:
        minutes, seconds, milliseconds = map(int, match[0:3])
        timestamp = minutes * 60 + seconds + milliseconds / 100
        lyrics = match[3].strip()
        if lyrics:
            lyrics_dict[timestamp] = lyrics
    
    lyrics_dict = dict(sorted(lyrics_dict.items()))
    # print(lyrics_dict)
    current_timestamp = None
    for timestamp in lyrics_dict.keys():
        if timestamp > current_time:
            break
        current_timestamp = timestamp