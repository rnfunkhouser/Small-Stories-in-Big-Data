
import pandas as pd



def process_comments(data):
    """Process the comments data to assign top-level IDs to each comment."""
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

def filter_by_submitter(data):
    """Filters the data to include only those comment trees where at least one 
    of the entries has "is_submitter" set to true."""
    top_level_ids_with_submitter = data[data['is_submitter'] == True]['top_level_id'].unique()
    return data[data['top_level_id'].isin(top_level_ids_with_submitter)]

def filter_by_word_count(data, threshold=20):
    """Filters the data to include only those comment trees where the top-level 
    comment contains at least a specified threshold of words in the "body" field."""
    top_level_comments = data[data['parent_id'].str.startswith("t3")]
    word_counts = top_level_comments['body'].str.split().apply(len)
    top_level_ids_with_threshold_words = top_level_comments[word_counts >= threshold]['id']
    return data[data['top_level_id'].isin(top_level_ids_with_threshold_words)]

def get_ancestors(comment_id, id_to_parent):
    """Retrieve all ancestor comment IDs for a given comment ID."""
    ancestors = []
    current_id = comment_id
    current_parent_id = id_to_parent.get(current_id, None)
    while current_parent_id:
        ancestors.append(current_parent_id)
        current_id = current_parent_id[3:]
        current_parent_id = id_to_parent.get(current_id, None)
    return ancestors

def process_and_consolidate_data(data_path):
    data = pd.read_csv(data_path)
    id_to_parent = dict(zip(data['id'], data['parent_id']))
    data = process_comments(data)
    data = filter_by_submitter(data)
    data = filter_by_word_count(data)
    data['received_delta'] = False
    delta_comments = data[data['body'].str.contains('!delta|Δ', na=False, case=False, regex=True)]
    data.loc[data['id'].isin(delta_comments['parent_id'].str.replace("t1_", "")), 'received_delta'] = True
    id_to_row = data.set_index('id').to_dict(orient='index')
    data['ancestors'] = data['id'].apply(lambda x: get_ancestors(x, id_to_parent))
    consolidated_entries = []
    for index, row in data.iterrows(): #for index, row in data[data['received_delta']].iterrows():
        sc = row['author']
        delta_comment_id = row['id']
        combined_text = [row['body']]
        earliest_date = pd.to_datetime(row['CreatedAt'])
        latest_date = pd.to_datetime(row['CreatedAt'])
        for ancestor_id in row['ancestors']:
            if ancestor_id not in id_to_row:
                continue
            ancestor_comment = id_to_row[ancestor_id]
            if ancestor_comment['author'] == sc:
                combined_text.append(ancestor_comment['body'])
                parent_date = pd.to_datetime(ancestor_comment['CreatedAt'])
                if parent_date < earliest_date:
                    earliest_date = parent_date
                if parent_date > latest_date:
                    latest_date = parent_date
        consolidated_text = "\n\n---\n\n".join(reversed(combined_text))
        consolidated_entries.append({
            'id': delta_comment_id,
            'author': sc,
            'combined_text': consolidated_text,
            'earliest_date': earliest_date,
            'latest_date': latest_date,
            'received_delta': row['received_delta']
        })
    consolidated_data = pd.DataFrame(consolidated_entries)
    return consolidated_data

# Explicit call to process_and_consolidate_data
if __name__ == "__main__":
    data_path = '/Users/ryanfunkhouser/Documents/Research/Active Projects/Small Stories in Big Data/Data/CMV_July_2022.csv'  # Replace with the path to your CSV file
    result = process_and_consolidate_data(data_path)
    #print(result.head())  # Display the first few rows of the result for verification
    result.to_csv('test_result.csv', index=False)