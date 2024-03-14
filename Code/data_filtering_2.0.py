import pandas as pd

file_path = 'CMV_July_2022.csv'
data = pd.read_csv(file_path)

def add_tlc_id(data):
    id_to_parent = dict(zip(data['id'], data['parent_id']))
    def find_top_level_id_fast(comment_id):
        """Find the top-level ID for a given comment ID."""
        current_id = comment_id
        current_parent_id = id_to_parent.get(current_id, None)
        while current_parent_id and not current_parent_id.startswith("t3"):
            current_id = current_parent_id[3:]
            current_parent_id = id_to_parent.get(current_id, None)
        return current_id

    data['top_level_id'] = None
    data.loc[data['parent_id'].str.startswith("t3"), 'top_level_id'] = data['id']
    non_top_level_rows = data[data['top_level_id'].isnull()]
    data.loc[non_top_level_rows.index, 'top_level_id'] = non_top_level_rows['id'].apply(find_top_level_id_fast)
    return data






def get_OP_comments(data):
    submitter_rows = data[data['is_submitter'] == True]







# this is an object that represents a comment and all its children
class RedditComment:
	# when we create it, initialize an empty list for the children
	def __init__(self, id):
		self.id = id
		self.children = []

	# recursively count how many children this comment has
	def total_children(self):
		count_children = 0
		for child in self.children:
			count_children += 1
			count_children += child.total_children()
		return count_children

if __name__ == "__main__":
	# put any top level comments we find here
	top_level_comments = []
	# keep a dictionary mapping id to comment
	all_comments_dict = {}
	for comment in comments: #need to link this to the database
		reddit_comment = RedditComment(comment['id'])
		# add the comment to the dict by its id so we can look it up later
		all_comments_dict[comment['id']] = reddit_comment

		if comment.parent_id.startswith("t3"):
			# if the parent id starts with t3, the parent is the submission, which means this is a top level comment
			top_level_comments.append(reddit_comment)
		else:
			# otherwise it's in a tree somewhere, so find its parent
			# the parent_id field is actually the parent fullname, so to get the comment id we need to cut the t1_ off the front
			parent_comment_id = comment['parent_id'][3:]
			# lookup the parent in the table
			parent_comment = all_comments_dict[parent_comment_id]
			# now add this comment as a child
			parent_comment.children.append(reddit_comment)

	# we've added all comments to our tree, now print out the top level ones with their count of children
	for reddit_comment in top_level_comments:
		print(f"{reddit_comment.id} : {reddit_comment.total_children()})