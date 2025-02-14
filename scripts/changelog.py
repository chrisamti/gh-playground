#!/usr/bin/env python3

import argparse
import os
import markdown
import re
from bs4 import BeautifulSoup

file_pattern = r'\b\w{2,6}-\d+_\w+\.md\b'
atlassian_jira_base_url = 'https://tamedia.atlassian.net/browse/'

def list_files_in_subfolder(path: str):
    try:
        files = os.listdir(path)
        return [f for f in files if os.path.isfile(os.path.join(path, f))]
    except FileNotFoundError:
        print(f"Error: The directory {path} does not exist.")
        return []

def read_changelog_pr_file(file: str):
    with open(file, 'r') as f:
        return f.read()

def parse_changelog_pr_file_content(content: str, filename: str) -> (dict,bool):
    if not content:
        raise Exception("Empty content")
    if not filename:
        raise Exception("Empty filename")

    valid_section_titles = ['added:', 'changed:', 'fixed:', 'removed:', 'jira:']
    required_section = ['jira:']
    sections = {}

    try:
        # Parse markdown content
        md = markdown.markdown(content).strip("\n")
        # Parse HTML content
        soup = BeautifulSoup(md, 'html.parser')

        # read h1 sections and their li elements, ignoring h1 elements

        for header in soup.find_all(['h1']):
            section_title = header.get_text()
            sections[section_title] = []
            for sibling in header.find_next_siblings():
                if sibling.name == 'h1':
                    break

                # Append all list items to the section
                list_items = sibling.find_all("li")
                # Check if the section has list items
                if not list_items:
                    print(f"Section #{section_title} has no list items in {filename}")
                    return sections, False

                # Append all list items to the section as strings
                sections[section_title].extend([item.get_text() for item in list_items])

        # Check if all required sections are present
        for section in required_section:
            if section not in sections:
                print(f"Section #{section} is missing in {filename}")
                return sections, False

        # Check if all section titles are valid
        for section in sections:
            if section not in valid_section_titles:
                print(f"#{section} is not a valid section title in {filename}")
                return sections, False

        # Check if all JIRA references are valid
        jira_references = sections['jira:']
        for jira_ref in jira_references:
            # get the JIRA references
            if not re.match(r'\b\w{2,6}-\d+\b', jira_ref):
                print(f"{jira_ref} is not a valid JIRA reference in {filename}")
                return sections, False

    except Exception as e:
        print(f"Error: {e}")
        return sections, False

    return sections, True

def check_changelog_pr_files(path) -> bool:
    print("Checking changelog pr files at %s" % path)
    # assume all files are valid
    all_changelog_pr_files_ok = True

    files = list_files_in_subfolder(path)
    matches = [f for f in files if re.match(file_pattern, f)]
    for match in matches:
        file_path = os.path.join(path, match)
        content = read_changelog_pr_file(file_path)
        sections, is_valid = parse_changelog_pr_file_content(content, file_path)
        if is_valid:
            print(f"File {file_path} is valid")
        else:
            print(f"File {file_path} is invalid")
            all_changelog_pr_files_ok = False # nope not all files are valid

    return all_changelog_pr_files_ok

def merge_changelog_pr_files():
    pass

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument('--check', action='store_true', help='Check existence of a valid changelog pr files')
    group.add_argument('--merge', action='store_true', help='Merge changelog pr files in a single Changelog.md file')
    p.add_argument('--path', help='Path to the changelog pr files', required=True)


    args = p.parse_args()
    if args.check:
        ok = check_changelog_pr_files(args.path)
        if not ok:
            exit(-1)
    elif args.merge:
        merge_changelog_pr_files()