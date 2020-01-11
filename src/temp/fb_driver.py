import sys
import facebook
import requests
import pprint
import random
from database import bookfaceDriver

class FacebookWrapper:
    def __init__(self, token):
        self.graph = facebook.GraphAPI(token)
        self.group_ids = {'417338889185518': 1, '1734025586728135': 1, '450484819215000': 2, '479386619362962': 2, '1026341897743105': 2, '2614963465260510': 3}

    def getGroupIDs(self):
        return self.group_ids

    def getGroupsDetails(self):
        groups_details = []
        fb_group_details = self.graph.get_object("/me/groups?fields=administrator,description,name,owner,picture")
        for fb_group in fb_group_details['data']:
            if fb_group["id"] in self.group_ids:
                group_details = {}
                group_details["_id"] = fb_group["id"]
                group_details["fb_id"] = fb_group["id"]
                group_details["name"] = fb_group["name"]
                group_details["description"] = fb_group.get("description", "")
                if "picture" in fb_group:
                    if "data" in fb_group["picture"]:
                        if "url" in fb_group["picture"]["data"]:
                            group_details["profile_picture"] = fb_group["picture"]["data"]["url"]
                group_details["category"] = self.group_ids[fb_group["id"]]
                group_details["group_admin_id"] = fb_group["owner"]["id"]
                groups_details.append(group_details)
        return groups_details

    def getEventTimeName(self, event_id):
        event_time = self.graph.get_object(event_id)["start_time"]
        event_name = self.graph.get_object(event_id)["name"]
        return event_time, event_name


    def getPostAttachments(self, post_id):
        # Assumes only one attachment per post
        attachment = {}
        fb_attachment = self.graph.get_object(post_id + "/attachments")
        if fb_attachment['data'] != []:
            fb_attachment_data = fb_attachment['data'][0]
            attachment['type'] = fb_attachment_data['type']
            attachment['fb_id'] = fb_attachment_data['target']['id']
            if attachment['type'] == "event":
                time, name = self.getEventTimeName(attachment['fb_id'])
            is_image_present = False
            if 'media' in fb_attachment_data:
                if 'image' in fb_attachment_data['media']:
                    if 'src' in fb_attachment_data['media']['image']:
                        attachment['link'] = fb_attachment_data['media']['image']['src']
                        is_image_present = True
            attachment['title'] = fb_attachment_data['description']
        if attachment.get('type', '') == "event":
            if is_image_present:
                attachment["type"] = "photo"
            return attachment, time, name
        else:
            return attachment
    
    def getGroupPosts(self, group_id):
        group_posts = []
        fb_group_posts = self.graph.get_object(group_id + "/feed")
        for fb_post in fb_group_posts['data']:
            post = {}
            if 'message' in fb_post:
                post['_id'] = fb_post['id']
                post['fb_id'] = fb_post['id']
                post['message'] = fb_post['message']
                post['timestamp'] = fb_post['updated_time']
                post['group_id'] = group_id
                post['category'] = self.group_ids[group_id]
                post['attachment'] = self.getPostAttachments(fb_post['id'])
                group_posts.append(post)
            elif 'story' in fb_post and 'created an event' in fb_post['story']:
                post['_id'] = fb_post['id']
                post['fb_id'] = fb_post['id']
                post['timestamp'] = fb_post['updated_time']
                post['group_id'] = group_id
                post['category'] = self.group_ids[group_id]
                post['attachment'], time, name = self.getPostAttachments(fb_post['id'])
                post['time'] = time
                post['message'] = name
                group_posts.append(post)
        return group_posts
    
    def getAllPosts(self):
        all_posts = []
        groups_ids = self.getGroupIDs()
        for group_id in groups_ids:
            group_posts = self.getGroupPosts(group_id)
            all_posts = all_posts + group_posts
        return all_posts


class PopulateDatabase(FacebookWrapper):
    def __init__(self, token):
        super().__init__(token)
        self.bf_driver = bookfaceDriver.BookfaceDriver()
        self.all_posts = self.getAllPosts()
        self.groups_details = self.getGroupsDetails()

    def populatePostsAndAttachments(self):
        self.bf_driver.clear_all_posts()
        for post in self.all_posts:
            self.bf_driver.insert_posts(post)

    def populateGroups(self):
        self.bf_driver.clear_all_groups()
        for group in self.groups_details:
            self.bf_driver.insert_groups(group)


def main():
    populateDB = PopulateDatabase(sys.argv[1])
    populateDB.populatePostsAndAttachments()
    populateDB.populateGroups()


if __name__ == "__main__":
    main()