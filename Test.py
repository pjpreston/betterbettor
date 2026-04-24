import racing_api as rapi

class Test:
    def __init__(self, name: str):
        self.name = name
   


def main():
    regions = rapi.get_course_regions()
    item= regions[0]
    print(item)
    num_lines = len(regions)
    print("get_course_regions # lines = ", num_lines)



if __name__ == "__main__":
    main()