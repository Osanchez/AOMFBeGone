import twitter
import configparser

CC = configparser.RawConfigParser()
CC.read('settings.cfg')


class AOMFBeGone:
    def __init__(self, options):
        self.options = options
        self.api = None
        self.get_api()

    def get_api(self):
        consumer_key = self.options[0]
        consumer_secret = self.options[1]
        access_token_key = self.options[2]
        access_token_secret = self.options[3]

        self.api = twitter.Api(consumer_key=consumer_key,
                               consumer_secret=consumer_secret,
                               access_token_key=access_token_key,
                               access_token_secret=access_token_secret)

    def get_all_followers(self):
        print('Getting all of the users who follow you')
        followers = self.api.GetFollowers()
        print("Total Followers:", len(followers))
        print([x.screen_name for x in followers])
        return followers

    def get_all_following(self):
        print('Getting all the users you follow')
        following = self.api.GetFriends()
        print("Total Following:", len(following))
        print([x.screen_name for x in following])
        return following

    def get_non_followers(self):
        print('Getting all users you follow who do not follow you back')
        followers = self.get_all_following()
        all_follower_ids = [x.id for x in followers]
        non_followers = []

        # must be done in batches of 100
        total_followers = len(followers)

        index = 0
        offset = 100

        while index < total_followers:
            friendships = self.api.LookupFriendship(all_follower_ids[index:index + offset])
            for friendship in friendships:
                if friendship.followed_by is False:
                    non_followers.append(friendship.screen_name)
            index += offset

        return non_followers

    def unfollow_followers(self, followers, whitelist):
        print('Unfollowing Users')
        if len(followers) == 0:
            print('all the users you follow, follow you back!')
            return

        unfollowed_users = []

        for follower in followers:
            if follower in whitelist:
                continue
            else:
                self.api.DestroyFriendship(screen_name=follower)
                unfollowed_users.append(follower)

        print(unfollowed_users)

    def remove_all_following(self, whitelist):
        print('Removing all users you follow')
        all_following = self.get_all_following()
        self.unfollow_followers(all_following, whitelist)

    def remove_all_followers(self, whitelist):
        # This works by blocking all of your followers then unblocking them
        # This will remove all of those users from your followers list without alerting them
        print('Removing all users that follow you')
        all_followers = self.get_all_followers()

        for follower in all_followers:
            if follower.screen_name in whitelist:
                continue
            else:
                self.api.CreateBlock(screen_name=follower.screen_name)
                self.api.DestroyBlock(screen_name=follower.screen_name)

    def aomf_be_gone(self, whitelist):

        print("This will remove all people you follow and block all the people that follow you")
        answer = input('Are you sure you want to do this?: ')

        if str(answer).lower() == 'yes' or 'y':
            self.remove_all_following(whitelist)
            self.remove_all_followers(whitelist)


if __name__ == "__main__":
    # Get config file settings
    consumer_key = CC.get('AOMFBeGone', 'consumer_key')
    consumer_secret = CC.get('AOMFBeGone', 'consumer_secret')
    access_token = CC.get('AOMFBeGone', 'access_token')
    access_token_secret = CC.get('AOMFBeGone', 'access_token_secret')

    # Create the app instance
    settings = [consumer_key, consumer_secret, access_token, access_token_secret, False]
    app = AOMFBeGone(settings)

    # Call functions to remove all followers and following
    whitelist = ["maygan_11"]  # users who you want to keep relationships with
    non_followers = app.get_non_followers()
    app.unfollow_followers(non_followers, whitelist)
