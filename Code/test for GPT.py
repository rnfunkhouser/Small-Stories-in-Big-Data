# %% [markdown]
# ## Import packages

# %%
import pandas as pd
import csv


# %% [markdown]
# ## Define RedditComment Class and Functions

# %%
#define the class object
class RedditComment:
    def __init__(self, id, author, is_submitter=False, content=""):
        self.id = id
        self.author = author
        self.content = content
        self.is_submitter = is_submitter
        self.children = []
        self.op_replied = is_submitter
        self.is_tlc_author = False
        self.has_delta = False

    def total_children(self):
        count_children = 0
        for child in self.children:
            count_children += 1
            count_children += child.total_children()
        return count_children
    def update_delta_received(self):
        print(f"Checking deltas for comment ID {self.id}, number of children: {len(self.children)}")
        for child in self.children:
            print(f"Child ID {child.id}, Content: '{child.content[:50]}'")  # print the first 50 characters of content
            if "!delta" in child.content or "Δ" in child.content:
                print(f"Delta awarded by Child ID {child.id}")
                self.has_delta = True
        for child in self.children:
            child.update_delta_received()
    def update_op_replied(self):
        # Check if any child has op_replied set to True
        if any(child.op_replied for child in self.children):
            self.op_replied = True
        # Update all children to propagate op_replied status downward if needed
        for child in self.children:
            child.update_op_replied()
    def mark_tlc_author_comments(self, tlc_author):
        # Recursively mark if a comment is by the TLC author
        if self.author == tlc_author:
            self.is_tlc_author = True
        for child in self.children:
            child.mark_tlc_author_comments(tlc_author)
    def any_tlc_author_has_delta(self):
        # Check if this comment or any child has a delta and is from the TLC author
        if self.is_tlc_author and self.has_delta:
            return True
        return any(child.any_tlc_author_has_delta() for child in self.children)

# %% [markdown]
# ## Execute Class Functions on Data

# %%
if __name__ == "__main__":
    # Open the CSV file containing the Reddit data
    with open('/Users/ryanfunkhouser/Documents/Research/Active_Projects/SSiBD/Data/CMV_July_2022.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        # Initialize a dictionary to map id to RedditComment objects
        all_comments_dict = {}
        # Initialize a list for top-level comments
        top_level_comments = []
        # Process each row from the CSV
        for comment in reader:
            author = comment['author']
            content = comment.get('body', '').strip()  # Safely extract and ensure it's a string
            print(f"Extracted content: '{content[:50]}'")  # Debugging line
            is_submitter = comment['is_submitter'].lower() == 'true'
            reddit_comment = RedditComment(comment['id'], author, is_submitter)
            all_comments_dict[comment['id']] = reddit_comment
            # Check if the comment is a top-level comment
            if comment['parent_id'].startswith("t3"):
                top_level_comments.append(reddit_comment)
            else:
                # This assumes that the parent_id field is prefixed with "t1_" when the parent is a comment
                parent_comment_id = comment['parent_id'][3:]
                parent_comment = all_comments_dict.get(parent_comment_id)
                if parent_comment:
                    parent_comment.children.append(reddit_comment)
    for comment in top_level_comments:
        comment.mark_tlc_author_comments(comment.author)  # Pass the author of the top-level comment
        comment.update_op_replied()
        comment.update_delta_received()

    # Output top-level comments and their count of children
    for reddit_comment in top_level_comments:
        print(f"{reddit_comment.id} : {reddit_comment.total_children()}")

# %% [markdown]
# ## Various Iterations of Validation Print Statements

# %%
print(f"Number of top-level comments: {len(top_level_comments)}")
for comment in top_level_comments:
    print(f"Top-level comment ID: {comment.id}")

# %%
delta_count = 0
for comment in top_level_comments:
    if comment.update_delta_received():
        delta_count += 1

print(f"Number of top-level comments where there is a delta in the tree: {delta_count}")

# %%
def print_filtered_trees(comments):
    valid_trees_count = 0
    for comment in comments:
        print(f"Top Level Comment: {comment.id}, op_replied: {comment.op_replied}, any_tlc_author_has_delta: {comment.any_tlc_author_has_delta()}")
        if comment.op_replied and comment.any_tlc_author_has_delta():
            print("\nTop Level Comment:", comment.id)
            print_comment_structure(comment, include_tlc_author_only=True)
            valid_trees_count += 1
    print(f"\nTotal Comment Trees Matching Criteria: {valid_trees_count}")
print_filtered_trees(top_level_comments)

# %%
def print_filtered_trees(comments):
    valid_trees_count = 0
    for comment in comments:
        if comment.op_replied and comment.any_tlc_author_has_delta():
            print("\nTop Level Comment:", comment.id)
            print_comment_structure(comment, include_tlc_author_only=True)
            valid_trees_count += 1
    print(f"\nTotal Comment Trees Matching Criteria: {valid_trees_count}")

def print_comment_structure(comment, level=0, include_tlc_author_only=False):
    if not include_tlc_author_only or (include_tlc_author_only and comment.is_tlc_author):
        print('  ' * level + f"{comment.id} : {comment.total_children()} children")
    for child in comment.children:
        print_comment_structure(child, level + 1, include_tlc_author_only)
print_filtered_trees(top_level_comments)

# %%
def print_comment_structure(comment, level=0):
    # Print the current comment's ID and its children count, indented by the level in the hierarchy
    # Include a marker or note if the comment is by the TLC author
    tlc_author_marker = " (TLC Author)" if comment.is_tlc_author else ""    
    # Print the current comment's ID, its children count, and if it's by the TLC author
    print('  ' * level + f"{comment.id} ({comment.total_children()} children){tlc_author_marker}")
    for child in comment.children:
        print_comment_structure(child, level + 1)


for reddit_comment in top_level_comments:
    count = 0
    print_comment_structure(reddit_comment)
    count += 1
    if count >= 20:
        break

# %%
def print_filtered_comment_structure(comment, is_top_level=True):
    # Base check at the top level: proceed only if OP replied in this subtree
    if is_top_level and not comment.op_replied:
        return

    # Print or process the comment only if it is by the TLC author
    if comment.is_tlc_author:
        print(f"{comment.id} (TLC Author) : {comment.total_children()} children")

    # Recurse into children to continue checking and printing as necessary
    for child in comment.children:
        print_filtered_comment_structure(child, is_top_level=False)

for comment in top_level_comments:
    comment.update_op_replied()  # Make sure the op_replied is up to date
    print("\nTop Level Comment:", comment.id)
    print_filtered_comment_structure(comment)


# %%
#validation check for capturing if OP replied
# Print only those top-level comments where the OP has replied in the subtree
op_replied_count = 0
for comment in top_level_comments:
    if comment.op_replied:
        print_comment_structure(comment)
        op_replied_count += 1
    if comment.
print(f"Total top-level comments where the OP replied: {op_replied_count}")



# %%
#validation check for printing the top 5 TLCs with the most comments under them. 
# Calculate the total number of children for each top-level comment
top_level_comments_with_children = [(comment, comment.total_children()) for comment in top_level_comments]

# Sort the top-level comments based on the total number of children
sorted_top_level_comments = sorted(top_level_comments_with_children, key=lambda x: x[1], reverse=True)

# Select the top 5 comments with the most children
top_5_comments = sorted_top_level_comments[:5]

# Print the comment structure for each of the top 5 comments
for comment, _ in top_5_comments:
    print("\nTop Level Comment:", comment.id)
    print_comment_structure(comment)

# %%



