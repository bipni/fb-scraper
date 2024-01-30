from fb_scraper import (
    get_group_posts_by_group_id,
    get_page_posts_by_page_id,
    get_profile,
)

# group_id = '140473731634479'
# group_id = '501370468320789'
# group_id = '1359582494109955'  # private 769054827223799


# page = 1
# print(f'Page {page}')
# data = get_group_posts_by_group_id(group_id=group_id, cookies='keye.txt')
# print(data)

# while data['next_url']:
#     page += 1
#     cookies = 'keye.txt' if page % 2 == 0 else 'tuli.txt'
#     print(f'Page {page} is using cookie {cookies}')
#     data = get_group_posts_by_group_id(group_id=group_id, cookies=cookies, start_url=data['next_url'])

# with open('/home/bipni/Documents/fb-scraper/post_details.html', 'w', encoding='utf-8') as file:
#     file.write(post_response)

# https://mbasic.facebook.com/profile.php?id=100077515030449&v=timeline
# https://mbasic.facebook.com/earkidotcom?v=timeline

# page_id = '100077515030449'
# page_id = 'earkidotcom'

# data = get_page_posts_by_page_id(page_id=page_id, cookies='tuli.txt', start_url=None)
# print(data)

# profile_id = '100089632299605'  # locked profile
# profile_id = '100069502939023'  # about
profile_id = '100090975546293'

data = get_profile(profile_id=profile_id, cookies='tuli.txt')
print(data)
