import gzip, requests, json, time, urllib
import opencc

"""
# API Endpoints
Last revised on 2024-11-14

- Video list information API, no cookie required, can get the cid of each part through bvid.
https://api.bilibili.com/x/player/pagelist?bvid=BV13f4y1G7sA

- Video part information API, requires cookie, can get the JSON subtitle link of the part through bvid and cid.
As of 2024-11-14, the API URL has been changed to: https://api.bilibili.com/x/player/wbi/v2?bvid=BV13f4y1G7sA&cid=391106273

- Subtitle file API, no cookie required, requires auth_key, which will expire.
http://aisubtitle.hdslb.com/bfs/subtitle/62fdb1a92f2b3cd943a76e747020d82c20275430.json?auth_key=1705912136-7063c95a74824f948b65fcd1e40e1e9b-0-aafa1c17b4b3b1dd5e1fa16553965cff
"""

encoding = 'utf-8'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0',
    }

cookie = {"SESSDATA": "",}
cookie_deprecated = {"SESSDATA": "",}

def set_cookie(cookie_string):
    # cookie = {i.split("=")[0]:i.split("=")[1] for i in cookie_string.split(";")} 
    global cookie
    cookie = ck


def download_all_subtitles(bv):
    """
    Download all subtitles for the given BV number.
    """
    video_list = get_video_list(bv)
    part_number = 1
    for video in video_list:
        cid = video['cid']
        download_single_subtitle(cid, bv, part_number, video['part'])  # Download subtitles for this part, 'part' is the name of the single part video.
        print('【Total Progress: %s/%s Parts】\n' % (part_number, len(video_list)))
        part_number += 1
    print('\n\n*** Task Completed ***\n')


def get_video_list(bv):
    """
    Return the video list for the given BV number.
    """
    url = 'https://api.bilibili.com/x/player/pagelist?bvid=%s' % bv  # Create URL
    print('Creating URL', url)
    video_list_response = requests.get(url, headers=headers, cookies=cookie).json()
    video_list = video_list_response['data']  # Convert JSON
    print('Request URL:', url)
    print('Video directory retrieved successfully! Total %s parts.\n' % len(video_list))
    return video_list


def download_single_subtitle(cid, bv, part_number, part_name=''):
    """
    Download all language subtitles for a single part using cid.
    """
    url = 'https://api.bilibili.com/x/player/wbi/v2?bvid=%s&cid=%s' % (bv, cid)
    print(url)
    data = requests.get(url, headers=headers, cookies=cookie).json()

    subtitle_list = data['data']['subtitle']['subtitles']  # Subtitle information list

    if len(subtitle_list) == 0: print('【Warning】Part %s has no subtitles!' % part_number)

    language_index = 1
    for subtitle in subtitle_list:
        language_code = subtitle['lan']  # Language code of the subtitle (e.g., ZH, JP, EN)
        file_name = bv + ' - P' + str(part_number) + '：' + sanitize_filename(part_name) + ' - ' + language_code  # Generate subtitle file name based on BV number, part number, and language
        subtitle_url = 'http:' + subtitle['subtitle_url']  # Subtitle URL

        # urllib.request.urlretrieve(subtitle_url, '%s.json' % file_name)  # Download JSON subtitle file
        response = urllib.request.urlopen(subtitle_url)  # Directly get content without downloading
        if response.info().get('Content-Encoding') == 'gzip':  # Get encoding format from response header
            json_content = gzip.decompress(response.read())
        else:
            json_content = response.read()
        json_to_srt(file_name, json_content)

        print('Part %s Language %s download completed, Progress: %s/%s' % (part_number, language_index, language_index, len(subtitle_list)))  # Report task progress (based on the number of subtitle languages for this part)

        language_index += 1
        time.sleep(0.2)


def json_to_srt(file_name, json_content):
    """
    Convert JSON subtitle content to SRT format and save to a file.
    """
    data = json.loads(json_content)['body']
    file = open('%s.srt' % file_name, 'w', encoding=encoding)  # Create SRT subtitle file
    # Initialize OpenCC for Simplified to Traditional conversion
    converter = opencc.OpenCC('s2t')
    subtitle_index = 1  # SRT subtitle sequence counter
    for subtitle in data:
        start_time = round(subtitle['from'], 3)  # Start time (rounded to three decimal places)
        end_time = round(subtitle['to'], 3)  # End time
        content = converter.convert(subtitle['content'])  # Convert subtitle content to Traditional Chinese
        formatted_start_time = time.strftime("%H:%M:%S", time.gmtime(start_time)) + ',' + format_milliseconds(start_time)  # Start time, convert seconds to HH:MM:SS format, add comma, and format milliseconds to three digits
        formatted_end_time = time.strftime("%H:%M:%S", time.gmtime(end_time)) + ',' + format_milliseconds(end_time)  # End time, same processing as above

        srt_content = str(subtitle_index) + '\n' + formatted_start_time + ' ' + '-->' + ' ' + formatted_end_time + '\n' + content + '\n\n'  # Format as SRT subtitle
        file.write(srt_content)  # Write to file
        subtitle_index += 1  # Increment counter

    file.close()
    print('%s OK.' % file_name)


invalid_filename_characters = [
    ['/','、'],
    ['\\','、'],
    ['|','、'],
    ['*','X'],
    [':','：'],
    ['?','？'],
    ['<','《'],
    ['>','》'],
    ['\"','“'],
    ['\"','”'],
]

def sanitize_filename(filename=''):
    """
    Remove special characters (not allowed in filenames) based on the list.
    """
    for char_pair in invalid_filename_characters:
        filename = filename.replace(char_pair[0], char_pair[1])
    return filename

def format_milliseconds(seconds):
    """
    Format milliseconds to three digits.
    """
    milliseconds = str(seconds).partition('.')[2]  # Get the fractional part
    milliseconds += '0' * (3 - len(milliseconds))  # Pad to three decimal places
    return milliseconds
