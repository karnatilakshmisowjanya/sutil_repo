#!/usr/local/py-utils/venvs/virtualenv/bin/python
import os
import sys
import difflib
import subprocess

orig_deps_file = './../session/requirements.txt'
new_deps_file = './requirements.txt'

'''
read package dependencies listed in requirements.txt files
'''
def read_dependencies():
    orig_deps = ""
    new_deps = ""
    if os.path.exists(orig_deps_file)and os.path.exists(new_deps_file):
        orig_deps = open(orig_deps_file, 'r')
        new_deps = open(new_deps_file, 'r')
    else:
        raise Exception("A requirements.txt file was not found")
    return orig_deps, new_deps

'''
report the diff between two requirements.txt files
'''
def report_changes(orig_deps, new_deps):
    change_report = difflib.ndiff(orig_deps.readlines(), new_deps.readlines())
    return change_report

'''
sync changes by detecting changes in requirements.txt to pip un-/install
'''
def sync_changes(change_report):
    changes_detected = False
    for change in change_report:
        if change.startswith('- '):
            dependency = change[2:].replace('\n','')
            auto_uninstall = "-y"
            print("Detected requirements.txt change for [{dep}] \n".format(dep=dependency))
            sys.stdout.flush()
            try:
                # Note: Uninstall will not remove site-packages/dist-info directories or resultant dangling dependencies
                subprocess.check_call(["pip", "uninstall", auto_uninstall, dependency])
            except subprocess.CalledProcessError as ex:
                 raise Exception("command '{}' return with error (code {}): {}".format(ex.cmd, ex.returncode, ex.output))
            changes_detected = True
        if change.startswith('+ '):
            dependency = change[2:].replace('\n','')
            print("Detected requirements.txt change for [{dep}] \n".format(dep=dependency))
            sys.stdout.flush()
            os.system("pip --no-cache-dir install {dep}".format(dep=dependency))
            changes_detected = True
    return changes_detected

'''
replace session requirements with newest dependencies
'''
def replace_session_deps(changes_detected):
    if not changes_detected:
        print("No changes detected \n")
        sys.stdout.flush()
        return
    
    if os.path.exists(orig_deps_file) and os.path.exists(new_deps_file):
        os.remove(orig_deps_file )
        print("Updating session with latest requirements.txt \n")
        sys.stdout.flush()
        with open(new_deps_file) as new_deps:
            with open(orig_deps_file, "w") as orig_deps:
                for line in new_deps:
                    orig_deps.write(line)
    else:
        raise Exception("A requirements.txt file was not found \n")

def main():
    try:
        print("main module: syncing requirements.txt deps for devcontainer session in [os:{os}]...\n".format(os=sys.platform))
        sys.stdout.flush()
        orig_deps, new_deps = read_dependencies()
        change_report = report_changes(orig_deps, new_deps)
        changes_detected = sync_changes(change_report)
        replace_session_deps(changes_detected)
    except Exception as ex:
        print(str(ex))

if __name__ == '__main__':
    sys.exit(main())
