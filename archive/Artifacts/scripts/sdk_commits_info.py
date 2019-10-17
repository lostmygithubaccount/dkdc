
import csv
import os
import subprocess
import json
import collections
import sys

_AZUREML_REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

_PRInfo = collections.namedtuple("PRInfo", "package_name, pr_name, yes_for_rn, release_notes")

DEFAULT_RELEASE_NOTES = "[Replace this section with a message in markdown format to appear in the release notes]"
DEFAULT_RELEASE_NOTES = DEFAULT_RELEASE_NOTES.encode("unicode_escape").decode("utf-8")


def get_all_package_dirs():
    all_package_dirs = list()
    azureml_source_dir = os.path.join(_AZUREML_REPO_DIR, "src")
    for package_name in os.listdir(azureml_source_dir):
        package_path = os.path.join(azureml_source_dir, package_name)
        if os.path.isdir(package_path):
            all_package_dirs.append(package_path)

    return all_package_dirs


def get_all_commits(start_commit, end_commit):
    all_packages = get_all_package_dirs()

    email_dict = dict()
    package_pr_info = dict()
    all_rn_pr_info_dict = dict()
    print("printing all commits between {} and {}:\n".format(start_commit, end_commit))
    print("package_name, commiter_email, pr_name, yes_for_notes, release_notes")
    for package_dir in all_packages:
        release_notes_provided = False
        package_name = os.path.basename(package_dir)
        package_pr_rn_section = "  + **{}**\n".format(package_name)

        git_log_command = ["git", "log", start_commit + ".." + end_commit,
                           "--pretty=format:{%n  \"commit\": \"%H\",%n  \"abbreviated_commit\": \"%h\",%n  "
                           "\"tree\": \"%T\",%n  \"abbreviated_tree\": \"%t\",%n  \"parent\": \"%P\",%n  "
                           "\"abbreviated_parent\": \"%p\",%n  \"refs\": \"%D\",%n  \"encoding\": \"%e\",%n  "
                           "\"sanitized_subject_line\": \"%f\",%n \"commit_notes\": \"%N\",%n  "
                           "\"verification_flag\": \"%G?\",%n  \"signer\": \"%GS\",%n  \"signer_key\": \"%GK\",%n  "
                           "\"author\": {%n    \"name\": \"%aN\",%n    \"email\": \"%aE\",%n    \"date\": "
                           "\"%aD\"%n  },%n  \"commiter\": {%n    \"name\": \"%cN\",%n    \"email\": \"%cE\",%n    "
                           "\"date\": \"%cD\"%n  }%n},",
                           "--", package_dir]

        output = subprocess.check_output(git_log_command).decode("UTF-8")
        # remove last ,
        output = output[0:len(output) - 1]
        # Making it a json array
        output = "[" + output + "]"

        # strict=False for weird decoding.
        all_commits = json.loads(output, strict=False)

        if len(all_commits) == 0:
            continue

        author_pr_dict = dict()
        for commit_json in all_commits:
            commit_id = commit_json["commit"]
            author_email = commit_json["author"]["email"]
            email_dict[author_email] = False
            pr_title = commit_json["sanitized_subject_line"]

            git_show_command = ["git", "show", "--format=%b", "-s", commit_id]

            output = subprocess.check_output(git_show_command).decode("UTF-8")

            yes_for_rn, release_notes = get_release_notes_from_PR_description(output)

            escaped_rn = release_notes.encode("unicode_escape").decode("utf-8")
            escaped_rn = " ".join(escaped_rn.split("\\n"))
            escaped_rn = " ".join(escaped_rn.split())

            pr_info = _PRInfo(package_name, pr_title, yes_for_rn, escaped_rn)

            author_pr_dict[author_email] = [] if author_email not in author_pr_dict else author_pr_dict[author_email]
            author_pr_dict[author_email].append(pr_info)

        for email in author_pr_dict.keys():
            pr_info_list = author_pr_dict[email]
            for pr_info in pr_info_list:
                print("{}, {}, {}, {}, {}".format(package_name, email, pr_info.pr_name,
                                                  pr_info.yes_for_rn, pr_info.release_notes))

                all_rn_pr_info_dict[email] = [] if email not in all_rn_pr_info_dict else all_rn_pr_info_dict[email]
                all_rn_pr_info_dict[email].append(pr_info)

                if pr_info.yes_for_rn:
                    email_dict[email] = True
                    if pr_info.release_notes != DEFAULT_RELEASE_NOTES:
                        release_notes_provided = True
                        temp_release_notes = pr_info.release_notes
                        if temp_release_notes.startswith("+") or temp_release_notes.startswith("-"):
                            temp_release_notes = temp_release_notes[1:]

                        package_pr_rn_section += "    + {}\n".format(temp_release_notes)

        if release_notes_provided:
            package_pr_info[package_name] = package_pr_rn_section

    print("\n\n List of people to email in To List.\n\n")
    email_list = ""
    for email in email_dict.keys():
        email_list = email_list + email + ";"

    print(email_list)

    return package_pr_info, all_rn_pr_info_dict


def get_release_notes_from_PR_description(pr_description):
    found_start_release_notes = False
    yes_for_release_notes = False
    # no_for_release_notes = False
    release_notes = ""
    for line in pr_description.splitlines():
        if "# Release notes" in line:
            found_start_release_notes = True

        if "# Reasons for optional gate failures" in line or "# Optional gates failures" in line:
            break

        without_spaces = "".join(line.split())
        if found_start_release_notes and "[x]Yes" in without_spaces:
            yes_for_release_notes = True

        # if found_start_release_notes and "[x] No" in line:
        #    no_for_release_notes = True

        if yes_for_release_notes:
            if not ("[x]No" in without_spaces or "[]No" in without_spaces or "[x]Yes" in without_spaces):
                release_notes = release_notes + "\n" + line

    return yes_for_release_notes, release_notes


def write_formatted_release_notes(file_basename, start_commit, end_commit):
    package_pr_info, all_rn_pr_info_dict = get_all_commits(start_commit, end_commit)

    markdown_file = file_basename + ".md"
    csv_file = file_basename + ".csv"

    with open(markdown_file, "w") as stream:
        for package_name, release_notes in package_pr_info.items():
            stream.write(release_notes)

    with open(csv_file, "w") as stream:
        fieldnames = ["package_name", "author_email", "pr_name", "yes_for_notes", "release_notes"]
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        for author_email, pr_info_list in all_rn_pr_info_dict.items():
            for pr_info in pr_info_list:
                csv_dict = {}
                csv_dict["package_name"] = pr_info.package_name
                csv_dict["author_email"] = author_email
                csv_dict["pr_name"] = pr_info.pr_name
                csv_dict["yes_for_notes"] = pr_info.yes_for_rn
                csv_dict["release_notes"] = pr_info.release_notes
                writer.writerow(csv_dict)


if __name__ == "__main__":
    """
    Takes two inputs, start_commit and end_commit.
    start_commit doesn't get counted, so it should be the last commit from the last release branch,
    like release/pypi/1.0.41 etc.
    end_commit should be the last commit in releases/current from the release cut you made for the SDK.
    Run chcp 65001 on terminal before running this file to avoid decode error.
    """
    start_commit = sys.argv[1]
    end_commit = sys.argv[2]
    base_filename = sys.argv[3]

    write_formatted_release_notes(base_filename, start_commit, end_commit)
