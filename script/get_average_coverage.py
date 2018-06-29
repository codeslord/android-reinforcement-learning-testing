import os
import argparse
import xml.etree.ElementTree as ET
import json

DIR="/Users/vuong/final_results/"

if __name__=="__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("tool", help="Tool name. Ex: monkey, dynodroid")

    # args = parser.parse_args()
    # tool = args.tool
    tool = ["monkey", "dyno", "mytool", "a3e", "puma"]
    app = ["any", "bat", "exp", "munch", "stuff", "tip", "note"]

    for t in tool:
        print("---------TOOL: {}-------".format(t))
        for a in app:
            print("---------APP: {}-------".format(a))
            if os.path.isdir(DIR + t + "/" + a):
                total_lines = []
                all = []
                emma = []
                coverage = []
                for f in os.listdir(DIR + t + "/" + a):
                    if ".xml" in f:
                        tree = ET.parse(DIR + t + "/" + a + "/" + f)
                        root = tree.getroot()
                        data = root.find('data')
                        all_xml = data.find('all')
                        for child in all_xml.findall("coverage"):
                            if child.attrib['type'] == "line, %":
                                all += [child.attrib["value"]]
                        for child in all_xml.findall("package"):
                            if "EmmaInstrument" in child.attrib["name"]:
                                for c in child.findall("coverage"):
                                    if c.attrib['type'] == "line, %":
                                        emma += [c.attrib["value"]]
                for i in range(len(all)):
                    all_ratio = all[i].split("  ")[-1].strip()[1:-1]
                    all_line = float(all_ratio.split("/")[1])
                    all_executed = float(all_ratio.split("/")[0])
                    emma_ratio = emma[i].split("  ")[-1].strip()[1:-1]
                    emma_line = float(emma_ratio.split("/")[1])
                    emma_executed = float(emma_ratio.split("/")[0])
                    total_lines += [all_line - emma_line]
                    coverage += [(all_executed - emma_executed)/float(all_line - emma_line)]
                print(all)
                print(emma)
                print(total_lines)
                print(coverage)
                if len(total_lines) >0 and len(coverage) >0:
                    print(reduce(lambda x, y: x + y, total_lines) / float(len(total_lines)))
                    print(reduce(lambda x, y: x + y, coverage) / float(len(coverage)))




