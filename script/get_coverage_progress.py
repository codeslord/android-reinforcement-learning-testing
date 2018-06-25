import os
import argparse
import xml.etree.ElementTree as ET
import json

DIR="/Users/vuong/resultsvm1/"

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("tool", help="Tool name. Ex: monkey, dynodroid")

    args = parser.parse_args()
    tool = args.tool
    progress = {}

    for dir in os.listdir(DIR+tool+"/"):
        progress[dir] = []
        for i in range(12):
            step = []
            coverage_name = "coverage" + str(i) if i != 0 else "coverage"
            coverage_folder = DIR+tool+"/"+dir+"/" + coverage_name
            if os.path.isdir(coverage_folder):
                tree = ET.parse(coverage_folder+'/coverage.xml')
                root = tree.getroot()
                data = root.find('data')
                all = data.find('all')
                for child in all.findall("coverage"):
                    print(child.attrib)
                    step.append(child.attrib)
                progress[dir].append(step)

    with open(tool+".json", "w") as f:
        json.dump(progress, f, indent=True)


