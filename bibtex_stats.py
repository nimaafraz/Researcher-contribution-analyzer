import bibtexparser
import pandas as pd
import math
import re

# Weights for the contribution metric
W_FIRST = 0.6
W_LAST = 0.4
W_MIDDLE = 1.0

def calculate_average_authors(bibtex_file):
    """Calculates and prints the average number of authors per paper."""
    with open('publications.bib', 'r') as bibfile:
        bib_database = bibtexparser.load(bibfile)
    
    entries = bib_database.entries
    total_authors = 0
    total_papers = len(entries)
    
    if total_papers == 0:
        print("No publications found in the BibTeX file.")
        return []
    
    data = []

    for entry in entries:
        title = entry.get('title', 'N/A')
        authors = entry.get('author', '').split(' and ')
        num_authors = len(authors)
        total_authors += num_authors
        
        # Extract number of citations from the note section
        note = entry.get('note', 'N/A')
        citations = extract_citations(note)
        
        data.append({
            'Title': title,
            'Authors': authors,
            'Number of Authors': num_authors,
            'Citations': citations
        })

    average_authors = total_authors / total_papers
    print(f"\nAverage number of authors per paper: {average_authors:.2f}\n")

    return data

def extract_citations(note):
    """Extracts the number of citations from the note field."""
    if note != 'N/A':
        match = re.search(r'Cited by: (\d+)', note)
        if match:
            return int(match.group(1))
    return 'N/A'

def find_author_position(data, author_last_name):
    """Finds the position of the given author in the author list for each paper."""
    first_author_count = 0
    last_author_count = 0
    middle_author_count = 0

    for paper in data:
        authors = paper['Authors']
        num_authors = len(authors)
        position = -1  # Default to -1 if the author is not found

        # Find the author's position in the list
        for idx, author in enumerate(authors):
            if author_last_name.lower() in author.lower():
                position = idx + 1  # Position is 1-based
                break

        # Add the position to the paper data
        paper['Author Position'] = position

        # Count first, last, and middle author papers
        if position == 1:
            first_author_count += 1
        elif position == num_authors:
            last_author_count += 1
        elif position > 1:
            middle_author_count += 1

    return data, first_author_count, last_author_count, middle_author_count

def calculate_contribution(data, author_last_name):
    """Calculates the contribution score for the target author based on their position."""
    total_contribution = 0.0

    for paper in data:
        authors = paper['Authors']
        num_authors = len(authors)
        position = paper.get('Author Position', -1)

        # Calculate contribution based on position
        if position == 1:
            # First author
            contribution = W_FIRST / math.sqrt(num_authors)
        elif position == num_authors:
            # Last author
            contribution = W_LAST / math.sqrt(num_authors)
        elif position > 1:
            # Middle author
            contribution = W_MIDDLE / num_authors
        else:
            # Not found
            contribution = 0

        # Add the contribution score to the paper data
        paper['Contribution Score'] = contribution
        total_contribution += contribution

    return data, total_contribution

def calculate_weighted_contribution(data):
    """Calculates the weighted contribution score based on citations."""
    weighted_contribution = 0.0

    for paper in data:
        contribution = paper.get('Contribution Score', 0)
        citations = paper.get('Citations', 0)

        if isinstance(citations, int):
            weighted_contribution += contribution * citations

    return weighted_contribution

def print_summary_table(total_papers, average_authors, first_author_count, last_author_count, middle_author_count, total_contribution, average_contribution, weighted_contribution):
    """Prints a summary table with publication metrics."""
    percentage_first = (first_author_count / total_papers) * 100
    percentage_last = (last_author_count / total_papers) * 100
    percentage_middle = (middle_author_count / total_papers) * 100

    summary_data = {
        'Metric': [
            'Average Number of Authors per Paper',
            'Total Number of Papers',
            'Number of First-Author Papers',
            'Number of Last-Author Papers',
            'Number of Middle-Author Papers',
            'Total Contribution Score',
            'Average Contribution Score',
            'Weighted Contribution Score (Contribution × Citations)'
        ],
        'Value': [
            f"{average_authors:.2f}",
            total_papers,
            first_author_count,
            last_author_count,
            middle_author_count,
            f"{total_contribution:.2f}",
            f"{average_contribution:.2f}",
            f"{weighted_contribution:.2f}"
        ]
    }

    df_summary = pd.DataFrame(summary_data)
    print("\nSummary Table:")
    print(df_summary)

def main():
    """Main function to process the BibTeX file and print results."""
    author_last_name = input("Enter the target author's last name: ").strip()

    data = calculate_average_authors('publications.bib')
    if data:
        # Find author position and calculate contribution
        data, first_author_count, last_author_count, middle_author_count = find_author_position(data, author_last_name)
        data, total_contribution = calculate_contribution(data, author_last_name)

        # Calculate average and weighted contribution
        average_contribution = total_contribution / len(data)
        weighted_contribution = calculate_weighted_contribution(data)

        # Convert to DataFrame for better display
        df = pd.DataFrame(data)
        df = df.drop(columns=['Authors'])  # Drop the full author list for a cleaner table
        print("\nTable of Papers with Author Analysis:")
        print(df)

        # Print summary table
        total_papers = len(data)
        average_authors = df['Number of Authors'].mean()
        print_summary_table(total_papers, average_authors, first_author_count, last_author_count, middle_author_count, total_contribution, average_contribution, weighted_contribution)

# Run the main function
if __name__ == "__main__":
    main()
