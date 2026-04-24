import racing_api as rapi


class RacingDataExtractor:

    def extract_courses(self) -> dict:
        regions = rapi.get_course_regions()
        courses = rapi.get_courses()
        return {"regions": regions, "courses": courses}

    def extract_todays_racing(self) -> dict:
        racecards = rapi.get_racecards()
        results = rapi.get_results()
        return {"racecards": racecards, "results": results}

    def extract_all(self) -> dict:
        return {
            **self.extract_courses(),
            **self.extract_todays_racing(),
        }


def main():
    extractor = RacingDataExtractor()
    extractor.extract_all()


if __name__ == "__main__":
    main()
