from fb_scraper import get_group_posts_by_group_id

# group_id = '140473731634479'
group_id = '501370468320789'
# group_id = '1359582494109955'  # private


get_group_posts_by_group_id(group_id=group_id, cookies='nila.txt')

# with open('/home/bipni/Documents/fb-scraper/post_details.html', 'w', encoding='utf-8') as file:
#     file.write(post_response)
