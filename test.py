from fb_scraper import get_group_posts_by_group_id, set_cookies

set_cookies('nila.txt')

group_id = '140473731634479'

get_group_posts_by_group_id(group_id=group_id, cookies='nila.txt')

# with open('/home/bipni/Documents/fb-scraper/post_details.html', 'w', encoding='utf-8') as file:
#     file.write(post_response)
