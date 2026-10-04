from app.ai.extractor import analyse_enquiry


def main() -> None:
    result = analyse_enquiry(
        course="Java",
        message=(
            "I want to join Java in December. "
            "Please WhatsApp me after 6 PM and send the syllabus."
        ),
    )

    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()