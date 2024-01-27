from fb_scraper import get_group_posts_by_group_id

group_id = '140473731634479'
# group_id = '501370468320789'
# group_id = '1359582494109955'  # private 769054827223799


page = 1
print(f'Page {page}')
data = get_group_posts_by_group_id(group_id=group_id, cookies='tuli.txt')

while data['next_url']:
    page += 1
    cookies = 'keye.txt' if page % 2 == 0 else 'tuli.txt'
    print(f'Page {page} is using cookie {cookies}')
    data = get_group_posts_by_group_id(group_id=group_id, cookies=cookies, start_url=data['next_url'])

# with open('/home/bipni/Documents/fb-scraper/post_details.html', 'w', encoding='utf-8') as file:
#     file.write(post_response)
